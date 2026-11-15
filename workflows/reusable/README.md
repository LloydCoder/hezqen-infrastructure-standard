# Reusable workflow policy

Reusable workflows must be introduced only after a product-specific review of permissions, trust boundaries, artifact handling, and runner isolation.

A reusable workflow reference must be pinned to an immutable commit. Caller workflows should pass only the minimum required inputs. Never pass secrets to jobs that build or execute untrusted pull-request content. Keep release signing and publication in a separate job with narrowly scoped permissions and protected environments.

The current templates are copy-and-adapt examples, not production-ready reusable workflows. Placeholder steps intentionally fail so an unconfigured release or security pipeline cannot appear green.
