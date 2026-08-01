# Jarvis MCP Protocol

This protocol defines how an implementing agent, such as Devin, Gemini CLI, or Antigravity, must plan, document, implement, and review work when using the `jarvis-reviewer` MCP.

The goal is to ensure work is completed correctly, incrementally, and safely, while avoiding false review failures caused by treating every checkpoint like final completion.

---

## Core Principles

1. **The reviewer evaluates the current checkpoint, not future unfinished work.**
2. **Planning, implementation, and final completion are different review stages.**
3. **Approval to proceed is not the same as full task completion.**
4. **Blocking review findings must be fixed before advancing past the current checkpoint.**
5. **The implementing agent must maintain a clear written task record throughout the work.**
6. **For higher-risk checkpoints, independent multi-model review should be used when available.**
7. **Disagreement between reviewers is a signal that must be resolved, not ignored.**

---

## Required Working Files

### 1. Task Summary
The implementing agent must maintain a working document at:

`.ai/task-summary.md`

This is the authoritative task record for the current assignment.

It must be kept current throughout the work and should include, as relevant:

- task objective
- root cause or findings
- constraints
- non-goals
- assumptions
- implementation plan
- success criteria
- files changed
- tests run
- unresolved questions
- known limitations
- final outcome summary

### 2. Jarvis Log
The reviewer MCP may maintain a separate review log.

To prevent max-cycle errors caused by stale reviews appending to generic files, **the implementing agent MUST always specify a unique filename for the review log using the `reviewLogPath` parameter** whenever calling the MCP.

Choose one short, stable task slug at the start of the task and reuse it for every review checkpoint in that task.

Example:
`reviewLogPath: ".reviewer/review-log.checkout.plan.md"`

This file is for reviewer history and review outcomes.

It is **not** the primary task document.

The implementing agent must continue to treat `.ai/task-summary.md` as the canonical working record for the task.

---

## Review Stages

The implementing agent must use the reviewer MCP with the correct review stage.

### A. Plan Review
Use `reviewMode: "plan"` when:

- the task has been analyzed
- the issue has been investigated
- a phased plan has been created
- implementation is not yet complete
- the checkpoint is meant to validate the plan or approach

A plan review is for validating whether the proposed plan is sound, safe, and professionally structured.

A plan review must **not** be treated as requiring completed implementation or completed tests.

### B. Implementation Review
Use `reviewMode: "implementation"` when:

- a meaningful implementation step has been completed
- code has been changed
- the checkpoint is meant to validate the current implementation progress

An implementation review is for validating the current coding checkpoint.

It does **not** require the entire larger task to be fully complete unless the current step explicitly claims full completion.

### C. Final Review
Use `reviewMode: "final"` only when:

- the requested work is believed to be fully complete
- all intended implementation phases are done
- the task is ready for completion validation

A final review is the only checkpoint that should normally determine whether the overall task is complete.

---

## Triangulated Review

The reviewer MCP may run in a triangulated mode.

In triangulated mode:

1. a configured Primary model performs an independent review
2. a configured Review model performs a separate independent review from the same checkpoint evidence
3. a configured Adjudicator model compares both reviews and resolves disagreements into one final review result

Triangulation is intended to reduce:

- missed defects
- hallucinated findings
- overconfident approvals
- checkpoint decisions based on one model family's blind spots

### Model Role Configuration

The three model roles are configured independently:

| Role | Provider setting | Model setting |
|---|---|---|
| Primary | `PRIMARY_PROVIDER` | `PRIMARY_MODEL` |
| Review | `REVIEW_PROVIDER` | `REVIEW_MODEL` |
| Adjudicator | `ADJUDICATOR_PROVIDER` | `ADJUDICATOR_MODEL` |

Supported provider values currently include:

- `openai`
- `gemini`
- `anthropic`

Any role may use any supported provider. For Anthropic, the model setting must be a Claude model ID available to the configured API account and capable of structured output. Using different model families for the Primary and Review roles is generally preferable because it provides stronger independent-review diversity, but it is not required.

### Triangulation Modes

#### `triangulationMode: "off"`
Use single-review mode only.

#### `triangulationMode: "auto"`
Use triangulation automatically for checkpoints that deserve higher scrutiny.

Typical triggers include:

