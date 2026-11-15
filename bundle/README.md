# HEZQEN Infrastructure Lab Bundle (IK-05)

The bundle is an aggregate distribution of independently versioned IK-01 through IK-04 releases. It does not duplicate their source code.

A bundle release must:
- reference immutable product artifact URLs and exact product versions;
- include each artifact's SHA-256 checksum, SBOM, provenance reference, and source commit;
- declare a tested compatibility matrix;
- verify every downloaded artifact before installation;
- fail closed if a required artifact is missing, its checksum fails, or its version is outside the declared matrix;
- preserve each product's license and third-party notices.

The bundle installer/orchestration implementation is planned. This README records the architectural contract only; it is not a functioning installer.
