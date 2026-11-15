"""Transparent model-memory and vLLM parallelism estimates."""
from __future__ import annotations

import math
import shlex
from dataclasses import asdict, dataclass

GIB = 1024**3
WEIGHT_BYTES = {"fp32": 4.0, "fp16": 2.0, "bf16": 2.0, "fp8": 1.0, "int8": 1.0, "int4": 0.5}
KV_BYTES = {"fp16": 2.0, "bf16": 2.0, "fp8": 1.0, "fp8_e5m2": 1.0}


class PlanningError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ModelProfile:
    name: str
    parameters_billion: float
    layers: int
    kv_heads: int
    head_dim: int
    max_context_length: int


@dataclass(frozen=True, slots=True)
class HardwareProfile:
    gpus_per_node: int
    nodes: int
    vram_gib_per_gpu: float
    tensor_parallel_size: int
    pipeline_parallel_size: int
    max_model_len: int
    max_num_seqs: int
    weight_dtype: str = "bf16"
    quantization: str | None = None
    kv_cache_dtype: str = "fp16"
    gpu_memory_utilization: float = 0.90
    system_reserve_gib: float = 2.0
    activation_reserve_gib: float = 1.0
    quantization_overhead_pct: float = 5.0


@dataclass(frozen=True, slots=True)
class Plan:
    model: dict[str, object]
    topology: dict[str, object]
    memory: dict[str, object]
    vllm: dict[str, object]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def command(self) -> list[str]:
        return list(self.vllm["command"])  # type: ignore[arg-type]

    def shell_command(self) -> str:
        return shlex.join(self.command())