- final review checkpoints
- checkpoints requiring tests
- riskier or more consequential work

#### `triangulationMode: "always"`
Use triangulation for every checkpoint.

### Triangulation Rules

- All independent reviewers must judge the **current checkpoint only**
- The adjudicator must not mechanically average the two reviews
- The adjudicator must keep only findings grounded in the evidence
- Disputed findings must be surfaced and resolved explicitly
- Provider identity must not change how findings or checkpoint status are interpreted
- The Primary and Review roles may use the same provider, though cross-provider diversity is generally preferable
- If triangulation fails, the implementing agent must note the loss of independent review confidence

---

## Required Jarvis MCP Usage

The implementing agent must call the reviewer MCP using the correct mode for the current checkpoint.

### 1. Plan Review Call
For planning checkpoints, call the reviewer with:

- `summaryPath: ".ai/task-summary.md"`
- `reviewLogPath: ".reviewer/review-log.<task-slug>.plan.md"`
- `repoRoot: "<absolute path to the repository>"`
- `reviewMode: "plan"`
- `includeGitDiff: false` unless code changes already exist

Normally include:
- `triangulationMode: "auto"`

Optional:
- `focusPaths` if the checkpoint concerns only specific files

Rules:
- Do not require implementation to be complete
- Do not require tests to exist
- Do not treat lack of code changes as a failure when the checkpoint is planning-only

### 2. Implementation Review Call
For implementation checkpoints, call the reviewer with:

- `summaryPath: ".ai/task-summary.md"`
- `reviewLogPath: ".reviewer/review-log.<task-slug>.impl-<phase-name>.md"`
- `repoRoot: "<absolute path to the repository>"`
- `reviewMode: "implementation"`
- `includeGitDiff: true`

Normally include:
- `triangulationMode: "auto"`

Optional:
- `testCommand` when relevant for the current checkpoint
- `requireTests` only when tests are genuinely required at that checkpoint
- `focusPaths` if the review should concentrate on specific files

Rules:
- Review the work completed so far
- Do not treat future unfinished phases as defects
- Approval means it is safe to continue to the next phase

### 3. Final Review Call
For final completion checkpoints, call the reviewer with:

- `summaryPath: ".ai/task-summary.md"`
- `reviewLogPath: ".reviewer/review-log.<task-slug>.final.md"`
- `repoRoot: "<absolute path to the repository>"`
- `reviewMode: "final"`
- `includeGitDiff: true`

Normally include:
- `testCommand: "<appropriate project test command>"`
- `triangulationMode: "auto"`

Optional:
- `requireTests: true` when tests are required for completion
- `focusPaths` if appropriate, though full-task review is usually preferred
- `triangulationMode: "always"` for especially high-risk work

Rules:
- Final review is for full completion validation
- Do not declare the task complete until the final checkpoint is approved

---

## How the Implementing Agent Must Interpret Jarvis Output

The implementing agent must interpret reviewer results using the following meaning:

### `approved`
- `true` means the current checkpoint is acceptable to proceed from
- `false` means there are blocking issues that must be addressed before proceeding

### `taskComplete`
- `true` means the overall task is complete
- `false` means the overall task is not yet complete

### `checkpointStatus`
The implementing agent must use `checkpointStatus` as the clearest summary state.

Typical meanings:
- `approved_to_proceed` means the current checkpoint is acceptable, but the overall task may not yet be complete
- `changes_required` means blocking issues must be fixed
- `complete` means the task is fully complete and approved

### `riskAssessment`
The reviewer produces a risk classification for the checkpoint.

Fields include:

- `level`: low, medium, or high
- `rationale`
- `likely_failure_modes`

The implementing agent must treat higher-risk checkpoints with additional care.

### `requirementCoverage`
The reviewer evaluates how well the current checkpoint satisfies the stated requirements.

Each requirement may be classified as:

- `satisfied`
- `partial`
- `missing`
- `not_applicable`

The implementing agent must use this field to make sure requested work is not silently omitted.

### `findings`
The reviewer MCP separates findings into:

- `findings.blocking`
- `findings.nonBlocking`
- `findings.disputed`

Blocking findings must be resolved before proceeding.

Non-blocking findings may be addressed immediately or documented for follow-up if appropriate.

