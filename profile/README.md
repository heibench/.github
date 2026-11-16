<img src="https://raw.githubusercontent.com/heibench/.github/main/assets/heibench-mark.png"
     alt="" width="96" height="96">

# heibench

**Open tools for scientific and technical workflows.**

*Drive the engine. Check the result.*

The engines of technical work — OpenRocket, PrusaSlicer, KiCad, OpenSCAD, OCCT,
Zotero, MediaWiki — are built for a person sitting at a GUI or a browser. Two
things follow, and the second is the one that bites.

A program cannot drive them well. Every one has a CLI or a binding, and every one
of those is version-skewed, undocumented in places, and shaped around a human
who will notice when something looks wrong.

**And a program cannot look at the result.** You catch a bad render by glancing
at it. A script does not glance. Neither does an agent. So a tool that returns a
plausible-looking artifact and says nothing is not merely unhelpful — it is
indistinguishable from a tool that worked, and everything downstream inherits
the mistake.

heibench does those two things and nothing else: it puts those engines under
program control, and it adjudicates what they produce against declared intent. An
engine is whatever owns the truth about the artifact — a CAD kernel, a slicer,
KiCad, a reference library, a wiki's revision history.

## The two layers

**Drive** — put the engine under program control: headless, scriptable,
version-aware, deterministic. A driver may write a design, as long as the engine
judges the result.

| | engine |
|---|---|
| **[orlab](https://github.com/heibench/orlab)** | OpenRocket, via JPype — load `.ork`, run simulations, extract time series and flight events |
| **[prusaslicer-py](https://github.com/heibench/prusaslicer-py)** | PrusaSlicer, via its CLI — slice a model and get back a verified artifact, on PATH or as a Flatpak |
| **[slicelab](https://github.com/heibench/slicelab)** | PrusaSlicer and OrcaSlicer — declare a small configuration delta, and get back G-code plus a lock recording exactly what the engine resolved. *Pre-alpha: the contract and its decisions, no verb implemented yet.* |
| **[boardwright](https://github.com/heibench/boardwright)** | KiCad, via `kicad-cli` and its IPC API — generate a board from a short Python description, or edit an existing board or schematic in place, and report success only when KiCad's own ERC, DRC and netlist agree |
| **[zotgo](https://github.com/heibench/zotgo)** | Zotero 7+, via its HTTP Local API and the Web API — search, read and export a library, and write through Zotero's own local write API, with a `doctor` that reports what the endpoint can actually do |
| **[wikisync](https://github.com/heibench/wikisync)** | MediaWiki, via its JSON API — pull pages as local wikitext, diff against the pulled baseline, and push back with the wiki's own conflict detection; previews by default and never deletes |

**Verify** — adjudicate an artifact against declared intent.

| | domain | oracle |
|---|---|---|
| **[partspec](https://github.com/heibench/partspec)** | mechanical parts, CAD-as-code | OpenSCAD, OCCT (build123d / CadQuery) |
| **[netspec](https://github.com/heibench/netspec)** | PCB connectivity | `kicad-cli` |
| **[gerberdiff](https://github.com/heibench/gerberdiff)** | fabrication output (Gerber / Excellon) | the fabrication files themselves |

Each tool is independent — no shared runtime, no framework, nothing to adopt in
order to use one.

## What belongs here

A tool belongs if **all three** hold:

1. It puts a scientific or technical engine, service or artifact under
   **program control** — headless, scriptable, deterministic, no human in the
   loop.
2. It is **honest about what it established** — a structured result, a
   meaningful exit code, never reporting success it did not verify and never
   substituting a plausible result for a real one.
3. It is **useful beyond one project** — someone who has never seen the work it
   came from can pick it up and use it.

The second is not a quality preference. It is the condition that makes the first
worth anything, and it is violated constantly — including fifteen recorded times,
in five unrelated domains, in this author's own code, thirteen now fixed. The
record is at [heibench.com/silence.html](https://heibench.com/silence.html).

## What does not

Generation that no engine checks, language runtimes, slicer post-processing,
dependency management, and machine control at runtime are not within the scope
of this org, and neither is a framework or a general collection of repositories.
Authoring belongs only as a driver: it writes through the engine, and the engine
decides whether the result stands.

heibench is the middle: **operate the tool, and know whether to believe the
output.**

## The name

heibench was founded on 2026-09-05 as the *Hardware Engineering Integration
bench*, when every member worked on hardware. On 2026-11-15 the scope
widened to open tools for scientific and technical work, with zotgo and wikisync
the first members outside hardware. The name stayed; the expansion was retired.
