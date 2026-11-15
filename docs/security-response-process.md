# Security Response Process

1. **Receive:** Accept reports privately; discourage public exploit details.
2. **Triage:** Confirm affected asset, prerequisites, impact, exploitability, and scope.
3. **Contain:** Revoke exposed credentials, disable unsafe workflows, or publish mitigations as appropriate.
4. **Fix:** Implement the smallest safe correction and add regression coverage.
5. **Verify:** Re-run relevant tests and review the patch for adjacent weaknesses.
6. **Release:** Publish an advisory and fixed version when users need to act.
7. **Learn:** Record root cause and update standards or automation to prevent recurrence.

Security exceptions must be explicit, owned, compensating-controlled, and time-bounded. A public repository issue is not an appropriate channel for unpatched exploit details.
