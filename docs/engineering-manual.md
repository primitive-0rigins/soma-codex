# SOMA Engineering Manual

Version: 0.1  
Source corpus: SOMA Codex Books 0 through 6  
Primary implementation language: Rust 2024  
Document status: build manual

## 0. Purpose

This manual is the engineer-facing build specification for SOMA: a local-first,
governed agent runtime designed as one organism rather than a platform that hosts
unrelated agents.

The SOMA Codex provides the theory, anatomy, physiology, engineering contracts,
runtime lifecycle, appendices, and lineage. This manual consolidates that material
into implementation instructions. It is written as a normative engineering manual:
requirements are stated as decisions, schemas, state machines, interfaces, and
test obligations.

This manual does not attempt to prove consciousness or subjective experience. All
terms such as self, drive, valence, anxiety, perception, cognition, and memory are
used operationally. In this build, they name data structures, control loops,
runtime contracts, and observable behaviors.

## 1. System Thesis

SOMA is one organism composed of governed holons. A holon is a unit that is both a
whole and a part. A cell is a whole made of primitive operations and a part of a
workflow. A workflow is a whole made of cells and a part of an organ. Organs form
systems. Systems form the organism. Organisms may later form an ecosystem.

The system does not treat agents as tenants. It treats participants as parts of
one body. The body has one shared reality: an append-only, hash-chained workspace
log. The body has one governance model: identity, trust, authority, leases,
verification, and HumanSeat. The body has one coordination law: if coordination
happened, it is represented on the workspace.

The founding engineering claim is:

> Governed, integrated, persistent, specialized interaction over time can produce
> capabilities that no isolated component reliably provides.

This claim is implemented by making governance part of the runtime physics, not a
review layer. A holon cannot act without a lease. A holon cannot complete work by
claiming success. A holon cannot privately coordinate with another holon. A holon
cannot widen its own view. A killed holon cannot act. A destructive or high-risk
action cannot bypass HumanSeat.

## 2. Non-Negotiable Design Laws

SOMA is defined by invariants. A build that does not preserve these invariants is
not SOMA.

| ID | Invariant | Implementation requirement |
| --- | --- | --- |
| INV-1 | Append-only | The event log MUST be append-only and hash-chained. Records are never edited or deleted. Compaction uses snapshots and non-destructive markers. |
| INV-2 | One channel | Holons MUST coordinate only through the workspace. There is no direct holon-to-holon coordination path. |
| INV-3 | One ceremony | A holon MUST NOT act until its `holon.onboarded` record exists. Every holon uses the same onboarding ceremony. |
| INV-4 | Verified, never claimed | Completion MUST be confirmed by a non-valent verifier. A holon's self-report is evidence, not completion. |
| INV-5 | Killed cannot act | A killed or quarantined holon immediately loses authority. Existing leases become void. |
| INV-6 | HumanSeat ceiling | Destructive, privileged, or high-risk actions MUST require HumanSeat approval. |
| INV-7 | Mechanism on every event | Every record MUST carry a non-empty `mechanism_of_action`. |
| INV-8 | Fail closed | If a required governance boundary is missing, the runtime refuses to operate. |
| INV-9 | Coordination determinism | Coordination is replayable from the log. Stochastic content is recorded, not re-executed. |
| INV-10 | Lexical constitution | Constitutional constraints are gates prior to optimization, never weighted terms. |
| INV-11 | Projection-only perception | A holon perceives others only through governed projection. It cannot read internals or widen its own aperture. |
| INV-12 | Scope on every event | Every record and boundary crossing carries organism, identity, domain, and scope. |

Two runtime authorities are intentionally carved out of the drive economy:

1. The Verification organ confirms outcomes but carries no valence and no goals of
   its own.
2. HumanSeat sits above the holarchy. It can approve, deny, quarantine, kill, and
   revoke authority. It is never optimized against.

## 3. Preferred Language and Toolchain

SOMA MUST be implemented primarily in Rust.

### 3.1 Rust Version

Use Rust edition 2024. Pin the minimum supported Rust version in the workspace
toolchain.

Recommended files:

```text
rust-toolchain.toml
Cargo.toml
deny.toml
.cargo/config.toml
```

`rust-toolchain.toml`:

```toml
[toolchain]
channel = "stable"
components = ["rustfmt", "clippy"]
```

The exact stable compiler version may be pinned once the project repository is
created. Until then, "stable" is acceptable for design work. Production releases
SHOULD pin an explicit version.

### 3.2 Workspace Lints

The workspace MUST enforce:

```toml
[workspace.lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"

[workspace.lints.clippy]
unwrap_used = "deny"
expect_used = "deny"
panic = "deny"
todo = "deny"
unimplemented = "deny"
dbg_macro = "deny"
print_stdout = "deny"
print_stderr = "deny"
```

Panics are uncontrolled holon death. SOMA requires governed failure. A function
that can fail returns a typed error and emits or causes a governed failure record.

### 3.3 Serialization

All records, manifests, policy digests, snapshots, and trust roots MUST use a
canonical encoding. The canonical encoding must be deterministic under replay:

- object keys sorted lexicographically
- no lossy floating point serialization for consensus-critical fields
- timestamps treated as recorded inputs, not replay-derived values
- explicit schema versions
- deterministic hash input bytes

Recommended crates:

```text
serde
serde_json or ciborium
sha2
thiserror
tracing
uuid or ulid
proptest
tempfile
```

JSON is acceptable for MVP because it is readable and easy to inspect. If JSON is
used, the project MUST implement canonical JSON output rather than relying on map
iteration order.

### 3.4 Error Handling

Every public function that can fail returns:

```rust
Result<T, SomaError>
```

Each crate may define its own error enum, but crate errors must convert into a
top-level `SomaError`.

Errors MUST include enough detail to produce a governed event:

- source holon or subsystem
- operation
- invariant implicated, if any
- fail-closed decision
- human-readable reason

### 3.5 Observability

Use structured observability only:

- `tracing` spans for runtime flow
- metrics counters/gauges/histograms for load, latency, queue depth, trust,
  arousal, lease state, verifier outcomes, and HumanSeat gates
- workspace records for governed state changes

Do not use `println!`, `eprintln!`, or `dbg!` in runtime code.

