# SOMA Codex

**Architecture codex for a governed local-first agent runtime.**

SOMA is a systems-design project, not a finished runtime. It defines the theory,
invariants, crate map, governance model, and implementation contracts for a future
Rust-based agent organism.

The core idea: an agent system should behave less like a platform hosting unrelated
agents and more like one governed body. Participants coordinate through one shared
workspace, authority is leased, completion is verified rather than self-claimed, and
high-risk actions remain under HumanSeat authority.

---

## Status

This repository is a portfolio architecture/spec project.

Working artifacts today:

1. Engineering manual with implementation requirements
2. Seven-book SOMA Codex source in HTML
3. Rendered ODT books
4. Source utility for regenerating ODT books from source HTML
5. Diagrams and visual system maps

Not implemented yet:

- Rust runtime workspace
- Append-only hash-chained workspace log
- Holon onboarding runtime
- Governance and lease enforcement
- HumanSeat approval surface
- Verifier organ
- Memory/world/cognition crates

This distinction is intentional. SOMA is included here to show architecture and systems
thinking; Mosaic and Tendril are the working prototype repos.

---

## What SOMA Demonstrates

- Governance-first multi-agent architecture
- Append-only workspace/event-log design
- Verification-gated completion instead of self-reported success
- Human authority ceiling for destructive or high-risk actions
- Holon/organism model for coordinated agent systems
- Rust crate planning and implementation contracts
- Invariants, state machines, threat boundaries, and test obligations
- Careful distinction between functional terms and consciousness claims

Additional project notes: [docs/project-notes.md](docs/project-notes.md)

---

## Repository Map

```text
soma-codex/
├── README.md
├── docs/
│   └── engineering-manual.md
├── artifacts/
│   └── odt/                 # rendered SOMA Codex books
└── src/
    ├── book0-overview.html
    ├── book1-theory.html
    ├── book2-anatomy.html
    ├── book3-physiology.html
    ├── book4-engineering.html
    ├── book5-runtime.html
    ├── appendices.html
    ├── build.py
    ├── style.css
    └── img/
```

---

## Main Artifact

Start with the engineering manual:

[`docs/engineering-manual.md`](docs/engineering-manual.md)

It consolidates the codex into build requirements: invariants, crate boundaries,
workspace contracts, governance rules, runtime lifecycle, and test obligations.

---

## Rendered Books

Rendered ODT files are included in:

```text
artifacts/odt/
```

Book map:

| Book | Focus |
|---|---|
| 0 - Overview | Orientation, reading map, operational definitions |
| 1 - Theory | Why organism-style agent architecture |
| 2 - Anatomy | Holarchy, membrane, systems, organs |
| 3 - Physiology | Runtime theorems and algorithms |
| 4 - Engineering | Crates, invariants, contracts, threat model |
| 5 - Runtime | Lifecycle, development, recovery, trajectory |
| 6 - Appendices | Theorem catalog, glossary, cross-reference, lineage |

---

## Rebuild The ODT Artifacts

The repository includes the rendered ODT books. The source utility can regenerate them
in environments where LibreOffice HTML-to-ODT conversion is available:

```bash
python3 src/build.py book0-overview.html
python3 src/build.py book1-theory.html
python3 src/build.py book2-anatomy.html
python3 src/build.py book3-physiology.html
python3 src/build.py book4-engineering.html
python3 src/build.py book5-runtime.html
python3 src/build.py appendices.html
```

The generated files are written to `artifacts/odt/`.

---

## Relationship To The Portfolio

SOMA is the high-level systems architecture piece.

It pairs with:

- [Mosaic](https://github.com/primitive-0rigins/mosaic): working AI memory/retrieval prototype
- [Tendril](https://github.com/primitive-0rigins/tendril): working Rust mesh/discovery prototype

Together, the three projects show concept design, runnable prototypes, local-first
infrastructure, and disciplined scope boundaries.

---

## Built By

[Primitive Origin LLC](https://github.com/primitive-0rigins)
