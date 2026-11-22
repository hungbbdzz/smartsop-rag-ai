---
name: Smart Factory Assistant
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#bfc7d2'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#89929b'
  outline-variant: '#3f4850'
  surface-tint: '#93ccff'
  primary: '#93ccff'
  on-primary: '#003351'
  primary-container: '#3198dc'
  on-primary-container: '#002c47'
  inverse-primary: '#006398'
  secondary: '#ffb95f'
  on-secondary: '#472a00'
  secondary-container: '#ee9800'
  on-secondary-container: '#5b3800'
  tertiary: '#ffb3ad'
  on-tertiary: '#68000a'
  tertiary-container: '#ff5451'
  on-tertiary-container: '#5c0008'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#cce5ff'
  primary-fixed-dim: '#93ccff'
  on-primary-fixed: '#001d31'
  on-primary-fixed-variant: '#004b73'
  secondary-fixed: '#ffddb8'
  secondary-fixed-dim: '#ffb95f'
  on-secondary-fixed: '#2a1700'
  on-secondary-fixed-variant: '#653e00'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ad'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#930013'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-lg: 1.5rem
  margin: 1rem
  margin-lg: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system channels an advanced industrial instrumentation aesthetic designed for high-stakes smart manufacturing floors and control rooms. It balances modern operator clarity with high-precision engineering telemetry. The design style blends utilitarian industrial brutalism with modern technical dark-mode precision: structural grids, sharp low-radius corners, luminous status optics, and technical data density.

The atmosphere is focused, Mission-Critical, and strictly authoritative. It avoids playful or consumer-centric soft curves in favor of crisp delineation, tactical telemetry, and rapid visual hierarchy designed to support plant supervisors, maintenance technicians, and automation engineers under demanding physical conditions.

## Colors

The palette is engineered for high legibility on terminal displays and ruggedized field tablets under harsh lighting conditions.

- **Neutral Canvas (`#0f172a`):** Deep industrial slate base providing deep contrast while minimizing glare. Surface hierarchy is built via stratified card levels: Tier 1 cards sit at `#1e293b`, interactive or elevated panels use `#334155`, and active borders hover around `#475569`.
- **Primary / Signal Blue (`#0284c7`):** Represents AI ingestion, retrieval-augmented queries (RAG), and standard system communication. Accompanied by faint alpha glows (`rgba(2, 132, 199, 0.2)`) to indicate active telemetry or computing states.
- **Secondary / Safety Amber (`#f59e0b`):** Dictates cautions, out-of-spec tolerances, pending maintenance SOPs, and system verification flags.
- **Tertiary / Emergency Red (`#ef4444`):** Strictly reserved for factory lockouts, critical equipment faults, E-stop conditions, and security violations.
- **Utility / Status Green (`#10b981`):** Applied for nominal operating parameters, validated calibrations, and closed tickets.

## Typography

The typography architecture uses a strict two-tier pairing: **Inter** handles narrative readability, instruction steps, conversational RAG outputs, and top-level hierarchy; **JetBrains Mono** controls all machine-critical data, including equipment IDs, telemetry timestamps, G-code references, system tags, and step-index badges.

All mono labels enforce uppercase or tabular numeric rendering (`tnum`) to maintain visual alignment across dense diagnostic grids. Headlines use tight letter-spacing (`-0.02em`) to assert an authoritative, precision-engineered presence.

## Layout & Spacing

Layouts follow a structured, multi-column fluid grid tailored for widescreen line terminals and rugged handheld tablets:
- **Desktop / Control Console (≥1200px):** 12-column layout with 24px gutters and 32px margins. Splits systematically into a persistent telemetry sidebar (3 cols), primary SOP workspace (6 cols), and contextual RAG assistant stream (3 cols).
- **Tablet / Rugged Field Slate (768px - 1199px):** 8-column layout with 16px gutters and 24px margins. Sidebar condenses into an icon rail, and the RAG assistant switches to a collapsible drawer.
- **Mobile Handheld (<768px):** 4-column layout with 16px gutters and 16px margins. Stacked single-column hierarchy prioritized by urgency.

