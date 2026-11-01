# Agent instructions

## Project

This Home Assistant integration controls TESmart LAN KVM switches: it reports and changes the active input and exposes supported switch settings and raw protocol commands.

## Working in this repository

- Read `README.md` before changing protocol framing or command behavior.
- Preserve the documented optimistic state for write-only settings and keep arbitrary raw commands explicit in the service API.
- Before changing CI, check [pschmitt/ci-workflows](https://github.com/pschmitt/ci-workflows) for reusable components and preserve this repository's existing checks.

## Validation

- Run `uvx ruff check .` and `uvx ruff format --check .` for Python changes.
- CI runs Hassfest and the shared Ruff checks; it currently has no test job.