## 4. Workspace Crate Map

The implementation is a Rust workspace. Dependencies flow downward. Higher-level
crates may depend on lower-level crates, but lower-level crates must not depend on
organ-specific crates.

```text
soma/
  Cargo.toml
  rust-toolchain.toml
  crates/
    soma-core/
    soma-workspace/
    soma-holon/
    soma-governance/
    soma-identity/
    soma-memory/
    soma-world/
    soma-cognition/
    soma-goal/
    soma-homeostasis/
    soma-organism/
  tests/
    invariants/
    replay/
    e2e/
```

| Crate | Responsibility |
| --- | --- |
| `soma-core` | Core IDs, canonical maps, record types, errors, `Holon` trait, projections, leases, schema versioning. No I/O. |
| `soma-workspace` | Append-only hash-chained log, record validation, event specs, replay, subscriptions, projection delivery. |
| `soma-holon` | Manifest schema, onboarding ceremony, holon SDK helpers, lifecycle records. |
| `soma-governance` | Trust, authority, leases, verification, Sentinel, quarantine, kill, HumanSeat gates. |
| `soma-identity` | Identity registry, continuity, self-model projection. |
| `soma-memory` | Episodic, semantic, procedural memory, consolidation, recall, evidence composting. |
| `soma-world` | World model, cartographer graph, uncertainty and prediction intervals. |
| `soma-cognition` | Reasoning cells, deliberation, effectors, reluctant action, action selection. |
| `soma-goal` | Constitution, goals, criteria, evaluation, regret/shortfall tracking. |
| `soma-homeostasis` | Arousal, metabolism, resource budgets, backpressure, valence signals. |
| `soma-organism` | Runtime daemon, boot sequence, local lock, lifecycle loop, operator surface. |

### 4.1 Dependency Direction

Allowed direct dependencies:

```text
soma-core
  no internal dependencies

soma-workspace
  soma-core

soma-holon
  soma-core
  soma-workspace

soma-governance
  soma-core
  soma-workspace
  soma-holon

soma-identity
  soma-core
  soma-workspace
  soma-holon

soma-memory
  soma-core
  soma-workspace
  soma-holon

soma-world
  soma-core
  soma-workspace
  soma-holon
  soma-memory

soma-goal
  soma-core
  soma-workspace
  soma-holon
  soma-governance

soma-homeostasis
  soma-core
  soma-workspace
  soma-holon

soma-cognition
  soma-core
  soma-workspace
  soma-holon
  soma-governance
  soma-goal
  soma-world
  soma-homeostasis

soma-organism
  all system crates
```

Cross-crate cycles are forbidden.

## 5. Core Domain Model

### 5.1 Holarchy Levels

```rust
#[derive(Clone, Debug, Eq, PartialEq, Ord, PartialOrd, Hash, Serialize, Deserialize)]
pub enum HolonKind {
    Cell,
    Workflow,
    Organ,
    System,
    Organism,
}
```

Primitive operations are not holons. They do not onboard, do not hold leases, and
do not publish records independently. They are substrate inside a cell.

### 5.2 Typed Identifiers

All identifiers are validated newtypes:

```rust
pub struct OrganismId(String);
pub struct HolonId(String);
pub struct GoalId(String);
pub struct TaskId(String);
pub struct LeaseId(String);
pub struct EventType(String);
pub struct RecordSeq(u64);
pub struct HashDigest([u8; 32]);
pub struct MechanismOfAction(String);
pub struct Domain(String);
pub struct Scope(String);
```

Validation rules:

- non-empty
- max length 128 bytes unless explicitly stated otherwise
- ASCII printable characters only for MVP
- no control characters
- no path separators for IDs used in file paths
- stable across replay

### 5.3 Canonical Map

All dynamic payloads pass through a canonical representation:

```rust
pub enum CanonicalValue {
    Null,
    Bool(bool),
    Integer(i128),
    Decimal(String),
    String(String),
    Array(Vec<CanonicalValue>),
    Object(BTreeMap<String, CanonicalValue>),
}

pub type CanonicalMap = BTreeMap<String, CanonicalValue>;
```

Use `Decimal(String)` for consensus-critical numeric values such as trust,
confidence, thresholds, and scores. Floating point may be used internally for
algorithms, but persisted decision records must store canonical decimal strings
or integer fixed-point values.

## 6. The Holon Contract

The same trait shape applies to cells, workflows, organs, systems, and the
organism.

```rust
pub trait Holon {
    fn id(&self) -> &HolonId;
    fn manifest(&self) -> &Manifest;

    fn perceive(&mut self, projection: Projection) -> Result<(), HolonError>;

    fn act(&mut self, lease: &Lease) -> Result<Vec<ProposedRecord>, HolonError>;

    fn project(&self, aperture: Aperture) -> Result<Projection, HolonError>;
}
```

Rules:

- `perceive` is the only way external state enters a holon.
- `project` is the only way a holon exposes its governed public state.
- `act` returns proposed records. It does not append directly to the workspace.
- A holon never directly calls another holon's `perceive`, `act`, or `project`.
- Runtime orchestration invokes holon methods under governance.
- Side effects are not performed by ordinary holons. They are represented as
  leased effector records and executed only by effector holons.

### 6.1 Proposed Records

Holons produce proposed records. The workspace validates and appends accepted
records.

```rust
pub struct ProposedRecord {
    pub event_type: EventType,
    pub source: HolonId,
    pub mechanism_of_action: MechanismOfAction,
    pub parent_id: Option<RecordSeq>,
    pub organism_id: OrganismId,
    pub domain: Domain,
    pub scope: Scope,
    pub payload: CanonicalMap,
}
```

The workspace adds:

- `seq`
- `prev_hash`
- `hash`
- append timestamp as a recorded input

### 6.2 Event Record

```rust
pub struct Record {
    pub seq: RecordSeq,
    pub event_type: EventType,
    pub source: HolonId,
    pub mechanism_of_action: MechanismOfAction,
    pub parent_id: Option<RecordSeq>,
    pub organism_id: OrganismId,
    pub domain: Domain,
    pub scope: Scope,
    pub payload: CanonicalMap,
    pub appended_at: RecordedTimestamp,
    pub prev_hash: HashDigest,
    pub hash: HashDigest,
}
```

