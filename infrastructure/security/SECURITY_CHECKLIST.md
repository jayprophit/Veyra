# Security Checklist

## Repository Hygiene

- Do not commit `.env` files.
- Keep only placeholder `.env.example` files.
- Ignore private keys, certificates, local databases, logs, and build outputs.
- Run secret scanning before pushing public branches.
- Rotate any credential that was ever committed or pasted into a public channel.

## Local Auth Baseline

- Use local development credentials only for private testing.
- Replace demo auth before any shared deployment.
- Add password hashing, refresh-token storage, session revocation, and audit logs before public use.

## API Protection Roadmap

- Rate limiting
- RBAC
- MFA
- Request audit logs
- Human approval for broker execution, infrastructure mutation, and destructive data actions

## Infrastructure Roadmap

- Environment-separated secrets
- Least-privilege cloud credentials
- Backups and restore tests
- Dependency scanning
- Container image scanning
