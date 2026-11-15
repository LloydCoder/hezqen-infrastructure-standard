# IK-03 Threat Model

## Assets
- Model architecture and hardware inventory inputs.
- Generated sizing and serving configurations.
- Integrity of the planner and its package dependencies.

## Trust boundaries
- Operator-supplied model metadata and hardware inventory.
- Planner output to operator deployment automation.
- Package build/install environment.

## Threats and controls

| Threat | Control | Residual risk |
|---|---|---|
| Incorrect capacity estimate leads to OOM | Explicit formula, configurable reserves, warnings, conservative assumptions | Runtime behavior differs by architecture, kernels, fragmentation, and workload |
| Malicious model identifier or output injection | Model identifier is passed as one argument; shell command is quoted with shlex | Operators must not eval untrusted output or interpolate it unsafely |
| Invalid topology produces misleading config | Validate TP/PP against node/GPU counts | Not all topology/performance effects are represented |
| Sensitive infrastructure metadata leaks | Tool is local and does not transmit inputs | Operators may share generated JSON or logs |
| Dependency compromise | Runtime has no third-party dependencies | Build backend and Python runtime still require supply-chain controls |

## Security assumptions
- The tool runs locally and does not connect to cloud APIs or GPU management endpoints.
- The operator validates model metadata and actual hardware inventory.
- Generated shell commands are reviewed before execution.
- No credentials, API keys, or model weights are collected or stored.
- A memory-fit estimate is not a guarantee of successful model startup or performance.
