---
name: AeroQual engineering brief
description: Scoped offline engineering evidence flipbook
colors:
  navy: "#0a1322"
  panel: "#121f30"
  raised: "#192a3b"
  rule: "#31465a"
  ink: "#edf4f9"
  muted: "#aebfce"
  cyan: "#73d7e4"
  green: "#83d4b2"
  amber: "#f0c780"
  red: "#f29699"
typography:
  display:
    fontFamily: 'PlexBrief, "Segoe UI", sans-serif'
    fontSize: "clamp(40px, 3.8vw, 72px)"
    fontWeight: 500
    lineHeight: 1.06
    letterSpacing: "-0.03em"
  headline:
    fontFamily: 'PlexBrief, "Segoe UI", sans-serif'
    fontSize: "clamp(27px, 2.5vw, 42px)"
    fontWeight: 500
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  body:
    fontFamily: 'Aptos, "Segoe UI", Arial, sans-serif'
    fontSize: "16px"
    lineHeight: 1.5
rounded:
  control: "6px"
  boundary: "8px"
  panel: "12px"
spacing:
  narrow-gutter: "20px"
  panel: "24px"
  gutter: "clamp(22px, 3.4vw, 64px)"
components:
  button-primary:
    backgroundColor: "{colors.cyan}"
    textColor: "{colors.navy}"
    rounded: "{rounded.control}"
    padding: "9px 16px"
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "24px"
---

# Design System: AeroQual engineering brief

## Overview

**Creative North Star: "Engineering review brief"**

This records the user's professional navy, graphite and cyan direction for `demo/aeroqual_brief.html`
only. It is a separate offline flipbook, not an application rebrand. Literal evidence geometry,
concise conclusions and restrained framing carry the presentation.

**Key Characteristics:**

- Six paginated spreads with persistent method and scenario context.
- Flat tonal surfaces, clear rules and tabular numerical evidence.
- Engineering conclusions with visible interpretation and provenance boundaries.

## Colors

Cyan identifies actions, active navigation and evidence marks. Navy is the canvas; panel and raised
graphite separate surfaces. Ink and muted ink distinguish conclusions from supporting explanation;
rule separates regions. Primitive values are normative in the frontmatter.

Green, amber and red convey favorable, investigation and adverse states. Pair color with written
status and measured evidence. Control limits and customer LSL retain different line treatments.
Print uses white surfaces, dark ink and darker semantic colors for legibility.

## Typography

Display, section titles and verdicts use embedded IBM Plex Sans Medium, exposed as `PlexBrief`.
The generated artifact includes the official IBM license. Body uses the platform sans stack.
The frontmatter records desktop display and headline ramps; h3 is 17px and lead copy is 18px.
At 1050px and below h1 is 44px; at 730px and below h1 is 39px, h2 is 28px and lead is 16px.
Data uses tabular numerals. Body generally stays within 70ch, with decision copy at 53ch.

## Layout

Desktop uses a fluid gutter and a 1920px maximum main width. The opening combines a decision and
strength trace with a six-part scorecard. Final desktop opening footer bottoms were measured at
896.3px in 1440x900 and 993.9px in 1920x1080 viewports.

Decision columns use 1.3fr and 0.9fr with a 44px gap; evidence uses 2.15fr and 0.85fr with a 26px
gap. At 1700px the opening gap becomes 64px. Intermediate layouts change at 1050px. At 730px,
major columns become one column and gutters become 20px. Charts keep a 680px local rail instead
of shrinking their geometry; mobile chart text is 16px and axis labels 14px. Tables scroll locally.
Navigation may scroll horizontally without overflowing the document.

## Elevation & Depth

No shadows. Navy, graphite and raised surfaces plus one-pixel rules convey hierarchy. Page turns
use a restrained 280ms rotation/translation and opacity transition. Reduced-motion preferences
disable animation. The sidecar records exact motion and breakpoint extensions.

## Shapes

Panels and inspectors use 12px corners; controls 6px; interpretation boundaries 8px. Rules are thin
and structural. Charts use literal data geometry; no decorative photographs, textures or illustrations.
Circular status dots accompany text rather than replacing it.

## Components

- **Controls:** cyan primary actions, raised secondary controls and transparent subtle actions;
  general buttons have a 42px minimum height. Hover lightens surfaces. Cyan 3px focus outlines remain visible.
- **Selectors:** transparent underlined fields with visible labels and persistent selection.
- **Navigation:** six links with muted defaults and a cyan underline on the current section;
  Previous/Next controls show position and disable at the ends.
- **Scorecard:** six measurements with separator rules and tabular numbers. Unstable input withholds
  capability; descriptive Cpk/Ppk are explicitly labeled.
- **Evidence:** five chart views, hover/focus point details, source-build inspection and backend
  recommendations. Chart tabs expose selected state; focused points gain a contrasting stroke.
- **Comparison:** two independent scenario selectors. Charts explicitly say "Independent y-axis"
  and retain separate full-log control limits.
- **Appendix and print:** expandable technical detail preserves source revision, source/data hashes,
  offline snapshot provenance and API/core parity context. Print produces six light-background spreads.

## Do's and Don'ts

- **Do** keep provenance and synthetic-data context inspectable offline.
- **Do** preserve keyboard focus, reduced motion and local mobile chart scrolling.
- **Do** distinguish control limits, customer LSL and descriptive capability values.
- **Don't** introduce decorative imagery or page-curl textures into this brief.
- **Don't** imply causality, approved operating windows, flightworthiness or release authority.
- **Don't** extend this contract to the existing app, tutorial or other task-owned files.

The scoped JSON sidecar is `demo/brief_source/design.json`; no root design system is introduced.
H-16 ownership stays limited to its named new brief/source/test artifacts and its own ledger entry.
