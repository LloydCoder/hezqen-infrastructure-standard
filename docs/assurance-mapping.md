# Assurance Framework Mapping

## Purpose and limits

This document maps HIES engineering controls to relevant public assurance frameworks. It is a navigation aid for product teams, not a certification, audit opinion, legal interpretation, or claim that a product conforms to every control. Each product must scope controls to its actual architecture, deployment profile, data, and customer obligations.

## NIST Secure Software Development Framework

Use NIST SP 800-218 SSDF 1.1 as the published baseline. Track the Rev. 1 draft separately; do not treat a draft as a final standard.

| SSDF practice area | HIES implementation references | Product evidence expected |
|---|---|---|
| Prepare the Organization (PO) | CONTRIBUTING.md, SECURITY.md, repository-hardening.md, engineering-handbook.md | Named owners, secure development policy, protected repository settings, support lifecycle |
| Protect the Software (PS) | secrets-management.md, release-integrity.md, redistribution-policy.md | Access controls, secrets handling, dependency inventory, signed/verified release assets |
| Produce Well-Secured Software (PW) | product-boundaries.md, ai-threat-model.md, secure-container-baseline.md, testing-standard.md | Threat model, secure design, code/config tests, integration and security evidence |
| Respond to Vulnerabilities (RV) | vulnerability-management.md, security-response-process.md, incident-response.md | Triage record, affected-version analysis, remediation, customer communication |

## OWASP Application Security Verification Standard

Apply OWASP ASVS 5.0.0 to any web/API control plane, management interface, or customer-facing service. Select the verification level from the product's risk and exposure; do not assume one level fits every kit.

Relevant HIES anchors include authentication and authorization requirements in product-specific security design, input and output validation, secure configuration, data protection, logging, error handling, and dependency management. Each product must produce a control-to-test mapping for the features it actually implements.

## OWASP Top 10 for LLM Applications 2025 and OWASP AI Exchange

For AI/RAG-enabled products, assess risks across the model and data lifecycle, including prompt injection, sensitive information disclosure, data/model poisoning, insecure output handling, excessive agency, vector/embedding weaknesses, supply-chain exposure, and resource exhaustion.

HIES anchors:
- standards/security/ai-threat-model.md
- standards/security/logging-and-data-minimization.md
- standards/security/network-boundaries.md
- standards/quality/testing-standard.md

Product teams must document model, retrieval, connector, tool, and operator trust boundaries. Model output must not grant permissions or independently authorize tool execution.

## Container and host security

Use Docker Engine security guidance and rootless mode where supported. Apply the HIES secure-container baseline and document exceptions for GPU devices, host networking, kernel modules, or other host privileges. A rootless profile is not a substitute for host patching, network isolation, or least-privilege configuration.

## Software supply-chain assurance

| Practice | HIES requirement | Evidence |
|---|---|---|
| SBOM | CycloneDX JSON for every stable release | SBOM file, generator/version, release manifest |
| Artifact integrity | SHA-256 checksums and verification | artifact-manifest.json, verifier output |
| Signing | Signed artifacts or verifiable signing statement | Signature and independent verification record |
| Provenance | Identify source revision and workflow identity | Platform provenance/attestation |
| Reproducibility | Document build inputs and reproducible steps where feasible | Build instructions and comparison evidence |

SLSA Build L2 is an initial target only where the platform's provenance and isolation properties have been verified. Do not claim a SLSA level from the presence of a provenance file alone. Use Sigstore/Cosign or an equivalent reviewed signing approach and verify signatures independently.

## Privacy and regulated data

GDPR Article 25 and HIPAA Security Rule safeguards are relevant only when the product's processing context and customer role bring them into scope. Product teams must identify controller/processor or covered-entity/business-associate responsibilities with qualified counsel and the customer. HIES data minimization and security controls support engineering practice but do not establish legal compliance.

## Review cadence

Revisit this mapping when:
- a referenced framework publishes a new final version;
- a product adds a web/API control plane, model, connector, tool, or external data flow;
- a new deployment profile changes trust boundaries or privilege requirements;
- a security incident reveals a missing control;
- a customer contract introduces additional assurance requirements.