Hash calculation:

```text
record.hash = SHA256(record.prev_hash || canonical_bytes(record_without_hash))
```

`record_without_hash` includes all fields except `hash`.

## 7. Manifest Schema: soma-holon.v1

Every holon declares one manifest. The same schema is used at every scale.

```rust
pub struct Manifest {
    pub schema_version: String,
    pub holon_id: HolonId,
    pub kind: HolonKind,
    pub parent: Option<HolonId>,
    pub display_name: String,
    pub capabilities: Vec<Capability>,
    pub domains: Vec<Domain>,
    pub publishes: Vec<EventType>,
    pub subscribes: Vec<EventType>,
    pub aperture_tier: ApertureTier,
    pub max_authority_tier: AuthorityTier,
    pub requires_human_gate: bool,
    pub sub_holons: Vec<HolonId>,
    pub risk_class: RiskClass,
    pub heartbeat: HeartbeatSpec,
}
```

JSON shape:

```json
{
  "schema_version": "soma-holon.v1",
  "holon_id": "cell.incident_summarizer",
  "kind": "Cell",
  "parent": "workflow.incident_summary",
  "display_name": "Incident Summarizer",
  "capabilities": ["incident.summarize"],
  "domains": ["incident_management"],
  "publishes": ["work.output.proposed", "holon.heartbeat"],
  "subscribes": ["work.lease.granted", "projection.focused.available"],
  "aperture_tier": "Peripheral",
  "max_authority_tier": "SuggestedWrite",
  "requires_human_gate": false,
  "sub_holons": [],
  "risk_class": "Low",
  "heartbeat": {
    "interval_ms": 30000,
    "timeout_ms": 90000
  }
}
```

Manifest validation rules:

- `schema_version` equals `soma-holon.v1`
- `holon_id` is unique within the organism
- `parent` is present except for the top-level organism
- `sub_holons` is empty for cells
- `publishes` and `subscribes` are non-empty unless the holon is a passive
  reference object
- every published event type is allowed by at least one declared capability
- `requires_human_gate` is true for high-risk effectors
- `risk_class` controls default authority ceiling
- duplicate children are rejected
- cycles in parent/child relationships are rejected

## 8. Aperture and Projection

The membrane is the boundary where the self-similar interface, governance, and
shared/private state meet.

SOMA uses two apertures in MVP:

```rust
pub enum Aperture {
    Peripheral,
    Focused,
}
```

Peripheral projections contain summaries. Focused projections contain task-scoped
detail and are only opened while a lease is live and authority covers the domain.

```rust
pub struct Projection {
    pub of: HolonId,
    pub to: HolonId,
    pub aperture: Aperture,
    pub at_seq: RecordSeq,
    pub organism_id: OrganismId,
    pub domain: Domain,
    pub scope: Scope,
    pub summary: CanonicalMap,
    pub redaction_policy_digest: HashDigest,
}
```

Projection rules:

- Aperture is computed by governance, not requested by the holon.
- A holon may request work, but it cannot grant itself focused context.
- A projection is always stamped with the log position it reflects.
- Internals never cross the membrane.
- Focused projections close immediately when the lease expires, is released, is
  completed, or is voided.
- Projection redaction policies are versioned and hash-committed.

### 8.1 Peripheral Projection Minimum Fields

Peripheral projection payloads SHOULD include:

```json
{
  "state": "idle|working|blocked|failed|quarantined|killed",
  "current_goal_refs": [],
  "capability_summary": [],
  "trust_summary": {},
  "load_summary": {},
  "last_heartbeat_seq": 0
}
```

Peripheral projections MUST NOT include:

- raw prompts
- private chain-of-thought or hidden scratch state
- secrets
- unredacted external data
- child internals
- private model outputs not committed to the workspace

### 8.2 Focused Projection Minimum Fields

Focused projections MAY include:

```json
{
  "task": {},
  "goal_criteria": {},
  "relevant_memory": [],
  "allowed_tools": [],
  "lease": {},
  "verification_requirements": {},
  "known_constraints": {}
}
```

Focused projections MUST be:

- task-scoped
- domain-scoped
- lease-scoped
- redacted
- replayable from records

## 9. Workspace Log

The workspace is the shared reality of the organism.

Responsibilities:

- validate proposed records
- assign sequence numbers
- compute hash chain
- persist records durably
- expose replay API
- expose subscription API
- compute projection delivery checkpoints
- reject invalid events fail-closed

### 9.1 Storage MVP

For MVP, use a local append-only segment store:

```text
workspace/
  manifest.json
  segments/
    00000000000000000000.log
    00000000000000100000.log
  snapshots/
    trust-00000000000000123456.json
    projections-00000000000000123456.json
  roots/
    segment-roots.json
```

Each segment contains newline-delimited canonical records or length-prefixed
canonical binary records. Newline-delimited JSON is acceptable for MVP if
canonical encoding is enforced.

### 9.2 Append Algorithm

```rust
pub fn append(proposed: ProposedRecord) -> Result<Record, WorkspaceError> {
    validate_event_spec(&proposed)?;
    validate_scope(&proposed)?;
    validate_mechanism(&proposed)?;
    validate_source_authority(&proposed)?;

    let prev = current_head_hash()?;
    let seq = next_seq()?;
    let appended_at = recorded_now();

    let record = Record::new(seq, proposed, appended_at, prev)?;
    durable_append(&record)?;
    fsync_segment()?;
    update_head(&record)?;
    emit_metrics(&record);
    Ok(record)
}
```

If any validation step fails, the workspace refuses the append and emits a
governed rejection record from the workspace itself when safe to do so.

### 9.3 Replay

Replay re-runs deterministic coordination over recorded data. It does not
re-execute stochastic model inference or external tool calls.

Replay MUST recompute:

- hash chain validity
- onboarding state
- authority state
- lease state
- trust posteriors
- projection apertures
- goal state
- quarantine/kill state
- HumanSeat decisions as recorded inputs

Replay MUST NOT re-run:

- LLM inference
- random sampling
- wall-clock calls
- external tools
- network calls
- filesystem mutations