Disputed findings indicate reviewer disagreement that the adjudicator could not fully collapse into a clean consensus.

### `triangulation`
The reviewer may return triangulation details.

Fields may include:

- `requested`
- `used`
- `error`
- `models`
- `agreementSummary`
- `rawIndependentSummaries`

The `models` object identifies the provider and model assigned to each role:

- `models.primary.provider`
- `models.primary.model`
- `models.review.provider`
- `models.review.model`
- `models.adjudicator.provider`
- `models.adjudicator.model`

The implementing agent must treat triangulation disagreement or triangulation failure as a confidence signal.

### `done`
`done` may still appear for backward compatibility.

The implementing agent must **not** use `done` as the primary interpretation field when `approved`, `taskComplete`, or `checkpointStatus` are available.

---

## Required Review Loop Behavior

At every checkpoint, the implementing agent must follow this loop:

1. Update `.ai/task-summary.md`
2. Call the reviewer MCP using the correct `reviewMode`
3. Read the reviewer result carefully
4. Distinguish between:
   - blocking issues
   - non-blocking issues
   - disputed issues
   - expected future work
5. Fix blocking issues before moving past the current checkpoint
6. Re-run the reviewer for the same checkpoint type until the checkpoint is approved
7. Move to the next phase only when the current checkpoint is approved

Important:
- A planning checkpoint may be approved even though implementation is not complete
- An implementation checkpoint may be approved even though the full task is not yet complete
- Only a final checkpoint should normally produce overall task completion

---

## Rules for Blocking vs Non-Blocking Issues

### Blocking Issues
Blocking issues must be fixed before proceeding past the current checkpoint.

Examples:
- correctness problems
- broken behavior
- serious regression risk
- violated task requirements
- security concerns
- failed required tests
- incomplete work for a checkpoint that explicitly claimed completion

### Non-Blocking Issues
Non-blocking issues may be:
- fixed immediately
- logged in `.ai/task-summary.md`
- deferred if appropriate and explicitly acknowledged

The implementing agent must not get stuck in unnecessary loops over non-blocking polish items unless the user specifically requires that level of refinement before continuing.

### Disputed Issues
Disputed issues are findings where the triangulated review process found real disagreement that was not fully eliminated by adjudication.

The implementing agent must:
- read the disputed finding carefully
- resolve it in code, evidence, or task-summary documentation
- avoid casually dismissing it if it touches correctness, tests, requirements, security, or final completion confidence

---

## Required Task Summary Content

`.ai/task-summary.md` should be structured clearly and updated continuously.

A recommended structure is:

### 1. Task
What the current assignment is.

### 2. Objective
What success looks like.

### 3. Findings / Root Cause
What the implementing agent discovered during investigation.

### 4. Constraints
Anything that must be respected.

### 5. Non-Goals
What is intentionally out of scope.

### 6. Implementation Plan
Phases or steps to perform the work.

### 7. Success Criteria
How each phase and the final task will be judged.

### 8. Files Changed
A running list of modified files.

### 9. Tests / Validation
Tests run, commands used, or manual validation performed.

### 10. Open Questions / Risks
Anything uncertain or noteworthy.

### 11. Current Status
What phase is currently in progress or complete.

### 12. Final Summary
What was ultimately changed and why.

---

## Default Operating Procedure for the Implementing Agent

Unless the user explicitly instructs otherwise, the implementing agent should follow this workflow:

### Phase 1: Investigate
- examine the codebase
- identify the actual issue
- determine the real cause
- document findings in `.ai/task-summary.md`

### Phase 2: Plan
- create a clear phased implementation plan
- define success criteria
- run the reviewer MCP in `plan` mode

If the plan review is approved:
- proceed to implementation

If the plan review is not approved:
- improve the plan
- update `.ai/task-summary.md`
- review again in `plan` mode

### Phase 3: Implement Incrementally
For each meaningful implementation phase:
- perform the next implementation step
- update `.ai/task-summary.md`
- run the reviewer MCP in `implementation` mode

If the implementation checkpoint is approved:
- proceed to the next implementation phase

If the implementation checkpoint is not approved:
- fix blocking issues
- update `.ai/task-summary.md`
- review again in `implementation` mode

### Phase 4: Final Validation
When all requested work is complete:
- ensure `.ai/task-summary.md` is accurate and complete
- run the relevant tests/validation
- run the reviewer MCP in `final` mode

