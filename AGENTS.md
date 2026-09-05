# AGENTS.md — the hardspec agent contract

The org-wide contract for humans and AI coding agents working in any
[hardspec](https://github.com/hardspec) repository.

Each repository also carries its own `AGENTS.md` with constraints specific to
it. **Where they conflict, the repository's file wins** — this file is the
floor, not the ceiling.

---

## 1. What this org is

Continuous inspection for hardware design. CI proves the artifact *built*; these
tools prove it is *what was declared*.

    partspec     mechanical parts, CAD-as-code   OpenSCAD, OCCT      pre-alpha
    netspec      PCB connectivity                kicad-cli           pre-alpha
    gerberdiff   fabrication output              the Gerbers         released

A tool belongs here if it (1) takes a **declaration of intent**, (2) adjudicates
it against an **oracle that owns the truth** rather than reimplementing that
oracle's arithmetic, and (3) **never lets *couldn't tell* exit `0`**.

Deliberately out of scope, and named so nobody drifts into them: design entry
and authoring, design *review*, and dependency management. **These tools read;
they do not write your design.**

Each tool is independent. There is no shared runtime and no framework. If you
find yourself building one, see §9 — that is an escalation, not a refactor.

---

## 2. The rule everything else follows from

> **Silence must never read as success.**

A check that could not run, could not reach its evidence, or could not decide
must never be reportable as one that looked and found nothing.

This is not a style preference. It is the property these tools exist to have,
and every clause below is a way it has already been violated in this codebase.

### 2.1 Three outcomes minimum, and the third is not optional

*Satisfied*, *violated*, and **could not tell**. The third never exits `0`.

partspec maps `Verdict.INCOMPLETE` to exit `2` for exactly this
(`src/partspec/status.py`), and its comparison verbs answer over
`{identical: 0, different: 1, indeterminate: 2}` — because for a differ, too,
silence must never read as *no difference*.

**Do not add an `--allow-incomplete`-style escape hatch** without a recorded
case where "could not tell" is a design's genuine long-term state. Shipping the
escape hatch alongside the discipline means the discipline is never tested.

### 2.2 An environment fault is not a verdict on the design

No engine on `PATH`, an engine that will not start, a source file that is not
there — none of these are statements about the part or the board. A run on a
machine without the oracle installed must never report a design as disproven.

Carry it **as a field a consumer can branch on**, not as prose in a message, and
give it its own exit code. netspec calls this "the most valuable thing taken
from partspec" (`docs/DECISIONS.md` D10).

### 2.3 Never substitute a plausible number for an answer

If the representation lacks the entity, return `unsupported`. Do not fit,
reconstruct, or approximate your way to a result. A triangle mesh has no
cylindrical face, and inventing one produces confident wrong numbers **in the
unsafe direction**.

Two corollaries, both learned the hard way in partspec:

- **Check the precondition before measuring, and make it narrow.** Volume and
  centre of mass need a closed, consistently-wound surface. Every one of those
  quantities returned a confident wrong number on an open mesh until
  2026-08-05. Equally, do not refuse *more* than the mathematics requires — an
  unnecessary `unsupported` is also a way of failing to answer an answerable
  question.
- **Never read an absolute measurement out of a library that rebuilds its
  input.** manifold3d retriangulated 55 of 10,688 triangles on a *clean* part
  and moved its volume by 0.078%. That number describes its reconstruction, not
  the artifact you exported. And when such a library reports an error status,
  believe it — manifold3d's rejected objects still answer `.decompose()` and
  `.genus()`.

### 2.4 A check that cannot fail is not a check

Break the thing it checks, watch it go red, put it back. A check whose red state
you have not personally observed is not a check.

**A skipped test is not a passing test.** partspec's suite once reported
195 passed / 23 skipped in CI because no runner had OpenSCAD — and those 23 were
the entire end-to-end path. If you add a `skipif` for a missing tool, add the
tool to the suite's require-engines handling so CI cannot lose it silently. Never
gate a test module at import: that reports as *one* skipped line and takes every
test in the file with it, including the ones needing nothing.

### 2.5 Status claims are part of the gate

The "Status:" lines in a `README.md` and an `AGENTS.md` say what does and does
not work. partspec's asserted its backends were unimplemented for three phases
after they shipped — in a project whose entire point is that a tool must not
claim more than it has established. Treat them as code: if your change makes one
false, the change is not finished.

---

## 3. The oracle boundary

**The domain engine leaks in through exactly one module.** netspec confines
KiCad to `oracle/` — no `kicad-cli` string and no `subprocess` import anywhere
else (`docs/DECISIONS.md` D4) — and that boundary *is* its migration plan for the
next KiCad major.

Do not reimplement the oracle's arithmetic. The entire premise is that the
engine knows what the design is and we do not.

Prefer a stable process boundary over an in-process binding that upstream may
delete. netspec never imports `pcbnew` because it is already gone in KiCad
master (D3).

---

## 4. Intent is code

Contracts are written in Python, not sidecar YAML. More expressive, no schema to
design or version, and it makes the tool's own vocabulary the thing being
authored against.

The consequence is explicit and must stay documented in each tool: **a contract
is code, and running a check executes it.**

---

## 5. The stable surface is the report and the exit code

Not the Python API. Every tool here is pre-1.0 and its internals will move.
Consumers — CI, agents, MCP clients — depend on the artifact schema plus the
process exit code, and those two change with a documented decision or not at all.

Corollary: an agent-facing MCP server is an *optional extra* over the CLI, and
its verbs are stateless — each call runs the tool and returns its artifact. It
never becomes a second, weaker interface with its own semantics.

---

## 6. The shared vocabulary — and where members currently disagree

### 6.1 Statuses (per check)

Common core, in all members that adjudicate: **`pass` · `fail` · `unsupported` ·
`skipped`**. Only `pass` is green.

`approximate` is a **domain-gated extension**, for when a measured error
interval straddles the threshold. partspec has it. netspec deliberately does
**not**: connectivity is discrete, so the status would be unreachable, and
importing interval epistemics into an exact domain adds concepts without adding
truth (D9, guarded by `test_report_carries_no_tolerance`).

**Add `approximate` only if your domain has real error intervals.** Absence is a
decision to record, not an omission to fix.

### 6.2 Exit codes

Agreed across partspec and netspec today:

    0    satisfied
    1    violated
    4    environment fault / error — not a verdict on the design

### 6.3 Open adjudications

These are **real conflicts between shipped members**, found while writing this
document. They are recorded rather than resolved, because resolving them changes
released behaviour and that is a decision with an owner.

**A1 — exit code `2` means two different things.**
partspec: `incomplete` (`status.py`), with usage errors at `64` (`EX_USAGE`).
netspec: `EXIT_USAGE` (`cli.py:29`), with no code for "could not evaluate".
A consumer branching on `2` across both tools is reading two different facts.
*Recommendation:* adopt partspec's split — `2` = could-not-tell, `64` = usage —
since `2` is the code the family's core rule needs most.

**A2 — netspec cannot report "could not tell" at the verdict level.**
`Verdict = Literal["pass", "fail"]` (`check.py:28`), and verdict is green only
when every rule is green — so an `unsupported` rule collapses into `fail`, which
says the board is wrong when the truth is that the tool could not check it. D10
also documents a `verdict: "error"` that the type does not contain; the
environment fault is carried by the exit code (`EXIT_ENVIRONMENT`, `cli.py:30`)
and not, as D10 requires, by a field in the report.
*Status: read from source, not reproduced.*

**A3 — gerberdiff has no third state, and one path exploits it.**
Its report summary carries `has_changes: boolean` (`docs/schema.md`) and layer
status is `matched | added | removed`. There is no value for *could not tell*.

*Status: **reproduced**, 2026-09-05, v0.29.1 — [gerberdiff#17](https://github.com/CameronBrooks11/gerberdiff/issues/17).*
A flash whose D-code selects an aperture that was never defined is dropped with
**no diagnostic of any severity**; `diff` and `geomdiff` then report `0 changes`
at exit `0` under `--fail-on-diff`, with zero bytes on stderr, and the JSON
report is byte-identical to diffing a board against an exact copy of itself.

Two things this exercise is worth recording, because they are the general
lesson and not a fact about Gerbers:

- **The first reading was wrong.** The hypothesis under review was that
  *warning*-level diagnostics leaked a silent pass, and that the missing `Error`
  branch in the diff commands' `_on_diagnostic` was the hole. Neither holds:
  both engines promote any `Error` diagnostic to a raised `GerberParseError`
  (`geometry/driver.py:105`, `diff/diff_engine.py:185`) and exit `2`, and the
  missing branch is unreachable. The real defect was one the reading had not
  considered — an aperture reference that produces no diagnostic at all. **The
  repro did not confirm the analysis; it replaced it.** This is why §7 says
  reproduce before reporting.
- **The tool already held the evidence.** `gerberdiff parse` prints
  `nets: 2, apertures: 1` and a bounding box reaching the dropped pad's *centre*
  rather than its edge. Nothing had to be measured that the tool was not already
  computing — it simply had no state in which to say it. That is what a missing
  third outcome costs: not a lost measurement, a lost *verdict*.

**Do not "fix" a member to match this document without an issue and a decision
entry.** The vocabulary follows the tools; the tools do not silently follow the
vocabulary.

---

## 7. Evidence

**Reproduce before reporting.** Inferring a failure mode from reading code is a
guess, and a wrong guess sends the fix in the wrong direction — or hides that the
real behaviour is worse than the one described. Where this document states a
finding it has not reproduced, it says so; do the same.

**Never state a number you did not produce.** A figure that reaches a spec, a
README, a commit message or an issue carries the command that produced it. An
estimate is fine when labelled as one and misleading when presented as a
measurement.

**Verify against the tool, not its roadmap.** netspec plans only against KiCad
facts confirmed in `master` and re-verified weekly in CI, because the roadmap
wiki is stale (D6). Upstream documentation describes intentions; upstream source
describes behaviour.

**Decisions live in each repo's `docs/DECISIONS.md`, numbered, with the
reasoning that produced them.** Do not relitigate a numbered decision. If it is
wrong, add a superseding entry.

---

## 8. How work lands

**Branch, PR, review, merge.** `just check && just test` before every commit.
Never `--no-verify`, never skip CI.

Conventional Commits: `type(scope): description`. Imperative, lowercase, no
trailing period, subject ≤ 72 characters. One logical change per commit.

**No AI attribution anywhere** — no co-author trailer, no generated-with footer,
no session URL in a commit message or PR body.

Where a repository's specs are normative, the code implements them: if code and
spec disagree, that is a bug in one of them. Say which. Do not silently pick.

**Do not write a test that reads a doc, reads the code, and diffs them.** That is
two copies of one fact with a failure report attached — generate the doc instead.
Equally, do not assert that a phrase appears in prose: `assert "five classes" in
README` passes when the README says "five classes in 2019, all of which failed".
A doc test must assert something **executable** — the example builds, the command
runs.

---

## 9. Licensing

Apache-2.0 across every repository in this org, matching all three members as
they stand.

Fixtures that are meant to be vendored into a third-party implementation may be
released more permissively per directory, but only with a decision entry saying
why.

---

## 10. Escalate, do not decide

Stop and ask rather than proceeding, for:

- anything that reverses a numbered decision in a repository's `DECISIONS.md`
- changing a report schema or an exit code in a released tool
- extracting shared code into a common library or framework across members
- adding a runtime dependency to a tool whose core is dependency-free by design
- deleting data, force-pushing, or rewriting published history
- publishing anything that names a private individual or private infrastructure

Everything else: decide, record the reasoning where the next agent will find it,
and keep moving.
