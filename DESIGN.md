# Design System Strategy: Architectural Clarity & High-Tactility Utility

## 1. Overview & Creative North Star: "The Brutalist Sanctuary"
This design system moves beyond the standard utility of a timer app to create an experience of **Architectural Clarity**. Our "Creative North Star" is **The Brutalist Sanctuary**: a space where high-contrast, oversized elements provide unapologetic accessibility, yet feel premium through intentional asymmetry and tonal depth.

Unlike typical apps that rely on thin lines and subtle greys, this system utilizes massive typographic scales and bold color blocks to guide the user’s focus. We break the "template" look by treating the screen as a physical desk—where elements aren't just placed, they are "settled" into a hierarchy of surfaces. This is not just a high-contrast theme; it is an editorial statement on legibility and intentionality.

---

## 2. Colors & Surface Philosophy
The palette is rooted in WCAG AAA compliance, but we avoid the "clinical" look of raw black-and-white through a sophisticated range of surface tiers.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders to section content. Boundaries must be defined solely through background color shifts. For example, a `surface-container-low` section should sit on a `surface` background to create a crisp, modern edge without the visual noise of a stroke.

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked, fine-paper layers.
- **Base Layer:** `surface` (#f7f9ff)
- **Primary Content Area:** `surface-container-low` (#f0f4fc)
- **High-Interaction Cards:** `surface-container-lowest` (#ffffff)
- **Active Navigation/Overlays:** `surface-container-high` (#e4e8f0)

### The "Glass & Gradient" Rule
To elevate the experience, use **Glassmorphism** for floating timers or persistent controls. Use a semi-transparent `surface` color with a `backdrop-filter: blur(20px)`.
*   **Signature Texture:** Main Call-to-Actions (CTAs) should utilize a subtle linear gradient from `primary` (#0051ae) to `primary_container` (#0969da) at a 135-degree angle. This adds "soul" and depth to the high-contrast aesthetic.

### Session Color Coding (The Semantic Engine)
- **Meditation:** Use `tertiary` (#0a6148) and `tertiary_container` (#2e7a5f) to create a grounding, earthen atmosphere.
- **Gratitude:** Use `secondary` (#9b4500) and `secondary_container` (#fd8a42) to radiate warmth and presence.
- **Deep Work:** Use `primary` (#0051ae) and `primary_container` (#0969da) to signal focus and authority.

---

## 3. Typography: The Editorial Voice
We use **Mona Sans VF** and **Inter** to create a high-contrast typographic hierarchy that prioritizes rapid scanning and extreme legibility.

*   **Display (Display-LG, 3.5rem):** Reserved exclusively for the active timer countdown. Use a tight letter-spacing (-0.02em) to give it a "monumental" feel.
*   **Headline (Headline-LG/MD):** Used for session titles. These should feel architectural and bold, anchoring the top of the layout.
*   **Body (Body-LG):** Minimum size for any descriptive text to ensure accessibility.
*   **Labels (Label-MD):** Used for secondary metadata. Despite the small size, ensure they utilize the `on-surface-variant` (#424753) for maximum contrast against light backgrounds.

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are largely discarded in favor of **Tonal Layering**.

*   **The Layering Principle:** Depth is achieved by "stacking." A `surface-container-lowest` card placed on a `surface-container-low` background creates a natural, soft lift.
*   **Ambient Shadows:** If a floating action button (FAB) requires a shadow, it must be extra-diffused.
    *   *Shadow Property:* `0px 24px 48px rgba(23, 28, 34, 0.06)` (A tinted version of `on-surface`).
*   **The "Ghost Border" Fallback:** If a container absolutely requires a boundary for accessibility (e.g., in a complex list), use the `outline-variant` (#c2c6d6) at **15% opacity**. Never use 100% opaque borders.

---

## 5. Components

### Primary Action Buttons (The "Touch-First" Standard)
*   **Sizing:** Minimum height of **64dp** for primary actions (Start/Stop).
*   **Radius:** Use `xl` (0.75rem) for a modern, architectural feel.
*   **Color:** `primary` (#0051ae) with `on-primary` (#ffffff) text.
*   **Interaction:** On press, shift to `primary_container`.

### The Session Card
*   **Style:** No borders. Use `surface-container-low`.
*   **Layout:** Asymmetric. The time remaining sits in the top-right in `display-sm`, while the session name sits bottom-left in `headline-sm`.
*   **Separation:** Never use divider lines. Use **24px - 32px of vertical whitespace** to separate cards.

### Input Fields
*   **Structure:** A "Boxless" approach. Use a `surface-container-highest` background with a 2px bottom-bar in `primary` when focused.
*   **Text:** Ensure the input text uses `headline-sm` to maintain the oversized aesthetic.

### Additional Component: The "Progress Horizon"
*   A custom progress bar that spans the full width of the screen, using a gradient from `primary` to `tertiary` (depending on session type). It should be at least 12dp thick to serve as a visual anchor.

---

## 6. Do’s and Don’ts

### Do
*   **Do** use extreme whitespace (32dp+) to separate major functional groups.
*   **Do** use `ui-monospace` for timer digits to prevent "jittering" as numbers change.
*   **Do** leverage the high-contrast `on-surface` (#171c22) for all critical information.
*   **Do** ensure all touch targets for navigation are at least 48dp.

### Don't
*   **Don't** use 1px solid lines or "dividers" to separate content.
*   **Don't** use grey text that falls below WCAG AAA contrast ratios. If in doubt, use `#171c22`.
*   **Don't** use standard "drop shadows" that look muddy. Stick to tonal shifts or highly diffused ambient glows.
*   **Don't** clutter the screen with icons. Let the oversized typography do the work.