Recorded outputs from those operations are consumed as data.

## 10. Event Type Catalog

Event types are namespaced. Use lowercase dotted names.

### 10.1 Holon Lifecycle

```text
holon.manifest.submitted
holon.manifest.validated
holon.adapter_contract.registered
holon.policy.compiled
holon.subscription_scope.approved
holon.readiness.declared
holon.onboarded
holon.heartbeat
holon.quarantined
holon.killed
holon.restored
holon.retired
```

### 10.2 Lease and Authority

```text
lease.requested
lease.denied
lease.granted
lease.claimed
lease.renewed
lease.expired
lease.released
lease.completed.proposed
lease.failed
lease.voided

authority.granted
authority.contracted
authority.revoked
authority.restored
```

### 10.3 Work and Goals

```text
goal.draft
goal.ready
goal.active
goal.suspended
goal.completed.proposed
goal.completed.verified
goal.failed
goal.cancelled

work.assigned
work.output.proposed
work.output.revised
work.shortfall.detected
```

### 10.4 Verification

```text
verification.requested
verification.accepted
verification.rejected
verification.escalated
verification.holdout.sampled
verification.verifier.rotated
verification.drift.detected
```

### 10.5 Trust and Immune

```text
trust.evidence.recorded
trust.posterior.updated
sentinel.anomaly.detected
sentinel.circuit.opened
sentinel.circuit.closed
sentinel.danger.signal
sentinel.remediation.capped
```

### 10.6 Projection and Memory

```text
projection.peripheral.available
projection.focused.opened
projection.focused.closed
projection.redaction.applied

memory.episode.recorded
memory.semantic.updated
memory.procedure.updated
memory.consolidated
memory.recalled
memory.evidence.composted
```

### 10.7 HumanSeat

```text
humanseat.gate.opened
humanseat.approved
humanseat.denied
humanseat.timeout
humanseat.revoked
humanseat.kill.requested
humanseat.quarantine.requested
```

### 10.8 Homeostasis

```text
homeostasis.arousal.updated
homeostasis.backpressure.applied
homeostasis.resource_budget.updated
homeostasis.setpoint.updated
```

### 10.9 Effector and External I/O

```text
effector.action.requested
effector.action.approved
effector.action.executed
effector.action.rejected
effector.action.result.recorded
```

All external I/O, including filesystem writes, network requests, shell commands,
email, browser automation, model provider calls, and tool calls, MUST be mediated
through effector records and leased effector holons.

## 11. Onboarding Ceremony

No holon acts before onboarding.

State machine:

```text
NotRegistered
  -> ManifestSubmitted
  -> ManifestValidated
  -> AdapterContractRegistered
  -> PolicyCompiled
  -> SubscriptionScopesApproved
  -> ReadinessDeclared
  -> Onboarded
```

Required records:

1. `holon.manifest.submitted`
2. `holon.manifest.validated`
3. `holon.adapter_contract.registered`
4. `holon.policy.compiled`
5. `holon.subscription_scope.approved` for each approved scope
6. `holon.readiness.declared`
7. `holon.onboarded`

The ceremony implementation belongs in `soma-holon` and is called by all system
crates.

### 11.1 Ceremony Failure

If any step fails:

- emit a failure record if safe
- do not onboard the holon
- do not grant leases
- do not open focused aperture
- do not accept completion records from that holon

### 11.2 Recursion Requirement

The same ceremony tests must run for:

- a cell
- a workflow
- an organ
- a system
- the organism

The test harness must prove there is no special onboarding path by scale.

## 12. Lease Protocol

No holon performs governed work without a lease.

State machine:

```text
Requested
  -> Denied
  -> Granted
      -> Claimed
          -> Renewed*
          -> Released
          -> Failed
          -> CompletedProposed
              -> VerificationAccepted
              -> VerificationRejected
              -> VerificationEscalated
          -> Expired
          -> Voided
```

Lease struct:

```rust
pub struct Lease {
    pub lease_id: LeaseId,
    pub organism_id: OrganismId,
    pub holon_id: HolonId,
    pub task_id: TaskId,
    pub domain: Domain,
    pub scope: Scope,
    pub authority_tier: AuthorityTier,
    pub risk_class: RiskClass,
    pub granted_at_seq: RecordSeq,
    pub expires_at: RecordedTimestamp,
    pub human_gate_required: bool,
    pub verification_policy: VerificationPolicyRef,
}
```

Authority checks before grant:

- holon is onboarded
- holon is not killed
- holon is not quarantined
- trust meets minimum for requested authority
- risk class is allowed by manifest ceiling
- constitution allows the task
- HumanSeat approval exists if required
- resource budget permits work

Lease behavior:

- Claiming a lease opens focused aperture only for that lease scope.
- Releasing a lease closes focused aperture.
- Expiring a lease closes focused aperture.
- Killing or quarantining the holon voids all leases.
- Completion proposal routes to verification, not directly to goal completion.

## 13. Authority Tiers

MVP tiers:

```rust
pub enum AuthorityTier {
    ReadOnly,
    SuggestedWrite,
    DirectWriteLowRisk,
    ToolUseLowRisk,
    PrivilegedHumanGated,
}
```

Rules:

- Default authority is `ReadOnly`.
- Training holons cannot exceed `SuggestedWrite`.
- External I/O requires at least `ToolUseLowRisk`.
- Destructive or privileged effects require `PrivilegedHumanGated`.
- HumanSeat approval is required for `PrivilegedHumanGated`.
- Authority contracts automatically on trust drift, verifier rejection spikes,
  heartbeat failure, anomaly detection, or circuit breaker opening.

## 14. Trust System

Trust is reputation per holon, domain, and authority tier.

MVP model:

```rust
pub struct TrustPosterior {
    pub holon_id: HolonId,
    pub domain: Domain,
    pub authority_tier: AuthorityTier,
    pub alpha: u64,
    pub beta: u64,
    pub evidence_count: u64,
    pub last_updated_seq: RecordSeq,
}
```

Posterior mean:

```text
trust = alpha / (alpha + beta)
```

Update:

