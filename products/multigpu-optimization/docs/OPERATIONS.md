# IK-03 Operations

1. Collect model metadata from the exact checkpoint/config and verify context length and attention architecture.
2. Inventory GPU model, VRAM, count per node, interconnect, node count, driver, CUDA runtime, and vLLM release.
3. Run the planner with intended precision, context length, concurrency, and topology.
4. Review warnings and generated command. Confirm the model's quantization method and KV-cache dtype are supported by the installed vLLM release.
5. Start a controlled benchmark; record peak memory, prompt/generation throughput, latency percentiles, and concurrency.
6. Compare actual measurements with estimates and adjust reserves/profile assumptions based on evidence.

Do not deploy a production fleet solely from an estimated-fit result. Re-run sizing after changing model, quantization, vLLM version, context length, concurrency, GPU type, or topology.
