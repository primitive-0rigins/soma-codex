# SOMA Codex Project Notes

## Portfolio Role

SOMA Codex demonstrates high-level AI systems architecture. It is a specification and design
codex for a governed local-first agent runtime, not a finished implementation.

## What Exists

- Engineering manual with normative implementation requirements
- Seven-book codex source in HTML
- Rendered ODT artifacts
- Diagrams and system maps
- Source utility for regenerating ODT books where LibreOffice conversion is available

## Key Design Choices

- **Governance as runtime physics:** authority, leases, verification, and HumanSeat are core
  runtime concepts rather than review-layer additions.
- **Append-only workspace:** coordination is represented through a replayable shared event log.
- **Verified completion:** holon self-reports are evidence, not proof of completion.
- **Operational language:** terms like self, valence, and cognition are used functionally, not
  as claims of subjective experience.

## Roadmap Boundary

SOMA does not currently include the Rust runtime workspace, append-only log implementation,
holon onboarding runtime, governance engine, verifier organ, or HumanSeat interface.

## How To Evaluate It

Start with:

```text
docs/engineering-manual.md
```

Then review the rendered books in:

```text
artifacts/odt/
```
