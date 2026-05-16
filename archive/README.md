# Archive

This directory preserves historical prototypes that are no longer part of the active runtime.

- `api_app_legacy/` contains the previous oversized backend catalog from `services/api-gateway/app`.
- `api_gateway_legacy/` contains dormant API support code that still referenced the removed `src.backend` tree.
- `mobile_flutter_legacy/` contains the duplicate Flutter scaffold that used to sit beside the React Native mobile workstream.
- `packages_config_legacy/` contains the old deployment/config bundle for the removed backend layout.
- `tests_integration_legacy/` contains tests that targeted the removed backend layout.
- `docs_legacy/` contains documentation tied to the removed backend layout.
- `tools_legacy/` contains the older automation and deployment scripts that targeted the removed `src/backend` layout.
- Archived code is reference material only. New work should be rebuilt inside the canonical service homes listed in `docs/architecture/PRE_PUBLIC_WORKSTREAMS.md`.
