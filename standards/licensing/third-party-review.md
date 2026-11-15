# Third-Party Dependency Review

Before adding a dependency, record its purpose, version, source, maintainer health, license, transitive dependencies, security posture, update cadence, and replacement options.

Review:
- license compatibility with the product's distribution and commercial model;
- copyleft, attribution, notice, patent, and source-disclosure obligations;
- known vulnerabilities and maintenance status;
- install-time and runtime network behavior;
- whether the dependency collects or transmits data;
- whether it is optional or required.

A dependency with unresolved license or redistribution questions MUST NOT be bundled into a stable commercial artifact.
