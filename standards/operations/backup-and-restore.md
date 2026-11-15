# Backup and Restore Standard

Each stateful product MUST document:
- what constitutes durable state and where it is stored;
- backup scope, frequency guidance, retention, encryption, and access controls;
- a consistent backup procedure for databases, indexes, configuration, and required metadata;
- restore prerequisites and an operator-confirmed restore procedure;
- integrity verification and a post-restore health check;
- recovery limitations, including state that cannot be reconstructed.

Restore tests MUST use isolated test data and MUST NOT overwrite production data. Documentation must distinguish backup creation from a verified successful restore.