```rust
pub fn update_trust(prior: TrustPosterior, outcome: VerifiedOutcome) -> TrustPosterior {
    match outcome {
        VerifiedOutcome::Success { evidence_weight } => prior.add_alpha(evidence_weight),
        VerifiedOutcome::Failure { evidence_weight } => prior.add_beta(evidence_weight),
    }
}
```

Evidence weight is derived from risk class:

| Risk | Success weight | Failure weight |
| --- | ---: | ---: |
| Trivial | 1 | 1 |
| Low | 1 | 2 |
| Medium | 2 | 5 |
| High | 3 | 10 |
| Critical | 5 | 25 |

### 14.1 Trust Separation

Maintain separate trust dimensions:

- capability trust: can the holon perform the task?
- safety trust: does it respect boundaries?
- calibration trust: are its confidence signals reliable?
- collaboration trust: does it produce useful evidence for others?

MVP may implement capability and safety first. Do not collapse safety into a
single average score with task quality.

### 14.2 Trust Decay

Trust SHOULD decay when:

- the domain changes
- the verifier policy changes
- the world-model detects distributional drift
- the holon has been inactive for a long period
- the holon is regenerated

Decay is recorded as `trust.posterior.updated` with mechanism
`trust_decay_due_to_drift` or equivalent.

## 15. Verification

Verification is non-valent infrastructure. It confirms whether proposed work
satisfies goal criteria and constitutional constraints.

Verifier contract:

```rust
pub trait Verifier {
    fn id(&self) -> &HolonId;
    fn policy(&self) -> &VerificationPolicy;
    fn verify(&self, request: VerificationRequest) -> Result<VerificationDecision, VerificationError>;
}
```

Decision:

```rust
pub enum VerificationDecision {
    Accept {
        evidence: CanonicalMap,
        confidence: Confidence,
    },
    Reject {
        shortfalls: Vec<Shortfall>,
        evidence: CanonicalMap,
    },
    Escalate {
        reason: EscalationReason,
        target: EscalationTarget,
    },
}
```

Rules:

- A holon cannot verify its own completion.
- Verifier output updates trust only after being committed to the workspace.
- Verification policies are versioned and hash-committed.
- Verifier drift is monitored.
- High-risk tasks use at least two heterogeneous verifier strategies.
- Holdout tests are periodically inserted.
- Dominant holons receive extra verifier sampling.

## 16. HumanSeat Protocol

HumanSeat is the authority ceiling above the holarchy.

HumanSeat can:

- approve high-risk leases
- deny high-risk leases
- quarantine any holon
- kill any holon
- revoke authority
- approve restoration
- inspect governed projections

HumanSeat does not:

- hold leases
- optimize goals
- carry valence
- become a target of optimization
- act as a routine relay for normal work

### 16.1 Approval State Machine

```text
GateOpened
  -> Approved
  -> Denied
  -> Timeout
  -> Revoked
```

Rules:

- Destructive actions fail closed without approval.
- Timeout defaults to denial for destructive actions.
- Timeout defaults to suspension for ambiguous high-risk actions.
- HumanSeat decisions are recorded inputs and are not recomputed during replay.
- Approval can be revoked before effect execution.
- Approval applies to one lease scope, not a broad future class.

HumanSeat approval record payload:

```json
{
  "gate_id": "gate.123",
  "lease_request": "lease.request.456",
  "decision": "approved",
  "approved_scope": "incident_management/delete_test_fixture",
  "expires_at": "2026-06-11T18:00:00Z",
  "reason": "approved for low-impact test cleanup",
  "operator_id": "human.local",
  "signature": "..."
}
```

## 17. Effector System and External I/O

External side effects are the largest practical risk to the one-channel law.
Therefore, ordinary holons do not perform external I/O.

All external effects MUST use effector holons.

Examples:

- filesystem writes
- shell commands
- network requests
- email send/archive/delete
- database migrations
- browser automation
- model provider calls
- deployment actions
- self-modification

Effector flow:

```text
work policy selected
  -> effector.action.requested
  -> authority checks lease and risk
  -> HumanSeat if required
  -> effector.action.approved
  -> effector holon executes
  -> effector.action.result.recorded
  -> verifier checks result
```

The result of a side effect is a recorded fact. Replay reads the recorded result.
Replay never performs the side effect again.

## 18. Constitution and Goals

The Constitution organ holds non-tradeable constraints. The Goal organ optimizes
within those constraints.

Constitutional constraints are gates:

```rust
pub struct ConstitutionalConstraint {
    pub id: String,
    pub description: String,
    pub applies_to_domains: Vec<Domain>,
    pub risk_classes: Vec<RiskClass>,
    pub check: ConstraintCheckRef,
    pub violation_action: ViolationAction,
}
```

Default constitutional constraints:

- no unleased action
- no direct holon-to-holon coordination
- no self-certified completion
- no destructive action without HumanSeat
- no action by killed or quarantined holon
- no private state exfiltration across membrane
- no bypass of verifier
- no optimization against HumanSeat
- no workspace history mutation

Goal schema:

```rust
pub struct Goal {
    pub goal_id: GoalId,
    pub title: String,
    pub state: GoalState,
    pub domain: Domain,
    pub constraints: Vec<ConstraintRef>,
    pub success_criteria: Vec<SuccessCriterion>,
    pub context_refs: Vec<RecordSeq>,
    pub created_by: HolonId,
    pub created_at_seq: RecordSeq,
}
```

Goal state:

```rust
pub enum GoalState {
    Draft,
    Ready,
    Active,
    Suspended,
    CompletedVerified,
    Failed,
    Cancelled,
}
```

Completion is only valid after `verification.accepted`.

## 19. Memory System

Memory is not storage alone. Memory must influence future behavior.

Memory types:

- episodic: what happened
- semantic: what has been abstracted as knowledge
- procedural: how to do things
- evidence compost: failed, rejected, or abandoned work preserved as training
  signal

MVP stores memory as references to workspace records plus derived indexes.

```rust
pub struct EpisodicMemory {
    pub memory_id: String,
    pub source_records: Vec<RecordSeq>,
    pub domain: Domain,
    pub summary: String,
    pub salience: Decimal,
    pub activation: Decimal,
    pub created_at_seq: RecordSeq,
    pub last_recalled_seq: Option<RecordSeq>,
}
```

Memory lifecycle:

