---
name: Obsidian Precision CUI
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#c2c6d4'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#8c919d'
  outline-variant: '#424752'
  surface-tint: '#aac7ff'
  primary: '#aac7ff'
  on-primary: '#002f65'
  primary-container: '#6ba3ff'
  on-primary-container: '#003875'
  inverse-primary: '#135db4'
  secondary: '#5ddda5'
  on-secondary: '#003824'
  secondary-container: '#04a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb3ae'
  on-tertiary: '#66060f'
  tertiary-container: '#ff7b76'
  on-tertiary-container: '#731217'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d7e3ff'
  primary-fixed-dim: '#aac7ff'
  on-primary-fixed: '#001b3e'
  on-primary-fixed-variant: '#00458e'
  secondary-fixed: '#7bfac0'
  secondary-fixed-dim: '#5ddda5'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ae'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#862122'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
  surface-canvas: '#121212'
  surface-panel: '#181818'
  surface-raised: '#1f1f1f'
  surface-muted: '#242424'
  surface-sunk: '#0e0e0e'
  border-hairline: '#2b2b2b'
  border-subtle: '#222222'
  border-focus: '#55adff'
  text-primary: '#f2f2f2'
  text-secondary: '#b4b4b4'
  text-muted: '#8c8c8c'
  status-warning: '#f2bd68'
  status-info: '#7cc4f0'
  series-branch-1: '#73aff1'
  series-branch-2: '#e7936c'
  series-branch-3: '#5ac299'
  series-branch-4: '#a3a0f1'
  series-branch-5: '#d1a24f'
  series-branch-6: '#e18cb5'
typography:
  headline-lg:
    fontFamily: Geist
    fontSize: 36px
    fontWeight: '500'
    lineHeight: 40px
    letterSpacing: -0.025em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 26px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '500'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-sm:
    fontFamily: Geist
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 28px
    letterSpacing: -0.015em
  title-md:
    fontFamily: Geist
    fontSize: 17px
    fontWeight: '500'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 23px
    letterSpacing: '0'
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: '0'
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: '0'
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 15px
    letterSpacing: 0.04em
  code-base:
    fontFamily: JetBrains Mono
    fontSize: 12.5px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: '0'
  code-metric:
    fontFamily: JetBrains Mono
    fontSize: 15px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 0.75rem
  gutter-desktop: 1rem
  margin: 1rem
  margin-desktop: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

The design system embodies a calm, perceptually calibrated, hardware-grade aesthetic engineered specifically for high-velocity software engineering, terminal-centric workflows, and desktop Git repository management. Inspired by precision audio hardware, high-end code editors (Zed, Linear), and modern terminal user interfaces (LazyGit, Nexa), the experience emphasizes tactile feedback, hyper-dense spatial efficiency, and non-distracting visual stillness.

The visual theme adheres to **Minimalist Technical Precision**:
- Depth is achieved primarily through dark, neutral value steps and razor-sharp 1px hairline dividers rather than aggressive blurs or loud drop shadows.
- Micro-interactions feature crisp, instant mechanical feedback (`140ms cubic-bezier(0.22, 1, 0.36, 1)`) with zero unnecessary motion or gratuitous decoration.
- Vibrant chromatic accents are reserved strictly for semantic state (additions, deletions, branch topological lanes, active selections), leaving interface chrome quiet, balanced, and receding into the background.

## Colors

The color palette is calibrated in uniform perceptual lightness intervals to preserve legibility across high-density developer views. The foundation relies on a stacked charcoal progression from the sunken terminal well (`#0e0e0e`) and canvas (`#121212`) up through panel (`#181818`), raised drawer (`#1f1f1f`), and muted header (`#242424`) levels.

Structural separation uses 1px hairline borders (`#2b2b2b` and `#222222`) rather than heavy drop shadows. Accent colors are deployed with mathematical discipline:
- **Primary (`#6ba3ff`)**: Focused interactions, active tree selections, primary action triggers, and active commits.
- **Secondary / Success (`#55d69f`)**: Staged changes, additions, passing checks, and fast-forward statuses.
- **Tertiary / Danger (`#f2716c`)**: Staged deletions, unstaged conflicts, merge failures, and destructive operations.
- **Warning (`#f2bd68`)**: Unstaged modifications, detached HEAD states, and dirty working trees.
- **Branch Topology (`series-branch-1` through `6`)**: Calibrated to identical perceived lightness and saturation to prevent any branch lane from overpowering neighboring topology tracks.

## Typography

The typography architecture balances structural UI clarity with technical data density. 

- **Geist** governs application titles, modal headers, and window navigation bars with tight negative tracking, conveying contemporary precision.
- **Inter** powers primary body copy, toolbars, metadata labels, and tree listings. OpenType features `cv11` (single-storey 'a') and `ss01` (disambiguated '1', 'I', 'l') are active to prevent misreading at compact desktop sizes.
- **JetBrains Mono** anchors all telemetry, commit SHAs, branch names, file diff viewports, keybindings, and inline status badges. 

