# GNOME // EVIDENCE REACTOR — Threat Model
- **Untrusted Imports**: Imported observation JSON and Evidence Capsules are parsed strictly via `JSON.parse` (zero `eval`, zero HTML injection).
- **Tampering Detection**: Every capsule file carries a SHA-256 checksum in `integrity/checksums.json`. Modified prompts or observations fail replay verification.
- **Credential Safety**: Path B (optional local Ollama endpoint) is opt-in only, never auto-probes localhost, and never embeds API keys in browser code.
- **Provenance Honesty**: Checksums prove internal capsule integrity since export, not independent third-party authorship.
