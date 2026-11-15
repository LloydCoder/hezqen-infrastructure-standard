# IK-03 Compatibility

- Python runtime: 3.12.
- Runtime dependencies: Python standard library only.
- Declared platforms: Linux amd64 and arm64; the CLI itself is architecture-independent.
- Output target: vLLM CLI argument layout; verify flags against the exact installed vLLM version.
- No CUDA, NVIDIA driver, GPU, container runtime, cloud account, or network access is required for planning.

GPU execution and performance are not validated by this CPU-only workspace.
