# hardspec

**Continuous inspection for hardware design.**

CI proves the artifact *built*. These tools prove it is *what you declared*.

A hardware design is edited for months by people and, increasingly, by agents.
Every tool that edits one reports on its own arithmetic. Only the domain's own
engine knows what the design actually **is** — so ask it, after every change,
and fail loudly when intent and reality diverge.

## The tools

| | domain | oracle | status |
|---|---|---|---|
| **[partspec](https://github.com/CameronBrooks11/partspec)** | mechanical parts, CAD-as-code | OpenSCAD, OCCT (build123d / CadQuery) | pre-alpha, `pip install partspec` |
| **[netspec](https://github.com/CameronBrooks11/netspec)** | PCB connectivity | `kicad-cli` | pre-alpha, `pip install kicad-netspec` |
| **[gerberdiff](https://github.com/CameronBrooks11/gerberdiff)** | fabrication output (Gerber / Excellon) | the fabrication files themselves | `pip install gerberdiff` |

Each is independent. There is no shared runtime, no framework, and nothing to
adopt in order to use one of them.

*The repositories are moving into this org; the links above point at their
current homes and will keep working either way.*

## The one idea

> **Silence must never read as success.**

A check that could not run, could not reach its evidence, or could not decide
must never be reportable as one that looked and found nothing. So every tool
here answers in at least three states — *satisfied*, *violated*, and **could not
tell** — and the third one never exits `0`.

That sounds obvious. It is the single most-violated property in verification
tooling, including in the tools here, which is why it is written down.

The corollary matters just as much: **an environment fault is not a verdict on
the design.** No engine on `PATH`, a solver that will not start, a file that is
not there — none of those are statements about your board or your part. A CI run
on a machine missing KiCad must never report a design as disproven.

## What belongs here

A tool belongs in hardspec if it:

1. takes a **declaration of intent** — what the design is supposed to be;
2. adjudicates it against an **oracle that owns the truth**, rather than
   reimplementing that oracle's arithmetic; and
3. **never lets *couldn't tell* exit `0`**.

Deliberately out of scope: authoring and design entry, design *review*, and
dependency management. These tools read; they do not write your design.

The org-wide contract for humans and agents working in these repositories is
[AGENTS.md](https://github.com/hardspec/.github/blob/main/AGENTS.md).
