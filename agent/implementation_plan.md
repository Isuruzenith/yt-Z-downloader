# Streamline — Professional UI/UX Redesign

## Overview

A complete UI/UX overhaul of the Streamline video downloader, replacing the current functional-but-basic Streamlit interface with a **premium, dark-themed design system** inspired by shadcn/ui, Linear, and Vercel's design language. The redesign focuses on visual hierarchy, micro-interactions, and a polished professional aesthetic while maintaining full yt-dlp feature parity.

---

## Design System Foundation

### Core Principles

| Principle | Implementation |
|-----------|---------------|
| **Visual Hierarchy** | Clear content layering with card depth, section headings, and badge systems |
| **Dark-First** | True black (#0A0A0A) base with layered card surfaces (#111, #1A1A1A, #262626) |
| **Typography** | Geist for UI, Geist Mono for data/code, strict size scale (11px→20px) |
| **Micro-animations** | 150ms transitions on borders, backgrounds, opacity for all interactive elements |
| **Information Density** | Progressive disclosure via accordion panels — power without overwhelm |

### Color Token System

```css
/* Base Palette — shadcn/ui dark extended */
--background:        hsl(0 0% 3.9%);    /* #0A0A0A — true dark */
--foreground:        hsl(0 0% 98%);      /* #FAFAFA — pure white text */
--card:              hsl(0 0% 6%);       /* #111111 — elevated surface */
--card-hover:        hsl(0 0% 8%);       /* #141414 — hover state */
--border:            hsl(0 0% 14.9%);    /* #262626 — subtle borders */
--border-hover:      hsl(0 0% 25%);      /* #404040 — active/focus border */
--muted:             hsl(0 0% 14.9%);    /* #262626 — secondary surfaces */
--muted-foreground:  hsl(0 0% 63.9%);    /* #A3A3A3 — secondary text */
--ring:              hsl(0 0% 83.1%);    /* #D4D4D4 — focus ring */

/* Semantic Colors */
--success:   hsl(142 76% 36%);  /* Green for done/success */
--error:     hsl(0 62.8% 30.6%); /* Red for errors */
--warning:   hsl(38 92% 50%);   /* Amber for warnings */
--info:      hsl(217 91% 60%);  /* Blue for running/active */
```

### Typography Scale

| Element | Font | Size | Weight | Letter-Spacing |
|---------|------|------|--------|---------------|
| Wordmark | Geist | 20px | 700 | -0.025em |
| Section Heading | Geist | 11px | 600 | 0.1em (uppercase) |
| Card Title | Geist | 15px | 600 | normal |
| Body | Geist | 14px | 400 | normal |
| Label/Caption | Geist | 12px | 500 | 0.025em |
| Meta/Stats | Geist Mono | 11px | 400 | 0.04em |
| Code | Geist Mono | 12.5px | 400 | normal |

---

## Screen Designs

### 1. Authentication Page

![Authentication page - centered card with dark theme, Streamline branding, sign in/register tabs](C:\Users\isuru\.gemini\antigravity\brain\dbcd5d05-db1d-45f6-aca9-d0d6102f3fb7\auth_page_design_1775324646108.png)

#### Key Design Decisions
- **Centered card** with `max-width: 400px`, vertically centered on the page
- **Glass-morphism subtle glow** on the card border (`box-shadow: 0 0 80px rgba(255,255,255,0.02)`)
- **Tab-based auth** — Sign In / Register with clean underline indicator
- **Full-width primary button** — white background with bold text, clear CTA
- **Demo mode fallback** — muted help text at bottom for offline usage
- Input fields use **dark surface (#1A1A1A)** with subtle border transition on focus

#### Interaction States
- Focus ring: 2px `hsl(--ring / 0.2)` glow on inputs
- Button hover: `opacity: 0.9` with 150ms ease
- Error states: destructive red border + inline message
- Loading: spinner replaces button text during API call

---

### 2. Download Tab (Main View)

![Download tab - URL input, video preview card, accordion options, command preview, action buttons](C:\Users\isuru\.gemini\antigravity\brain\dbcd5d05-db1d-45f6-aca9-d0d6102f3fb7\download_tab_design_1775324782293.png)

#### Layout Architecture
```
┌─── Navigation Bar ──────────────────────────────────────┐
│  Streamline ←wordmark    user@email.com  [Sign out]     │
├─── Tab Bar ─────────────────────────────────────────────┤
│  [Download●] [Queue (2)] [Formats] [History] [Settings] │
├─── URL Input ───────────────────────────────────────────┤
│  [🔗 Paste]  https://youtube.com/watch?v=...  [Preview] │
├─── Video Preview Card ──────────────────────────────────┤
│  [Thumbnail] Title · Channel · Duration · Views         │
│              [1080p] [720p] [480p] [audio] badges       │
├─── Options Accordion ───────────────────────────────────┤
│  ▼ Format & Quality ──────────── (expanded)             │
│    Container [mp4▼] Quality [1080p▼] Codec [Any▼]       │
│    Format Sort [___] Merge Output [mp4▼]                │
│  ▶ Post-Processing ──────────── (collapsed)             │
│  ▶ Subtitles ────────────────── (collapsed)             │
│  ▶ Video Selection ──────────── (collapsed)             │
│  ▶ Download Behaviour ───────── (collapsed)             │
│  ▶ Network & Authentication ─── (collapsed)             │
│  ▶ SponsorBlock ─────────────── (collapsed)             │
│  ▶ Output Template ──────────── (collapsed)             │
│  ▶ Extractor Options ────────── (collapsed)             │
├─── Command Preview ─────────────────────────────────────┤
│  yt-dlp -f "bestvideo[height<=1080]+bestaudio" \        │
│    --embed-metadata --embed-thumbnail \                  │
│    "https://..."                           [📋 Copy]    │
├─── Action Buttons ──────────────────────────────────────┤
│  [Preview Info] [List Formats] [    ⬇ Download    ]     │
└─────────────────────────────────────────────────────────┘
```

#### Key Improvements Over Current
1. **Video Info Preview Card** — shows thumbnail + metadata before downloading
2. **Progressive disclosure** — 9 accordion sections hide complexity until needed
3. **Live command preview** — updates reactively as options change
4. **Resolution badges** — from fetched format data after preview
5. **Format selector string** — shows computed yt-dlp format string for power users

#### Accordion Section Design
- Sections labeled with human-friendly names (not "Section A", "Section B")
- Each section has an icon prefix: `🎬 Format & Quality`, `⚡ Post-Processing`, `💬 Subtitles`
- Expanded section has smooth card-like content area with consistent padding
- Two-column grid layout inside each section for compact yet readable controls

---

### 3. Queue Tab

![Queue tab - active download cards with progress bars, stats, and cancel buttons](C:\Users\isuru\.gemini\antigravity\brain\dbcd5d05-db1d-45f6-aca9-d0d6102f3fb7\queue_tab_design_1775324867571.png)

#### Job Card Design
```
┌─ Job Card ──────────────────────────────────────────────┐
│  Video Title Here                          ◉ running    │
│  Channel Name · mp4 · 1080p                            │
│  ████████████████████░░░░░░░░░  72.4%                  │
│  ↓ 3.2 MB/s · ETA 0:23 · 234 MB / 324 MB              │
│                                    [Pause] [Cancel]     │
└─────────────────────────────────────────────────────────┘
```

#### Key Features
- **Status badges** with semantic colors: blue (running), gray (queued), green (done), red (error)
- **Thin progress bar** — 6px height with rounded caps, white fill on dark track
- **Real-time stats** in Geist Mono — speed, ETA, bytes downloaded/total
- **Auto-refresh** every 1.5s when jobs are running (with countdown indicator)
- **Empty state** — centered icon + message when queue is clear

---

### 4. Formats Inspector Tab

![Formats tab - URL input, data table with video and audio formats, filters](C:\Users\isuru\.gemini\antigravity\brain\dbcd5d05-db1d-45f6-aca9-d0d6102f3fb7\formats_tab_design_1775325079861.png)

#### Key Features
- **Dedicated format inspection** without needing to download
- **Filter toggle** — All / Video Only / Audio Only radio group
- **Sort options** — by resolution, bitrate, size, codec
- **Monospace data table** — clean grid with alternating row hints
- **"Apply to Download Tab"** — carry format ID back to download configuration

---

### 5. History Tab

![History tab - search, filters, download cards with status, error details, pagination](C:\Users\isuru\.gemini\antigravity\brain\dbcd5d05-db1d-45f6-aca9-d0d6102f3fb7\history_tab_design_1775325209204.png)

#### Key Features
- **Search bar** — filter by title or URL, client-side instant filtering
- **Status filter chips** — multiselect done/error/cancelled
- **History cards** — similar to queue cards but with date timestamps and file paths
- **Error expansion** — expandable error details with log snippet
- **Re-download** — pre-fills Download tab with same URL + options
- **Pagination** — 20 items per page with prev/next navigation

---

### 6. Settings Tab

![Settings tab - cookie auth, defaults, yt-dlp info, session management](C:\Users\isuru\.gemini\antigravity\brain\dbcd5d05-db1d-45f6-aca9-d0d6102f3fb7\settings_tab_design_1775325359908.png)

#### Settings Sections

| Section | Content |
|---------|---------|
| **Cookie Auth** | Upload cookies.txt, load from browser, bookmarklet, status indicator |
| **Default Options** | Pre-fill format, quality, output dir, embed toggles, output template |
| **Download Presets** | Named preset management with edit/delete, import/export JSON |
| **yt-dlp Info** | Version display, ffmpeg/ffprobe/aria2c availability, update buttons |
| **Session & Account** | User stats (total/completed jobs), sign out, delete account |
| **Power Mode** | Raw yt-dlp arguments editor with allowlist enforcement |

---

## Component Library

### Reusable Primitives

| Component | Styling | Usage |
|-----------|---------|-------|
| `sl-card` | `bg-card border-border rounded-[--radius] p-4` | All content cards |
| `sl-badge` | Pill shape, semantic color variants, Geist Mono 11px | Status, format, quality tags |
| `sl-section` | Uppercase 11px, muted, decorative line after | Section headings |
| `sl-code-preview` | Geist Mono 12.5px, card bg, border, `pre-wrap` | Command preview, code blocks |
| `sl-job-card` | Card with hover border glow, title/meta/progress slots | Queue and history items |
| `sl-empty-state` | Centered icon + title + subtitle, muted colors | Empty tab states |
| `sl-wordmark` | Geist Bold 20px, -0.025em tracking | Brand identity |
| `sl-progress-detail` | Geist Mono 11px, flex row with gap | Speed/ETA/size stats |

### Badge Variants

| Variant | Background | Text | Border | Usage |
|---------|-----------|------|--------|-------|
| `default` | `--secondary` | `--secondary-fg` | none | Format, quality, neutral info |
| `success` | `hsl(142 76% 10%)` | `hsl(142 76% 60%)` | `hsl(142 76% 20%)` | Done, connected |
| `error` | `hsl(0 62.8% 30.6% / 0.15)` | `hsl(0 80% 65%)` | `--destructive` | Error, failed |
| `warning` | `hsl(38 92% 10%)` | `hsl(38 92% 60%)` | `hsl(38 92% 20%)` | Playlist, caution |
| `running` | `hsl(217 91% 10%)` | `hsl(217 91% 65%)` | `hsl(217 91% 20%)` | Active, downloading |

---

## User Review Required

> [!IMPORTANT]
> **Accordion Section Naming**: The current implementation uses "Section A: Format & Quality", "Section B: Post-Processing" etc. The redesign proposes using human-friendly names with emoji icons instead (e.g., "🎬 Format & Quality", "⚡ Post-Processing"). Please confirm this approach.

> [!IMPORTANT]
> **Tailwind CDN vs Vanilla CSS**: The PRD specifies Tailwind CDN for complex components. However, since all styling is injected via `st.markdown`, we can achieve the same results with pure CSS custom properties, which is lighter and avoids Tailwind CDN load times (~50KB). Recommendation: **Use vanilla CSS only** (already working in current implementation). Should we keep or remove the Tailwind CDN dependency?

> [!IMPORTANT]
> **Design Fidelity vs Streamlit Constraints**: Some mockup elements (glass-morphism, gradient shimmer on wordmark, hover glow on cards) go beyond what standard Streamlit can render natively. These will be approximated using CSS injection where possible. Are there any specific visual effects you want prioritized?

## Proposed Changes

### Streamlit App

#### [MODIFY] [streamlit_app.py](file:///c:/Projects/Streamline/streamlit_app.py)

**Complete CSS/design system overhaul:**
- Replace all existing CSS with new refined token system
- Add card hover transitions, focus states, glassmorphism effects
- New progress bar design (thinner, rounded, animated shimmer on active downloads)
- Enhanced input/select styling with refined border transitions

**Auth page rebuild:**
- Redesigned centered card with glow effect
- Cleaner tab-based sign in / register flow

**Download tab redesign:**
- Rename accordion sections from "Section A/B/C..." to descriptive names with icons
- Add video preview card with thumbnail display
- Enhance command preview with syntax highlighting
- Better button hierarchy (Download is visually dominant)

**Queue tab improvements:**
- Richer job cards with all progress stats
- Animated progress bar
- Auto-refresh indicator

**History tab enhancements:**
- Search + filter toolbar
- Pagination controls
- Re-download and retry actions

**Settings tab expansion:**
- Multi-section layout with all 6 sections from PRD
- Tool version display with availability indicators
- Preset management UI

---

## Open Questions

1. **Do you want me to implement this redesign now?** This is a significant rewrite of the CSS and rendering functions in `streamlit_app.py`. The backend/API remains unchanged.

2. **Preset Management**: Should presets be stored client-side in `st.session_state` only, or should they persist via the API (`/api/presets/` endpoints which already exist)?

3. **Priority**: Should I implement all tabs at once, or phase it (start with Download + Queue, then add the rest)?

## Verification Plan

### Automated Tests
- Run existing test suite: `pytest tests/ -q --tb=short`
- Ruff lint: `ruff check api/`
- Launch app: `streamlit run streamlit_app.py --server.headless true`

### Manual Verification
- Browser screenshot of each tab after implementation
- Verify demo mode works (backend offline)
- Check all interactive elements respond correctly
