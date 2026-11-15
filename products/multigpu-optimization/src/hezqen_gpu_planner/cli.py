from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .planner import HardwareProfile, ModelProfile, PlanningError, estimate


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Estimate model memory and generate a vLLM parallelism command.")
    p.add_argument("--model", required=True)
    p.add_argument("--params-b", type=float, required=True)
    p.add_argument("--layers", type=int, required=True)
    p.add_argument("--kv-heads", type=int, required=True)
    p.add_argument("--head-dim", type=int, required=True)
    p.add_argument("--model-context", type=int, required=True)
    p.add_argument("--context", type=int, required=True)
    p.add_argument("--concurrency", type=int, default=1)
    p.add_argument("--gpus-per-node", type=int, required=True)
    p.add_argument("--nodes", type=int, default=1)
    p.add_argument("--vram-gib", type=float, required=True)
    p.add_argument("--tp", type=int, required=True)
    p.add_argument("--pp", type=int, default=1)
    p.add_argument("--weight-dtype", choices=tuple(WEIGHT_BYTES), default="bf16")
    p.add_argument("--kv-dtype", choices=tuple(KV_BYTES), default="fp16")
    p.add_argument("--gpu-memory-utilization", type=float, default=0.90)
    p.add_argument("--system-reserve-gib", type=float, default=2.0)
    p.add_argument("--activation-reserve-gib", type=float, default=1.0)
    p.add_argument("--quantization-overhead-pct", type=float, default=5.0)
    p.add_argument("--fail-if-no-fit", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    try:
        model = ModelProfile(args.model,args.params_b,args.layers,args.kv_heads,args.head_dim,args.model_context)
        hw = HardwareProfile(args.gpus_per_node,args.nodes,args.vram_gib,args.tp,args.pp,args.context,args.concurrency,args.weight_dtype,args.kv_dtype,args.gpu_memory_utilization,args.system_reserve_gib,args.activation_reserve_gib,args.quantization_overhead_pct)
        plan = estimate(model,hw)
    except PlanningError as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 2
    output = json.dumps(plan.to_dict(),indent=2)+"\n"
    if args.output:
        args.output.write_text(output,encoding="utf-8")
    print(output,end="")
    return 3 if args.fail_if_no_fit and not plan.memory["estimated_fit"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
