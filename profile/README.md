<img src="https://raw.githubusercontent.com/heibench/.github/main/assets/heibench-mark.png"
     alt="" width="96" height="96">

# heibench

**Hardware Engineering Integration bench.**

*Drive the engine. Check the result.*

Engineering engines — OpenRocket, PrusaSlicer, KiCad, OpenSCAD, OCCT — are built
for a person sitting at a GUI. Two things follow, and the second is the one that
bites.

A program cannot drive them well. Every one has a CLI or a binding, and every one
of those is version-skewed, undocumented in places, and shaped around a human
who will notice when something looks wrong.

**And a program cannot look at the result.** You catch a bad render by glancing
at it. A script does not glance. Neither does an agent. So a tool that returns a
plausible-looking artifact and says nothing is not merely unhelpful — it is
indistinguishable from a tool that worked, and everything downstream inherits
the mistake.

heibench does those two things and nothing else: it puts engineering engines
under program control, and it adjudicates what they produce against declared
intent.

## The two layers

**Drive** — put the engine under program control: headless, scriptable,
version-aware, deterministic.

| | engine |
|---|---|
| **[orlab](https://github.com/heibench/orlab)** | OpenRocket, via JPype — load `.ork`, run simulations, extract time series and flight events |
| **[prusaslicer-py](https://github.com/heibench/prusaslicer-py)** | PrusaSlicer, via its CLI — slice a model and get back a verified artifact, on PATH or as a Flatpak |

**Verify** — adjudicate an artifact against declared intent.

| | domain | oracle |
|---|---|---|
| **[partspec](https://github.com/heibench/partspec)** | mechanical parts, CAD-as-code | OpenSCAD, OCCT (build123d / CadQuery) |
| **[netspec](https://github.com/heibench/netspec)** | PCB connectivity | `kicad-cli` |
| **[gerberdiff](https://github.com/heibench/gerberdiff)** | fabrication output (Gerber / Excellon) | the fabrication files themselves |

Each tool is independent — no shared runtime, no framework, nothing to adopt in
order to use one.

## What belongs here

A tool belongs if **both** hold:

1. It puts an engineering engine or artifact under **program control** —
   headless, scriptable, deterministic, no human in the loop.
2. It is **honest about what it established** — a structured result, a
   meaningful exit code, never reporting success it did not verify and never
   substituting a plausible result for a real one.

The second is not a quality preference. It is the condition that makes the first
worth anything, and it is violated constantly — including ten recorded times, in
five unrelated domains, in this author's own code, two of them still open. The
record is at [heibench.com/silence.html](https://heibench.com/silence.html).

## What does not

Authoring and design generation, language runtimes, slicer post-processing,
dependency management, and machine control at runtime are not within the scope of this org.

heibench is the design-time middle: **operate the tool, and know whether to
believe the output.**