Tabular figures (`tnum`) are enforced on all monospace and label roles to guarantee vertical column alignment across changing numerical metrics.

## Layout & Spacing

The layout is built around a fixed-fluid multi-pane workbench optimized for wide desktop displays, while seamlessly reflowing onto compact viewports:
- **Desktop (>= 1200px)**: A 3-pane orchestration with a fixed 268px left repository/branch explorer, a flexible fluid center commit history/graph lane, and a 340px right-hand staging/inspector panel. Top toolbars remain locked at a compact 36px height.
- **Tablet (860px - 1199px)**: Inspector collapses into a toggleable slide-over drawer; file trees remain visible alongside the main diff view with gutters tightened to 12px.
- **Mobile / Compact (< 860px)**: Panes stack into single-view tabs (Branches, Commit Log, Diff View, Staging). Outer margins compress to 16px (`margin`).

All component padding, item heights, and gaps snap strictly to a 4px base rhythm. Dense data grids, file trees, and commit rows use `space-xs` (4px) and `space-sm` (8px) internal padding, ensuring high data density without feeling cramped.

## Elevation & Depth

Visual hierarchy uses a flat, layered-tonal approach paired with precision hairline frames:
- **Baseline Surface (`surface-canvas` #121212)**: The desktop shell backdrop.
- **Panels & Sidebars (`surface-panel` #181818)**: Delineated from canvas via 1px solid `#2b2b2b` border lines. Zero drop shadows.
- **Recessed Wells (`surface-sunk` #0e0e0e)**: Applied to diff viewers, code blocks, and terminal panels to create optical depth without blur.
- **Raised Dialogs & Overlays (`surface-raised` #1f1f1f)**: Quick-open palettes, branch switchers, and context menus use a crisp ambient shadow (`0 14px 36px -4px rgba(0,0,0,0.40), 0 1px 3px rgba(0,0,0,0.24)`) bounded by a 1px `#2b2b2b` border.
- **Focus Indicators**: Instead of diffuse glows, keyboard-navigated elements trigger a high-visibility, crisp 2px solid `#55adff` outline with a 2px offset.

## Shapes

The interface utilizes concentric, mathematically proportional corner radii to maintain visual discipline across nested desktop elements:
- Outer panels and card frames use `rounded-lg` (16px/1rem).
- Interactive inputs, buttons, and command rows use `rounded` (8px–10px/0.5rem).
- Micro-badges, keycap hints, and tree item hover states use `rounded-sm` (6px/0.375rem).
- Pills and full circular states are reserved exclusively for avatar initials and live presence indicators. Controls and action triggers retain their crisp, structural rectangular identity.

## Components

### Buttons & Action Controls
- **Primary**: Solid `#6ba3ff` background with `#0b1526` bold text. On hover, shifts to `#a4c7ff`. Active state responds with a subtle `transform: scale(0.98)` tactile press.
- **Secondary / Ghost**: `#181818` background with a 1px `#2b2b2b` hairline border and `#f2f2f2` text. Hover upgrades the border to `#676767` with `#1f1f1f` fill.
- **Danger**: Recessed `#f2716c` tint (`rgba(242, 113, 108, 0.12)`) with `#f2716c` border and text.
- **Heights**: Compact toolbar triggers are 30px high; modal CTAs are 36px high.

### Badges, Status Chips & Keycaps
- **Status Badges**: 20px height, 6px radius, `JetBrains Mono` 11px uppercase. Composed of a 12% alpha background fill matching the semantic tone (`#55d69f` for staged, `#f2bd68` for modified, `#f2716c` for deleted) and a matching 1px border.
- **Keycap Badges**: `#242424` fill, `#2b2b2b` border, 4px radius, 11px monospace typography displaying shortcut combinations (e.g., `⌘K`, `⇧P`).

### Input Fields & Search Bars
- Standard 34px height, `#181818` background, 1px `#2b2b2b` border, and `#f2f2f2` text with `#8c8c8c` placeholder.
- Focus triggers an immediate 1px border shift to `#55adff` and a 2px offset focus ring.
- Integrated search inputs display embedded right-aligned keycap badges.

### Lists & Tree Views
- Git branch and file tree items feature 28px row heights, 6px hover radiuses, and 12px indent guides (`border-left: 1px solid #222222`).
- Active items receive a `#1f1f1f` background, a 2px left-edge accent line in `#6ba3ff`, and primary alabaster typography.

### Checkboxes & Toggle Radios
- 16x16px boxes with 4px corner radius, `#181818` background, and `#2b2b2b` border. Checked states transition to `#6ba3ff` fill with `#0b1526` checkmarks.

### Cards & Code Diff Panels
- Staged/unstaged files and diff comparisons are hosted in `#0e0e0e` recessed wells framed with `#2b2b2b`.
- Unified diff lines have a full-bleed row height of 22px in `JetBrains Mono`, featuring `#55d69f` (+12% background tint) for insertions and `#f2716c` (+12% background tint) for removals, accompanied by 1-character gutter markers (`+`, `-`).