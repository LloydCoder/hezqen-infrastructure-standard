# Secure Container Baseline

This baseline applies to containerized product profiles unless a documented platform constraint requires an exception.

## Mandatory controls

- Services MUST run as non-root where supported.
- Containers MUST NOT use `privileged: true` by default.
- Linux capabilities MUST be dropped by default; add only capabilities proven necessary.
- Read-only root filesystems SHOULD be used where compatible.
- Production profiles MUST define appropriate CPU, memory, and process limits.
- Port bindings MUST be explicit. Inference and vector-database services MUST bind to loopback or a private interface by default, never public interfaces by default.
- Application containers MUST NOT mount the Docker socket.
- Containers MUST NOT mount the host root filesystem or broad home directories.
- Images MUST use explicit versions; stable releases MUST record immutable image digests.
- Health checks and readiness conditions MUST represent actual service readiness.
- Writable volumes, ownership, persistence, and retention MUST be documented.
- Host networking and device access MUST be opt-in and justified.

## Installation safety

Installers MUST NOT pipe remote content directly into a shell. Downloaded scripts must be inspectable and checksum-verifiable. Destructive uninstall operations MUST require explicit confirmation and distinguish configuration removal from data deletion.

## Exceptions

An exception must identify the affected component, privilege, business or hardware need, threat introduced, compensating control, owner, approval, and expiry date. Exceptions are not silently inherited by other products.
