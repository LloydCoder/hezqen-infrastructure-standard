# HIES Release Process

## Change readiness

1. Confirm the change has an issue or documented rationale.
2. Review normative wording and backward compatibility.
3. Validate schemas and examples.
4. Run the complete test suite.
5. Review security and licensing impact.
6. Update CHANGELOG.md.

## Stable release requirements

A stable HIES release must be tagged from a reviewed commit. Release notes identify the standard version, included policies/schemas/workflows, migration impact, and known limitations.

Product repositories must pin the HIES release or commit they adopt. They must vendor the needed files into their own source/release so their build and installation do not depend on HIES availability.

Do not publish a stable release while mandatory validation fails or while material security requirements are ambiguous.