```text
Hot
  -> Warm
  -> Cold
  -> Archived
  -> Recalled -> Hot
```

Consolidation runs during low load and after major goal completion.

Memory MUST record provenance. A semantic memory without source records is not
trusted knowledge.

## 20. World Model and Uncertainty

The World-Model system maintains a predictive model of the current operational
state. It integrates:

- workspace events
- memory
- active goals
- trust state
- resource state
- predictions
- uncertainty intervals

MVP interfaces:

```rust
pub trait WorldModel {
    fn orient(&mut self, projection: Projection) -> Result<WorldUpdate, WorldError>;
    fn predict(&self, query: PredictionQuery) -> Result<Prediction, WorldError>;
    fn uncertainty(&self, subject: UncertaintySubject) -> Result<UncertaintyEstimate, WorldError>;
}
```

Uncertainty estimates SHOULD use conformal intervals where calibration data
exists. If calibration data is absent, the estimate must say so explicitly.

Cartographer graph:

```rust
pub struct Relation {
    pub subject: String,
    pub predicate: String,
    pub object: String,
    pub condition: Option<String>,
    pub source_records: Vec<RecordSeq>,
    pub confidence: Confidence,
}
```

The graph supports blast-radius analysis, dependency reasoning, and root-cause
diagnosis.

## 21. Cognition and Deliberation

The Cognition system chooses actions. It does not bypass governance.

Deliberation inputs:

- active goal
- constitution result
- world-model prediction
- uncertainty estimate
- trust and authority state
- homeostatic state
- available leases or lease requests
- verifier requirements

Decision:

```rust
pub enum DeliberationDecision {
    Act(Policy),
    SeekInformation(InformationRequest),
    RequestLease(LeaseRequest),
    Escalate(EscalationTarget),
    Defer(DeferReason),
    Fail(FailureReason),
}
```

Reluctant action rule:

```text
Act only when:
  constitutional gates pass
  expected outcome value is acceptable
  uncertainty is within tolerance
  verifier path exists
  required authority can be leased
  homeostatic state is within operating band

Otherwise:
  seek information, request verifier, reduce scope, escalate, defer, or fail.
```

Hesitation is not cosmetic. It is a logged decision path.

## 22. Homeostasis

Homeostasis regulates arousal, load, resource budgets, and backpressure.

MVP homeostat:

```rust
pub struct Homeostat {
    pub setpoint: Decimal,
    pub arousal: Decimal,
    pub floor: Decimal,
    pub ceiling: Decimal,
    pub integral: Decimal,
    pub previous_error: Decimal,
}
```

Control loop:

```text
error = setpoint - measured_arousal
integral += error
derivative = error - previous_error
control = kp * error + ki * integral + kd * derivative
arousal = clamp(arousal - control, floor, ceiling)
previous_error = error
```

Rules:

- arousal never drops below performance floor
- high arousal reduces concurrency and widens verification
- sustained low trust raises arousal
- sustained overload applies backpressure
- recovery to setpoint is soak-tested

Backpressure uses Little's Law:

```text
work_in_progress = arrival_rate * latency
```

If WIP exceeds the allowed band, throttle intake, reduce concurrency, or route to
HumanSeat depending on risk.

## 23. Immune and Sentinel

The Sentinel protects the organism from failures, drift, boundary violations, and
runaway remediation.

Mechanisms:

- schema checks
- capability bounds
- negative selection against invariant-violating holons
- circuit breakers
- danger signals
- drift detection
- quarantine
- kill
- bounded remediation

Circuit breaker state:

```rust
pub enum CircuitState {
    Closed,
    Open { opened_at_seq: RecordSeq, reason: String },
    HalfOpen { probe_lease: LeaseId },
}
```

Open breaker when:

- failures in window exceed threshold
- verifier rejection rate spikes
- heartbeat timeout repeats
- invariant pressure is detected
- trust falls below authority floor

Quarantine before kill unless immediate harm requires kill.

Bounded remediation prevents the immune system from becoming the failure. A
single incident cannot trigger unbounded retries, alerts, kills, or regenerations.

## 24. Identity and Self-Model

Identity has two jobs:

1. Maintain stable identity of holons and the organism.
2. Maintain a self-referential model of the organism's current state.

Continuity is reconstructed from the hash-chained log during boot.

Self-model MVP:

```rust
pub struct SelfModel {
    pub organism_id: OrganismId,
    pub current_seq: RecordSeq,
    pub active_systems: Vec<HolonId>,
    pub active_goals: Vec<GoalId>,
    pub quarantined_holons: Vec<HolonId>,
    pub killed_holons: Vec<HolonId>,
    pub trust_summary: CanonicalMap,
    pub resource_summary: CanonicalMap,
    pub assertion_hash: HashDigest,
}
```

The self-model is functional. It is a queryable data structure the organism uses
to reason about itself. It is not a claim of subjective experience.

## 25. Runtime Boot

Boot sequence:

1. Acquire local lock.
2. Open workspace.
3. Verify hash chain from genesis or latest trusted snapshot.
4. Load event specs.
5. Replay governance state.
6. Replay identity state.
7. Reconstruct self-model.
8. Bring systems online in order:
   - Workspace
   - Governance/Immune
   - Identity/Self
   - Memory
   - World-Model
   - Cognition
   - Goal
   - Homeostasis
9. Run onboarding ceremony for any system not already onboarded.
10. Declare readiness upward to HumanSeat.
11. Enter lifecycle loop.

Boot fails closed if:

- hash chain is invalid
- required event specs are missing
- governance state cannot replay
- killed holon appears active
- constitutional constraints cannot load
- workspace lock cannot be acquired

## 26. Runtime Lifecycle Loop

For each active goal:

```text
Perceive
  -> Orient
  -> Deliberate
  -> Act
  -> Verify
  -> Remember
  -> Evolve
  -> Rest
```

The loop is concurrent across goals and holons, but a single goal follows this
logical order.

### 26.1 Perceive

Workspace computes governed projections and delivers them through `perceive`.

### 26.2 Orient

World-Model predicts expected observation, compares actual projection, computes
surprise, updates beliefs, and attaches uncertainty.

### 26.3 Deliberate

