# AI and RAG Threat-Model Standard

AI-enabled products MUST maintain a threat model covering the full data and control flow, including models, prompts, retrieved content, tools, plugins, vector stores, connectors, logs, and operator interfaces.

Assess at minimum, where applicable:
- prompt injection from user input and retrieved documents;
- insecure output handling and downstream code/command execution;
- training or retrieval data poisoning;
- sensitive information disclosure through prompts, logs, embeddings, or model output;
- excessive agency and unauthorized tool execution;
- insecure plugin, connector, and model supply chains;
- denial of service and resource exhaustion;
- model and dependency vulnerabilities;
- trust-boundary confusion between instructions and untrusted retrieved content.

For each threat, record assets, actor, preconditions, attack path, impact, mitigations, residual risk, and verification evidence. Model output MUST NOT independently grant authorization or bypass application policy. Tool permissions and execution authority must be enforced outside the model.
