# Cascade Reviewer Protocol

This repository uses an automated review loop via a local MCP tool
named `review_task_summary`.

Cascade must follow this protocol for all non-trivial work.

---

## Protocol

1. Maintain a working log at:

   `.ai/task-summary.md`

2. During implementation:
   - Keep the task summary up to date.
   - Record goals, decisions, files changed, and known limitations.

3. When the task is ready for review, call the MCP tool
   `review_task_summary` with the following arguments:

   - `summaryPath: ".ai/task-summary.md"`
   - `repoRoot: "/home/greg/Code/GitHub/MockTeamGen"`
   - `includeGitDiff: true`
   - `testCommand: ""`

4. Review loop behavior:
   - If the tool returns `done = false`:
     - Read the newest **Automated Review** section in the task summary.
     - Fix the issues identified.
     - Update `.ai/task-summary.md`.
     - Call `review_task_summary` again.
   - Repeat until `done = true`.

5. Completion:
   - Ensure the final task summary accurately reflects the completed work.
   - Do not declare completion until the reviewer returns `done = true`.

---

## Official Documentation Rule

- `.ai/task-summary.md` is the only file the reviewer loop writes to during iterations.
- During review cycles (while `done=false`), do NOT create or modify anything under:
  - `docs/ai_notes/`
- Only after the reviewer returns `done=true`, create/update the relevant `docs/ai_notes/...` files:
  - create the correct numbered note file with required metadata
  - update `docs/ai_notes/index.md`
- If you are unsure about numbering/category, STOP and ask the user for the exact filename and category before writing official docs.

---

## Notes

- The automated review is authoritative.
- High or critical issues must be addressed.
- This protocol applies only to this repository.