Components adhere to a 4px baseline grid rhythm to ensure clean alignment between mono data tables and graphical status widgets.

## Elevation & Depth

This system avoids soft, organic dropshadows. Depth is generated through layered surface luminance, crisp technical hairline borders, and localized photon luminescence:

- **Surface Tiers:**
  - Base: `#0f172a` (Machine canvas background)
  - Card / Panel: `#1e293b` (Enclosed diagnostic unit)
  - Floating / Dropdown / Popover: `#334155` (Elevated operational layer)
- **Precision Borders:** 1px solid boundaries using `#334155` on resting states, escalating to `#475569` on hover.
- **Telemetry Glows:** Active statuses employ colored edge-glows rather than traditional shadows:
  - AI Pulse: `0 0 12px rgba(2, 132, 199, 0.35)`
  - Caution Aura: `0 0 12px rgba(245, 158, 11, 0.35)`
  - Critical Alarm: `0 0 16px rgba(239, 68, 68, 0.45)`

## Shapes

Corner radii are kept tight and functional (`roundedness: 1`), providing an industrial feel that nods to milled metal, rack-mounted instrumentation, and hardened touch interfaces:
- Standard elements (inputs, buttons, badges): `0.25rem` (4px).
- Container cards and telemetry panels: `0.5rem` (8px).
- Modal dialogs and critical confirmation shells: `0.75rem` (12px).
- Status LEDs and badge pulse-nodes are the only fully circular components (`rounded-full`).

## Components

### Buttons
- **Primary / Action (AI & Ingestion):** Solid `#0284c7`, text `#ffffff` (`Inter` 600). Hover state shifts to `#0369a1` with a subtle `0 0 8px rgba(2, 132, 199, 0.4)` aura.
- **Industrial Danger / Halt:** Solid `#ef4444`, text `#ffffff` with active red warning ring.
- **Secondary / Equipment Controls:** Surface `#1e293b`, 1px border `#475569`, text `#e2e8f0`. Hover turns background to `#334155`.
- **Target Hit Sizes:** Standard desktop/rugged tablet buttons maintain a minimum 44px tap height for glove accessibility.

### Status Indicators & Glowing Beacons
- Composed of an 8px circular core paired with an animated ping or static radial glow ring (`box-shadow: 0 0 8px currentColor`).
- Green (`#10b981`) indicates nominal status; Amber (`#f59e0b`) flags preventive maintenance required; Red (`#ef4444`) signals fatal line stoppage; Blue (`#0284c7`) represents RAG inference or active query generation.

### Badges & Technical Chips
- Structured with `JetBrains Mono` font (`label-sm`).
- High-contrast framing: Dark translucent background (`rgba(x, y, z, 0.15)`), 1px solid colored border matching the token, and capitalized uppercase text with `0.05em` tracking.

### Cards & Telemetry Containers
- Background `#1e293b`, 1px hairline border in `#334155`.
- Card headers feature an integrated top-bar with monospaced machine identification tags, step counters (e.g., `SOP-409 // STEP 03`), and live connection beacons.

### Inputs & Query Bars
- Background `#0f172a`, border 1px `#334155`, text `#f8fafc`.
- Focus state activates an intense 1px `#0284c7` border and a soft glow (`0 0 0 2px rgba(2, 132, 199, 0.2)`).
- Search/Prompt fields feature a dedicated keyboard shortcut tag (e.g., `[CMD + K]` or `[SCAN]`) styled in `JetBrains Mono`.

### Checkboxes, Steppers & Radios
- Industrial toggle aesthetic: Angular 4px radius box with 1px `#475569` border.
- Selected state fills with `#0284c7` displaying a crisp white micro-tick, optimized for decisive verification during physical lockout-tagout or assembly inspection workflows.