def estimate(model: ModelProfile, hw: HardwareProfile) -> Plan:
    positive = {
        "parameters_billion": model.parameters_billion, "layers": model.layers,
        "kv_heads": model.kv_heads, "head_dim": model.head_dim,
        "max_context_length": model.max_context_length, "gpus_per_node": hw.gpus_per_node,
        "nodes": hw.nodes, "vram_gib_per_gpu": hw.vram_gib_per_gpu,
        "tensor_parallel_size": hw.tensor_parallel_size, "pipeline_parallel_size": hw.pipeline_parallel_size,
        "max_model_len": hw.max_model_len, "max_num_seqs": hw.max_num_seqs,
    }
    if not model.name.strip():
        raise PlanningError("model name must not be empty")
    for name, value in positive.items():
        if not math.isfinite(float(value)) or value <= 0:
            raise PlanningError(f"{name} must be greater than zero")
    if hw.weight_dtype not in WEIGHT_BYTES:
        raise PlanningError(f"unsupported weight dtype: {hw.weight_dtype}")
    if hw.weight_dtype in {"int4", "int8"} and not hw.quantization:
        raise PlanningError("int4/int8 weights require an explicit vLLM quantization method")
    if hw.quantization is not None and not hw.quantization.strip():
        raise PlanningError("quantization method must not be empty")
    if hw.kv_cache_dtype not in KV_BYTES:
        raise PlanningError(f"unsupported KV cache dtype: {hw.kv_cache_dtype}")
    if not 0.1 <= hw.gpu_memory_utilization <= 0.99:
        raise PlanningError("gpu_memory_utilization must be between 0.10 and 0.99")
    numeric_options = (hw.quantization_overhead_pct, hw.system_reserve_gib, hw.activation_reserve_gib, hw.gpu_memory_utilization)
    if not all(math.isfinite(value) for value in numeric_options):
        raise PlanningError("overhead, reserve, and utilization values must be finite")
    if hw.quantization_overhead_pct < 0 or hw.system_reserve_gib < 0 or hw.activation_reserve_gib < 0:
        raise PlanningError("overhead and reserve values cannot be negative")
    if hw.max_model_len > model.max_context_length:
        raise PlanningError("max_model_len exceeds the model's declared context limit")
    tp, pp = hw.tensor_parallel_size, hw.pipeline_parallel_size
    total_gpus = hw.gpus_per_node * hw.nodes
    used_gpus = tp * pp
    if tp > hw.gpus_per_node:
        raise PlanningError("tensor_parallel_size must not exceed GPUs per node; use pipeline parallelism across nodes")
    if pp > hw.nodes:
        raise PlanningError("pipeline_parallel_size must not exceed node count")
    if used_gpus > total_gpus:
        raise PlanningError("requested parallelism exceeds available GPUs")

    weight_bytes = model.parameters_billion * 1_000_000_000 * WEIGHT_BYTES[hw.weight_dtype]
    weight_bytes *= 1 + hw.quantization_overhead_pct / 100
    weight_gib = weight_bytes / used_gpus / GIB
    layers_per_stage = math.ceil(model.layers / pp)
    kv_heads_per_rank = max(1, math.ceil(model.kv_heads / tp))
    kv_bytes = 2 * layers_per_stage * kv_heads_per_rank * model.head_dim * KV_BYTES[hw.kv_cache_dtype] * hw.max_model_len * hw.max_num_seqs
    kv_gib = kv_bytes / GIB
    reserve = hw.system_reserve_gib + hw.activation_reserve_gib
    estimate_gib = weight_gib + kv_gib + reserve
    budget = hw.vram_gib_per_gpu * hw.gpu_memory_utilization
    headroom = budget - estimate_gib
    fits = headroom >= 0
    warnings = [
        "Planning estimate only; validate exact checkpoint, vLLM release, quantization kernels, topology, and workload.",
        "KV sharding/replication and layer placement vary by model architecture; this uses a simplified conservative layout.",
        "CUDA graphs, fragmentation, adapters, speculative decoding, multimodal encoders, and runtime workspaces are not modeled.",
    ]
    if hw.weight_dtype in {"int4", "int8", "fp8"}:
        warnings.append("Quantized weights include the configured metadata overhead; actual formats may require materially different memory.")
    if not fits:
        warnings.append("Estimated per-GPU memory exceeds the configured utilization budget.")
    dtype = {"fp32":"float32","fp16":"half","bf16":"bfloat16","fp8":"auto","int8":"auto","int4":"auto"}[hw.weight_dtype]
    kv_dtype = {"fp16":"float16","bf16":"bfloat16","fp8":"fp8","fp8_e5m2":"fp8_e5m2"}[hw.kv_cache_dtype]
    command = ["vllm","serve",model.name,"--tensor-parallel-size",str(tp),"--pipeline-parallel-size",str(pp),"--max-model-len",str(hw.max_model_len),"--max-num-seqs",str(hw.max_num_seqs),"--gpu-memory-utilization",f"{hw.gpu_memory_utilization:.2f}","--dtype",dtype,"--kv-cache-dtype",kv_dtype]
    if hw.quantization:
        command.extend(["--quantization", hw.quantization])
    if hw.nodes > 1:
        command.extend(["--distributed-executor-backend", "ray"])
    return Plan(
        model={"name":model.name,"parameters_billion":model.parameters_billion,"layers":model.layers,"kv_heads":model.kv_heads,"head_dim":model.head_dim,"max_context_length":model.max_context_length},
        topology={"nodes":hw.nodes,"gpus_per_node":hw.gpus_per_node,"total_gpus_available":total_gpus,"tensor_parallel_size":tp,"pipeline_parallel_size":pp,"gpus_requested":used_gpus},
        memory={"vram_gib_per_gpu":hw.vram_gib_per_gpu,"gpu_memory_utilization":hw.gpu_memory_utilization,"budget_gib_per_gpu":round(budget,3),"weights_gib_per_gpu":round(weight_gib,3),"kv_cache_gib_per_gpu":round(kv_gib,3),"system_and_activation_reserve_gib":round(reserve,3),"estimated_total_gib_per_gpu":round(estimate_gib,3),"headroom_gib_per_gpu":round(headroom,3),"estimated_fit":fits},
        vllm={"weight_dtype":hw.weight_dtype,"quantization":hw.quantization,"kv_cache_dtype":hw.kv_cache_dtype,"command":command,"shell_command":shlex.join(command)},
        warnings=tuple(warnings),
    )
