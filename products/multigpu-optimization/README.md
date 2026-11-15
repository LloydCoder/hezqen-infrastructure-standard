# HEZQEN Multi-GPU Optimization Kit (IK-03)

A CPU-only planning toolkit for estimating model weight/KV-cache memory and generating vLLM tensor-parallel and pipeline-parallel launch configurations. It accepts model architecture, precision, context, concurrency, GPU memory, and node topology as explicit inputs. It does not query GPUs or require CUDA to produce a plan.

> **Status: engineering preview.** Memory figures are simplified planning estimates, not guarantees that a model will load or meet a throughput target. Benchmark the exact model, quantization implementation, vLLM version, drivers, GPU topology, and workload before committing infrastructure.

## Install

```bash
cd products/multigpu-optimization
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Example: 70B quantized model on four 24 GiB GPUs

```bash
hezqen-gpu-plan \
  --model org/example-70b \
  --params-b 70 --layers 80 --kv-heads 8 --head-dim 128 \
  --model-context 32768 --context 8192 --concurrency 8 \
  --gpus-per-node 4 --nodes 1 --vram-gib 24 \
  --tp 4 --pp 1 --weight-dtype int4 --kv-dtype fp16 \
  --output plan.json
```

JSON output includes per-GPU weight and KV-cache estimates, reserves, headroom, topology, warnings, and a generated vLLM command. Add `--fail-if-no-fit` to return exit code 3 when the simplified estimate exceeds the configured budget.

## Estimation model

- Weight memory: parameter count × bytes per parameter × quantization metadata overhead, divided by TP × PP ranks.
- KV cache: 2 × layers per pipeline stage × KV heads per tensor rank × head dimension × KV element bytes × max context × max concurrent sequences.
- Runtime budget: per-GPU VRAM × vLLM memory-utilization target.
- Estimated requirement: weights + KV cache + explicit system and activation reserves.

The KV calculation uses a simplified sharding/replication model. Actual allocation depends on model architecture, GQA/MQA layout, vLLM implementation, cache block size, quantization kernels, and runtime workspaces.

## Topology guidance

- Prefer tensor parallelism within a node where high-bandwidth GPU interconnect is available.
- Use pipeline parallelism across nodes when scaling beyond one node; inter-node communication and model partitioning affect throughput.
- The planner rejects TP larger than GPUs per node and PP larger than node count. This is a conservative default topology, not every topology vLLM can support.
- Heterogeneous GPU fleets, MIG, NVLink/NVSwitch topology, PCIe placement, and NUMA effects require operator validation.

The generated command targets the vLLM OpenAI-compatible serving interface. Review the output against the exact installed vLLM release's CLI. The planner does not install vLLM, download weights, or start a GPU workload.

## Verification

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m hezqen_gpu_planner --help
```

See [methodology](docs/METHODOLOGY.md), [operations](docs/OPERATIONS.md), and [THREAT_MODEL.md](THREAT_MODEL.md).
