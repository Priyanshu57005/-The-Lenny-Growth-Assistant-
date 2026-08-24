# Design & UI/UX Specification: The Lenny Growth Assistant

## 1. UI Architecture & Layout Principles
The Lenny Growth Assistant interface is built following modern AI SaaS standards (inspired by Claude Artifacts and OpenAI ChatGPT):

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ [≡] Lenny Growth Assistant      Engine: OLLAMA (llama3.2)  [Canvas Tab] │
├─────────────┬─────────────────────────────────────┬─────────────────────┤
│             │                                     │                     │
│  Sidebar    │            Chat Workspace           │   Artifact Canvas   │
│             │                                     │                     │
│  [+ New]    │ User: What is the LNO Framework?    │ ┌─────────────────┐ │
│             │ Assistant: Grounded Answer...       │ │  Markdown /     │ │
│  Sessions   │ [Source: Shreyas Doshi (95%)]       │ │  Sandboxed HTML │ │
│  - PM Fit   │                                     │ │  Preview        │ │
│  - PLG Essay│ User: Create interactive pricing... │ │                 │ │
│             │ Assistant: Generated HTML Artifact  │ └─────────────────┘ │
│             │ [View Artifact Button]              │ [Copy] [Download]   │
│             ├─────────────────────────────────────┤                     │
│             │ [ Ask question or request artifact ]│                     │
└─────────────┴─────────────────────────────────────┴─────────────────────┤
```

## 2. Aesthetics & Design Tokens
- **Color Palette**: Dark mode base (`#0b0f17`), card surface (`#0d1320`), sidebar (`#080c14`), primary brand blue (`#2563eb`), grounded accent amber (`#f59e0b`), artifact purple (`#9333ea`).
- **Typography**: Primary font `Inter`, Code font `JetBrains Mono`.
- **Micro-Interactions**: Hover states on session list items, animated spinner during agent retrieval, transition animations on split canvas opening.

## 3. Key Component Interaction Specs

### Sidebar
- Displays session list sorted by `updated_at` descending.
- Hovering session item reveals delete trash icon.
- Bottom footer contains active LLM provider toggle buttons with real-time health status dots.

### Chat Stream & Citation Cards
- User messages styled in blue user bubbles.
- Assistant messages styled in structured markdown.
- Grounded citations collapsible accordion showing guest name, episode title, match score percentage, and source text snippet.

### Artifact Canvas
- Desktop: Split side-by-side (50% chat / 50% canvas).
- HTML View: Toggles between live sandboxed Preview mode and raw syntax-highlighted Code mode.
- Action Bar: Copy code button with success feedback, download file button, full-screen toggle, close panel button.

## 4. Accessibility & Responsiveness
- Accessible contrast ratios (WCAG AA compliant).
- Responsive breakpoint at `lg` (1024px): On mobile screens, sidebar collapses to top drawer and artifact canvas renders full screen overlay with close toggle.