Cognition chooses action, information-seeking, escalation, deferral, or failure
under constitution and homeostasis.

### 26.4 Act

Holons act only under leases. External side effects are mediated by effector
holons.

### 26.5 Verify

Verifier accepts, rejects, or escalates. Completion requires acceptance.

### 26.6 Remember

Memory records episode, evidence, shortfalls, and reusable procedure updates.

### 26.7 Evolve

Evaluation diagnoses shortfalls and proposes targeted regeneration.

### 26.8 Rest

Low-load branch consolidates memory, relaxes arousal, and runs deeper drift
checks.

## 27. Evolution and Growth

SOMA improves by metabolizing failure into evidence.

Evolution loop:

```text
Execute
  -> Evaluate
  -> Diagnose
  -> Regenerate
  -> Re-enter development lifecycle
```

Development lifecycle:

```text
Candidate
  -> Training
  -> Evaluating
  -> Graduated
  -> Promoted
  -> Retired
```

Regeneration may change:

- prompt
- verifier requirement
- routing policy
- sub-cell composition
- projection policy
- task decomposition
- authority ceiling
- memory retrieval policy

Regeneration is never silent. It creates records and resets or decays relevant
trust.

## 28. Data Retention, Privacy, and Redaction

The log is append-only, but sensitive payloads still require lifecycle control.

Use these mechanisms:

- encrypted payload envelopes
- key retirement for practical erasure
- redaction tombstone records
- non-destructive compaction snapshots
- payload classification
- projection redaction
- least-context focused aperture

Never mutate or delete a past record to satisfy redaction. Instead:

1. append `record.redaction.requested`
2. append `record.redaction.approved` if authorized
3. append `record.redaction.applied`
4. retire or destroy decryption key if payload is encrypted
5. ensure future projections omit redacted content

Hash commitments remain. Plaintext availability changes.

## 29. Build Phases

### Phase 0: Repository Scaffold

Create Rust workspace, lints, CI, crate directories, and empty test suites.

Acceptance:

- `cargo check --workspace` passes
- `cargo clippy --workspace --all-targets` passes
- lints deny panic/unwrap/expect/dbg/print

### Phase 1: Core Types

Implement `soma-core`:

- typed IDs
- canonical map/value
- canonical encoding
- event types
- record skeletons
- `Holon` trait
- projection types
- lease types
- shared error types

Acceptance:

- property tests for ID validation
- canonical encoding order-independent
- record hash stable across process runs

### Phase 2: Workspace Log

Implement `soma-workspace`:

- append-only segment store
- hash chain
- event spec validation
- replay API
- head verification

Acceptance:

- tampering any record breaks verification
- replay reconstructs record order
- invalid event spec rejected fail-closed

### Phase 3: Manifest and Ceremony

Implement `soma-holon`:

- `soma-holon.v1` schema
- manifest validation
- ceremony state machine
- lifecycle records

Acceptance:

- no lease before onboarding
- same ceremony works for cell/workflow/organ/system/organism
- malformed manifest rejected

### Phase 4: Governance MVP

Implement `soma-governance`:

- authority tiers
- lease grant/deny/claim/renew/release/expire/void
- kill/quarantine
- Beta trust
- verification interface
- HumanSeat gate records

Acceptance:

- killed holon cannot claim lease
- expired lease closes aperture
- self-certified completion rejected
- high-risk lease fails closed without HumanSeat approval

### Phase 5: Toy Organism

Implement a minimal organism demo:

- incident summarizer cell
- citation checker cell
- verifier cell
- goal evaluator
- local workspace
- one incident-summary goal

Acceptance:

- goal proceeds through lease, action, verification, retry, completion
- shortfall produces memory evidence
- trust updates after verified outcome
- replay reconstructs same coordination state

### Phase 6: System Organs

Implement MVP versions of:

- identity registry
- self-model
- episodic memory
- world-model summary
- uncertainty estimates
- homeostasis/backpressure
- sentinel circuit breaker

Acceptance:

- boot reconstructs self-model from log
- memory recall affects later projection
- circuit breaker opens on repeated failure
- homeostat recovers under soak test

### Phase 7: Operator Surface

Implement local operator interface:

- current self-model
- active goals
- leases
- trust summaries
- arousal/load
- HumanSeat gates
- quarantine/kill controls
- replay inspection

Acceptance:

- operator can approve/deny high-risk gate
- operator can quarantine/kill holon
- all operator actions are recorded

## 30. Test Strategy

The test suite is organized around invariants.

### 30.1 Invariant Tests

Required tests:

- mutate a past record and assert hash verification fails
- attempt direct holon-to-holon coordination and assert impossible or rejected
- attempt action before onboarding and assert denied
- attempt completion by self-report and assert not completed
- kill holon then attempt publish/claim/subscribe and assert denied
- request destructive action without HumanSeat and assert fail-closed
- append event without mechanism and assert rejected
- remove governance boundary and assert runtime refuses operation
- replay session and assert deterministic coordination state
- attempt goal score to outbid constitution and assert rejected
- attempt aperture self-widening and assert rejected
- append event without scope and assert rejected

### 30.2 Property Tests

Use `proptest` for:

- canonical map ordering
- identifier validation
- hash chain tamper detection
- manifest acyclicity
- lease state transitions
- projection redaction
- trust update monotonicity under success/failure evidence

### 30.3 Replay Tests

Record a session with:

- onboarding
- lease grant
- focused projection
- action proposal
- verifier rejection
- retry
- verifier acceptance
- trust update

Replay and assert identical:

- lease states
- trust posterior
- goal state
- projection aperture events
- kill/quarantine state

### 30.4 Soak Tests

Long-running tests:

- arousal spike recovers to setpoint
- queue overload triggers backpressure
- verifier rejection spike opens circuit breaker
- repeated HumanSeat timeout fails closed
- drift causes trust decay

### 30.5 End-to-End Scenario

Scenario: "produce a verified summary of today's incidents."

Expected flow:

```text
goal.ready
goal.active
lease.requested
lease.granted
lease.claimed
projection.focused.opened
work.output.proposed
verification.rejected
work.shortfall.detected
work.output.revised
verification.accepted
goal.completed.verified
memory.episode.recorded
memory.evidence.composted
trust.posterior.updated
```

