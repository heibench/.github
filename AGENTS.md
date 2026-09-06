# AGENTS.md — the heibench agent contract

The org-wide contract for humans and AI coding agents working in any
[heibench](https://github.com/heibench) repository.

Each repository also carries its own `AGENTS.md` with constraints specific to
it. **Where they conflict, the repository's file wins** — this file is the
floor, not the ceiling.

---

## 1. What this org is

**Hardware Engineering Integration bench: drive the engine, check the result.**

Two layers, and neither is worth much alone.

    DRIVE     put an engineering engine under program control
              headless, scriptable, version-aware, deterministic

    VERIFY    adjudicate what it produced against declared intent

A tool belongs here if **both** hold:

1. It puts an engineering engine or artifact under **program control** — no
   human in the loop.
2. It is **honest about what it established** — a structured result, a
   meaningful exit code, never reporting success it did not verify, never
   substituting a plausible result for a real one.

**Out of scope, deliberately:** authoring and design generation, language
runtimes, slicer post-processing, dependency management, and machine control at
runtime. heibench is the design-time middle.

Where a member repository is private, **do not name it, link it, or describe its
internals in anything public** — issues on other projects, upstream reports,
commit messages, published docs.

---

## 2. The rule everything else follows from

> **Silence must never read as success.**

A check that could not run, could not reach its evidence, or could not decide
must never be reportable as one that looked and found nothing.

**This is the enabling condition, not a quality preference.** A person catches a
bad render by glancing at it; a script does not glance, and neither does an
agent. Strip out the human who would have noticed, and the tool's own honesty
is the only thing left holding the result up. That is the whole reason this org
can exist at all — so it is the first rule, and it binds drivers as hard as it
binds checkers. A driver that swallows an engine error and returns a truncated
artifact poisons the loop upstream of every check that would have caught it.

**How often it is violated is the point.** This exact defect — no state for
*could not tell*, defaulting to green, to a wrong verdict, or to a signal the
caller cannot read — has been recorded **ten times as of 2026-09-06**, across
five unrelated domains, written at different times by the same author. Nine are
fixed and one is **accepted** -- measured, bounded, and deliberately not fixed,
because every channel that could refuse it refuses correct work too. They reach
callers through drivers exactly as they do through checkers.

**The record is at <https://heibench.com/silence.html>**, which is canonical for
it: each case with its reproduction, its layer, and its status. Add a case there,
not here. Most were found by *running* the code after a reading of it had
concluded something different, twice concluding the wrong mechanism entirely.
Nobody set out to build any of them that way. Assume you are doing it too.

**When you file an instance, label the issue `silence-defect` and add it to the
record in the same sitting.** Filing is the only moment when someone reliably
knows the case exists; the label's description says where it goes. Nothing else
connects the two, and without it the record went stale twice -- once by five
cases, and once by two within a single day. The count is the argument, so a
record that undercounts makes the case weaker than the evidence supports.

That label is also the drift check, and it costs one query:

```
gh search issues --owner=heibench --label silence-defect
```

If the label and the record disagree, **the record is wrong**. Per 2.5, that
makes it a status claim like any other.

### 2.1 Three outcomes minimum, and the third is not optional

*Satisfied*, *violated*, and **could not tell**. The third never exits `0`.

partspec maps `Verdict.INCOMPLETE` to exit `2` for exactly this
(`src/partspec/status.py`), and its comparison verbs answer over
`{identical: 0, different: 1, indeterminate: 2}` — because for a differ, too,
silence must never read as *no difference*.

For a **driver** the same rule reads: a call that did not do the thing must not
return as though it did. Establish the artifact exists before saying so.

**Do not add an `--allow-incomplete`-style escape hatch** without a recorded
case where "could not tell" is a genuine long-term state. Shipping the escape
hatch alongside the discipline means the discipline is never tested.

### 2.2 An environment fault is not a verdict on the design

No engine on `PATH`, an engine that will not start, a source file that is not
there — none of these are statements about the part or the board. A run on a
machine without the engine installed must never report a design as disproven.

Carry it **as a field a consumer can branch on**, not as prose in a message, and
give it its own exit code. netspec calls this "the most valuable thing taken
from partspec" (`docs/DECISIONS.md` D10).

### 2.3 Never substitute a plausible number for an answer

If the representation lacks the entity, return `unsupported`. Do not fit,
reconstruct, or approximate your way to a result. A triangle mesh has no
cylindrical face, and inventing one produces confident wrong numbers **in the
unsafe direction**.

- **Check the precondition before measuring, and make it narrow.** Volume and
  centre of mass need a closed, consistently-wound surface. Every one of those
  returned a confident wrong number on an open mesh until 2026-08-05. Equally,
  do not refuse *more* than the mathematics requires — an unnecessary
  `unsupported` is also a way of failing to answer an answerable question.
- **Never read an absolute measurement out of a library that rebuilds its
  input.** manifold3d retriangulated 55 of 10,688 triangles on a *clean* part
  and moved its volume by 0.078%. That describes its reconstruction, not the
  artifact you exported. And when such a library reports an error status,
  believe it — manifold3d's rejected objects still answer `.decompose()` and
  `.genus()`.

### 2.4 A check that cannot fail is not a check

Break the thing it checks, watch it go red, put it back. A check whose red state
you have not personally observed is not a check.

**A skipped test is not a passing test.** partspec's suite once reported
195 passed / 23 skipped in CI because no runner had OpenSCAD — and those 23 were
the entire end-to-end path. Never gate a test module at import: that reports as
*one* skipped line and takes every test in the file with it.

**Clear `__pycache__` before you believe the observation.** The break-and-watch
procedure above has a failure mode that inverts it, and it is invisible while it
happens:

    find . -name __pycache__ -type d -exec rm -rf {} +

CPython invalidates a `.pyc` by comparing the source's mtime **and size**, with
mtime truncated to one second. The natural red-state edit is one character —
flipping a comparison, changing a return value, swapping a constant — which keeps
the size identical, and a break-run-restore cycle finishes well inside one second.
The `.pyc` is then reused and **the interpreter runs the previous version of the
code you just edited**.

Reproduced deterministically: with `return 0` changed to `return 3` and run in the
same second, the interpreter answered `0` while `inspect.getsource` showed `3`.
Note the direction — the break was *invisible*, so the observation is a false
**green**. That is §2.1's silence-reading-as-success landing inside the one
procedure meant to defend against it: you break a check, it still passes, and the
honest conclusion from that evidence is the wrong one. `getsource` disagreeing
with the interpreter is the tell, because `getsource` re-reads the file and the
interpreter does not.

slicelab reports the mirror case — a false *red* on a restored tree — which is the
same mechanism with the cache written from the broken source instead. Recorded as
reported: it was not reproduced here, and the window for it is narrower. Neither
direction is worth diagnosing in the moment. Clear the cache and measure again.

### 2.5 Status claims are part of the gate

The "Status:" lines in a `README.md` and an `AGENTS.md` say what does and does
not work. partspec's asserted its backends were unimplemented for three phases
after they shipped. Treat them as code: if your change makes one false, the
change is not finished.

---

## 3. The engine boundary

**The engine leaks in through exactly one module.** netspec confines KiCad to
`oracle/` — no `kicad-cli` string and no `subprocess` import anywhere else
(`docs/DECISIONS.md` D4) — and that boundary *is* its migration plan for the
next KiCad major. orlab reached the same design independently: never hardcode a
package root, detect the jar version before starting the JVM, keep per-version
facts in `profiles/`.

**Engines move under you, and their own documentation lies about it.** Plan only
against facts verified in the engine's source or binary, and re-verify them on a
schedule — netspec counts `registerHandler<>` calls in KiCad `master` and pins
what it relies on in a test, because the roadmap wiki is stale (D6). orlab
detects 24.12's `net.sf.openrocket` → `info.openrocket.core` rename rather than
assuming either.

**Do not reimplement the engine's arithmetic.** The entire premise is that the
engine knows what the design is and we do not. Prefer a stable process boundary
over an in-process binding upstream may delete — netspec never imports `pcbnew`
because it is already gone in KiCad master (D3).

**Degrading to an older profile is a "could not tell", not a success.** Where a
driver falls back because it does not recognise a version, that fact must reach
the caller as a value, not only a log line. orlab exposes `profile_exact` for
exactly this, and did not at first — <https://heibench.com/silence.html> case 3.

---

## 4. Intent is code

Contracts are written in Python, not sidecar YAML. More expressive, no schema to
design or version, and it makes the tool's own vocabulary the thing being
authored against.

The consequence is explicit and must stay documented in each tool: **a contract
is code, and running a check executes it.**

---

## 5. The stable surface is the artifact and the exit code

Not the Python API. Every tool here is pre-1.0 and its internals will move.
Consumers — CI, agents, MCP clients — depend on the artifact schema plus the
process exit code, and those two change with a documented decision or not at all.

For a driver the equivalent surface is **what the call returns and what it
guarantees about the engine's output**. Returning `None` and relying on "it did
not raise" is not a surface; the caller cannot branch on it.

An agent-facing MCP server is an *optional extra* over the CLI, and its verbs
are stateless — each call runs the tool and returns its artifact. It never
becomes a second, weaker interface with its own semantics.

---

## 6. Shared vocabulary — and where members disagree

### 6.1 Statuses (per check)

Common core, in every member that adjudicates: **`pass` · `fail` ·
`unsupported` · `skipped`**. Only `pass` is green.

`approximate` is a **domain-gated extension**, for when a measured error
interval straddles the threshold. partspec has it; netspec deliberately does
not, because connectivity is discrete and importing interval epistemics into an
exact domain adds concepts without adding truth (D9, guarded by
`test_report_carries_no_tolerance`). **Absence is a decision to record, not an
omission to fix.**

### 6.2 Exit codes

Agreed across partspec, netspec and gerberdiff:

    0    satisfied            no differences, every rule passed
    1    violated             a finding about the design
    2    could not tell       the tool could not decide — NOT a finding
    4    environment fault    could not run or read its input — not a verdict either
    64   usage                EX_USAGE: bad arguments

**`2` is the one that carries §2.1's third outcome**, and it is why a caller must not
read "nonzero" as "the design is wrong". `4` and `64` say nothing about the design
either. gerberdiff spells `2` as a third *diff* outcome — `indeterminate` beside
`identical` and `different` — rather than as a verdict, because a differ answers a
different question; the code and its meaning are the same.

Settled 2026-09-06 by adjudications A1, A2 and A3. Before that netspec used `2` for
usage and had no third verdict, and gerberdiff used `2` for a parse error.

**`3` is a domain-gated extension, on §6.1's terms.** partspec and slicelab both
exit `3` for **`empty`**: the run completed, nothing went wrong, and it verified
*nothing* — every requested check passed vacuously because none was requested.
partspec has had it; slicelab adopted the same number for the same idea in D24
(slicelab#16), deliberately rather than coincidentally. Note what agreed and what
did not: slicelab is a driver, so its §6.1 words diverge on purpose (`sliced` and
`refused`, not `pass` and `fail`) while the *code* is shared. The exit map is the
part §5 makes a stable surface; the vocabulary above it is scoped to members that
adjudicate, which is why §6.3's count of three is unchanged by this.

`3` is not in the table above because netspec and gerberdiff do not have it, and
that is a decision rather than a gap. `empty` exists where a run's scope is
supplied by the file under test, so a file can ask for nothing; netspec's scope
is the board's netlist, which is not a request the author can leave blank. Adding
`3` to the common core would say netspec is missing something it chose not to
have — the same error §6.1 warns about for `approximate`.

The distinction `3` buys over `1` is the one that decided it. `1` asserts *the
tool established the design is wrong* — slicelab spells it `refused`, partspec
`fail` — and over zero requested keys nothing was established, so `1` would claim
a cause the tool never found. `0` would claim a verification that did not happen,
which is §2.1's silence-reads-as-success in the one place it is hardest to see:
the run really did succeed, and the file really is the first one anyone writes.

netspec's objection is recorded and is not overruled: a caller that only asks
"did this verify anything at all" can branch on a report field instead of a code.
slicelab's D24 carries the supersede condition in those terms — if after 20 real
files nobody has branched on `3`, it folds into `refused` and this note goes. The
measurement decides it, not the argument.

### 6.3 Open adjudications

Real conflicts between shipped members are recorded rather than resolved, because
resolving one changes released behaviour and that is a decision with an owner.

**They live at <https://heibench.com/adjudications.html>**, which is canonical for
them. **None are open today**, for the first time: A1 and A2 were settled in netspec
0.9.0 (its `docs/DECISIONS.md` D26) and A3 in gerberdiff `0685cde`. All three
verification members now answer on the same exit codes — `0` satisfied, `1` violated,
`2` could not tell, `4` environment fault, `64` usage — and each can say *could not
tell* in its report, gerberdiff as a third diff outcome rather than a verdict.

That agreement is the point of recording adjudications at all, so treat an empty list
as a state to defend rather than a task completed: the next member to ship a verb, or
the next tool to join, is where it drifts.

**Do not "fix" a member to match that page without an issue and a decision entry.**
The vocabulary follows the tools; the tools do not silently follow the vocabulary.

---

## 7. Evidence

**Reproduce before reporting.** Inferring a failure mode from reading code is a
guess, and a wrong guess sends the fix in the wrong direction — or hides that
the real behaviour is worse. Where this document states a finding it has not
reproduced, it says so. Do the same.

**Never state a number you did not produce.** A figure that reaches a spec, a
README, a commit message or an issue carries the command that produced it. An
estimate is fine when labelled as one and misleading when presented as a
measurement.

**Verify against the tool, not its roadmap.** Upstream documentation describes
intentions; upstream source describes behaviour.

**Check metadata before you build on it.** A repository's description, language
and topics are not what it is. This org's own founding survey characterised a
fork as the author's work and put a decision to the user on that basis. Open the
thing.

**Decisions live in each repo's `docs/DECISIONS.md`, numbered, with the
reasoning that produced them.** Do not relitigate a numbered decision; if it is
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

**Do not write a test that reads a doc, reads the code, and diffs them** — that
is two copies of one fact with a failure report attached; generate the doc
instead. Equally, do not assert that a phrase appears in prose: `assert "five
classes" in README` passes when the README says "five classes in 2019, all of
which failed". A doc test must assert something **executable**.

---

## 9. Licensing

**Per repository, and often not a free choice.** A driver's licence is
frequently constrained by the engine it binds to, and that constraint wins.

    partspec, netspec, gerberdiff     Apache-2.0
    prusaslicer-py, slicelab          Apache-2.0
    orlab                             GPL-2.0 (follows OpenRocket)

Each driver above reaches its engine across a **process boundary**, which does not
propagate a licence, so nothing is compelled and the choice is free. `orlab` is the
exception and the reason this section exists: OpenRocket is reached in-process through
JPype, and GPL-2.0 follows.
Pick Apache-2.0 where the binding leaves the choice open; take what the engine
compels where it does not, and record which case applies in the repo's
`DECISIONS.md`. **There is no org-wide default to apply blindly** — an earlier
draft of this file claimed Apache-2.0 across the org, which was already false.

---

## 10. Escalate, do not decide

Stop and ask rather than proceeding, for:

- anything that reverses a numbered decision in a repository's `DECISIONS.md`
- changing a report schema or an exit code in a released tool
- extracting shared code into a common library or framework across members
- adding a runtime dependency to a tool whose core is dependency-free by design
- naming or describing a private repository anywhere public
- deleting data, force-pushing, or rewriting published history
- transferring a repository, renaming the org, or changing org settings

Everything else: decide, record the reasoning where the next agent will find it,
and keep moving.
