# IK-01 GPU Guidance

## NVIDIA

The optional `compose.nvidia.yaml` override requests all NVIDIA GPUs for the Ollama container. The host must have a supported NVIDIA driver and NVIDIA Container Toolkit configured for Docker. Verify host visibility with `nvidia-smi` and then verify container visibility with the vendor-supported runtime diagnostics.

```bash
docker compose -f compose.yaml -f compose.nvidia.yaml config --quiet
docker compose -f compose.yaml -f compose.nvidia.yaml up -d
docker compose -f compose.yaml -f compose.nvidia.yaml logs ollama
```

GPU reservation syntax and runtime behavior depend on Docker Compose, Engine, driver, and toolkit versions. This repository's static CI validates the Compose contract only; it does not prove that a physical GPU is available or selected.

## Sizing

Do not size a deployment from parameter count alone. Estimate model-weight memory from the selected quantization, then add KV cache (which grows with context length and concurrent sequences), runtime overhead, and safety headroom. Benchmark the exact model, quantization, context, concurrency, and hardware. Record measured tokens/s, time-to-first-token, peak VRAM/RAM, and thermal/power conditions before making performance claims.

## CPU fallback

The base Compose file runs without GPU reservations. CPU inference may be substantially slower and is dependent on model size, quantization, memory bandwidth, and available RAM.