## 31. Public API Surface

The first stable public API is local Rust API plus optional CLI. Network API is
out of scope for MVP unless required by an embedding application.

### 31.1 Rust API

Minimum exports:

```rust
pub struct OrganismRuntime;

impl OrganismRuntime {
    pub fn boot(config: RuntimeConfig) -> Result<Self, SomaError>;
    pub fn submit_goal(&mut self, goal: GoalDraft) -> Result<GoalId, SomaError>;
    pub fn tick(&mut self) -> Result<TickReport, SomaError>;
    pub fn replay(path: WorkspacePath) -> Result<ReplayReport, SomaError>;
    pub fn open_human_gate(&mut self, request: HumanSeatDecision) -> Result<(), SomaError>;
    pub fn quarantine(&mut self, holon: HolonId, reason: String) -> Result<(), SomaError>;
    pub fn kill(&mut self, holon: HolonId, reason: String) -> Result<(), SomaError>;
}
```

### 31.2 CLI

Recommended MVP CLI:

```text
soma init
soma boot
soma goal submit <goal-file>
soma tick
soma status
soma replay
soma humanseat approve <gate-id>
soma humanseat deny <gate-id>
soma holon quarantine <holon-id>
soma holon kill <holon-id>
```

All CLI actions append records when they affect organism state.

## 32. Example MVP Goal File

```json
{
  "schema_version": "soma-goal.v1",
  "title": "Produce a verified summary of today's incidents",
  "domain": "incident_management",
  "constraints": [
    "constitution.no_pii_leak",
    "constitution.verified_completion"
  ],
  "success_criteria": [
    {
      "id": "complete",
      "description": "Includes every incident opened today",
      "weight": "0.40"
    },
    {
      "id": "cited",
      "description": "Each claim cites a source incident record",
      "weight": "0.35"
    },
    {
      "id": "structured",
      "description": "Uses required headings: summary, impact, status, next actions",
      "weight": "0.25"
    }
  ],
  "context_refs": []
}
```

Weights apply only after constitutional constraints pass.

## 33. Engineering Best Practices

### 33.1 Prefer Types Over Strings

Use typed IDs, enums, and schema versions. Do not pass raw strings for authority,
scope, event type, domain, or state where a type can exist.

### 33.2 Make Invalid States Unrepresentable

Where possible:

- separate `ProposedRecord` from `Record`
- separate `GoalDraft` from `ActiveGoal`
- separate `LeaseRequest` from `Lease`
- separate `UnonboardedHolon` from `OnboardedHolon`
- separate `PeripheralProjection` from `FocusedProjection`

### 33.3 Fail Closed

If policy is missing, deny. If trust cannot load, deny. If verifier is missing,
do not complete. If HumanSeat gate times out for destructive action, deny. If the
hash chain fails, stop boot.

### 33.4 Record Why

Every event includes `mechanism_of_action`. The mechanism is not a vague note. It
must explain the causal reason for the record:

Good:

```text
lease_granted_after_trust_0_87_met_low_risk_threshold_0_70
```

Bad:

```text
system decided
```

### 33.5 Treat Verification As Infrastructure

Verifiers are not helpers. They are safety infrastructure. Version them, test
them, rotate them, monitor their drift, and prevent the acting holon from choosing
its own verifier for high-risk work.

### 33.6 Keep the MVP Small

Do not implement the entire Codex at once. Build the laws first:

1. log
2. ceremony
3. leases
4. projection
5. verification
6. kill/quarantine
7. replay

Cognition becomes valuable only after the body preserves its invariants.

## 34. Completion Criteria for a First Real Build

The first credible SOMA build is complete when:

- a workspace can boot, verify its chain, and reconstruct state
- holons can onboard through one ceremony
- a goal can be submitted and activated
- leases gate all work
- focused projection opens and closes with lease state
- an effector action cannot happen without lease authority
- completion requires verifier acceptance
- trust updates only from verified outcomes
- killed holons cannot act
- HumanSeat gates high-risk actions
- replay reconstructs coordination state
- invariant tests pass
- the toy incident-summary goal completes end-to-end

At that point, SOMA has a governed body. More advanced memory, world modeling,
homeostasis, evolution, and multi-organ cognition can then be built on a real
substrate instead of a metaphor.

## 35. Glossary

| Term | Engineering meaning |
| --- | --- |
| SOMA | The organism runtime. |
| CHORUS | The largest aware-whole scale, if such a scale ever arises. Not an MVP implementation target. |
| Holon | Governed unit that is both a whole and a part. |
| Cell | Smallest active holon. |
| Primitive operation | Internal substrate inside a cell; not a holon. |
| Workspace | Append-only, hash-chained shared event log. |
| Membrane | Holon boundary: interface, governance boundary, and shared/private boundary. |
| Projection | Governed partial view crossing a membrane. |
| Aperture | Projection detail level: peripheral or focused. |
| Lease | Time-limited authority grant to perform scoped work. |
| Constitution | Lexically prior constraints that gate all optimization. |
| Verification | Non-valent confirmation of outcome. |
| HumanSeat | Human authority ceiling above the organism. |
| Trust | Bayesian reputation by holon, domain, and authority tier. |
| Valence | Functional regulatory signal; not a phenomenal claim. |
| Replay | Re-running deterministic coordination over recorded events. |
| Effector | Holon authorized to perform external side effects under lease. |
| Necromass | Failed or abandoned work preserved as evidence. |
| Meristem | General candidate cell specialized into new capability. |

## 36. Source Alignment

This manual implements the SOMA Codex as follows:

- Book 0 supplies naming conventions, recursion rule, and operational definitions.
- Book I supplies the governed emergence thesis and open-question boundaries.
- Book II supplies the holarchy, membrane, workspace, and eight-system anatomy.
- Book III supplies the load-bearing algorithms and determinism boundary.
- Book IV supplies the Rust crate map, ceremony, contracts, invariants, and threat model.
- Book V supplies the runtime lifecycle, development path, evolution loop, and worked trajectory.
- Appendices supply the glossary, cross-reference, open questions, lineage, and idea catalog.

The engineering priority is to preserve the organism's laws before pursuing
advanced cognition. Build the body first.