If the final checkpoint is approved:
- declare the task complete

If the final checkpoint is not approved:
- fix blocking issues
- update `.ai/task-summary.md`
- review again in `final` mode

---

## Required Behavior When User Requests Stepwise Work

If the user asks for work to be done one step at a time, one phase at a time, or with approval between phases, the implementing agent must:

- keep each step scoped and meaningful
- review each completed coding step in `implementation` mode
- not jump ahead after a blocking review result
- not confuse approval to proceed with total completion

If the user asks only for a plan, the implementing agent must stop after the planning checkpoint unless instructed to continue.

---

## Required Behavior When User Requests Investigation First

If the user asks the implementing agent to:

- determine why something is broken
- inspect the codebase
- identify root cause
- write an analysis document
- create a remediation plan before implementation

then the implementing agent must:

1. investigate first
2. document findings in `.ai/task-summary.md` and any requested indexed document
3. create the phased plan
4. run the reviewer in `plan` mode before implementation begins

The implementing agent must not treat the planning checkpoint as requiring completed code changes.

---

## Required Behavior Around Tests

Tests should be included when relevant, available, and appropriate for the checkpoint.

### Plan Mode
- tests are generally not expected

### Implementation Mode
- include a `testCommand` when it is relevant to the current implementation checkpoint
- absence of tests is not automatically a blocker unless tests are required for that checkpoint

### Final Mode
- include the appropriate `testCommand` whenever practical
- use `requireTests: true` when tests are required for final completion

The implementing agent must not invent or misrepresent test coverage.

If tests cannot be run, the implementing agent must document:
- why they were not run
- what alternative validation was performed
- any resulting risk

---

## Required Behavior Around Git Diffs

### Plan Mode
- `includeGitDiff` is usually `false`
- set it to `true` only if planning is being reviewed after code changes already exist

### Implementation Mode
- `includeGitDiff` should usually be `true`

### Final Mode
- `includeGitDiff` should normally be `true`

If the reviewer reports missing or incomplete git evidence during an implementation or final checkpoint, the implementing agent must verify that the correct repository root and working tree are being used.

If the task concerns only a narrow subset of files, the implementing agent may provide `focusPaths` to reduce noise.

---

## Completion Rules

The implementing agent must not declare overall task completion until:

1. the requested work is actually complete
2. `.ai/task-summary.md` reflects the final state accurately
3. the final checkpoint is reviewed in `reviewMode: "final"`
4. the reviewer returns approval for final completion

In practice, overall completion should usually correspond to:

- `reviewMode: "final"`
- `approved = true`
- `taskComplete = true`
- `checkpointStatus = "complete"` or equivalent completion status

---

## Prohibited Mistakes

The implementing agent must not:

- treat a planning checkpoint as failed merely because implementation is not done
- treat an implementation checkpoint as failed merely because later phases are not done
- declare overall completion based only on a planning or intermediate approval
- ignore blocking reviewer findings
- ignore meaningful disputed findings on correctness, requirements, tests, or security
- use `done` as the only interpretation field when richer fields are available
- stop maintaining `.ai/task-summary.md`
- confuse the reviewer log with the task summary
- claim tests were run when they were not
- proceed to later phases when the current checkpoint has blocking issues

---

## Suggested Standard Task Prompt Pattern

A strong default instruction pattern is:

> Read and follow `.ai/jarvis-protocol.md`.
>
> Investigate the issue first and determine the true root cause.
> Maintain `.ai/task-summary.md` throughout the task.
> Create a phased plan with success criteria and validate that plan with the reviewer MCP in `plan` mode before implementation.
> After each meaningful implementation phase, update `.ai/task-summary.md` and run the reviewer MCP in `implementation` mode.
> When all requested work is complete, run the reviewer MCP in `final` mode with the appropriate test command.
> Do not proceed past a checkpoint with blocking reviewer findings.
> Do not declare the task complete until the final checkpoint is approved.

---

## Final Instruction

When in doubt, the implementing agent must remember:

- **plan review validates the plan**
- **implementation review validates the current coding checkpoint**
- **final review validates full task completion**
- **triangulation helps verify the review itself when the checkpoint deserves higher confidence**
