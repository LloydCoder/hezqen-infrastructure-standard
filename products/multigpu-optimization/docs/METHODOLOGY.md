# IK-03 Memory Estimation Methodology

## Inputs
The model profile requires parameter count, layer count, KV-head count, head dimension, and declared context limit. The hardware profile requires GPUs per node, node count, VRAM per GPU, TP/PP sizes, max model length, concurrency, weight precision, and KV-cache precision.

## Weight estimate
`parameters × bytes_per_parameter × (1 + quantization_metadata_overhead) ÷ (tensor_parallel_size × pipeline_parallel_size)`

The estimator assumes balanced partitioning. It does not inspect the checkpoint or determine tied embeddings, uneven layer placement, quantization scales/zero-points, mixed precision, or model-specific sharding behavior.

## KV-cache estimate
`2 × ceil(layers ÷ PP) × max(1, ceil(KV_heads ÷ TP)) × head_dim × KV_bytes × max_model_len × max_num_seqs`

This approximates key and value tensors for each active token. It assumes simplified KV-head sharding/replication and does not model block allocation, prefix caching, sliding-window attention, MLA, multimodal state, or engine-specific layouts.

## Budget
`VRAM_per_GPU × gpu_memory_utilization`

The planner subtracts estimated weight and KV-cache allocations plus explicit system and activation reserves. It reports headroom and fit status.

## Interpretation
- Positive headroom is not a startup guarantee.
- Negative headroom means the simplified estimate exceeds the budget.
- Benchmark the exact model and serving settings; record peak VRAM and throughput.
- Update methodology and regression fixtures when vLLM changes materially alter memory allocation.
