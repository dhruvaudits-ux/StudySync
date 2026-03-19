# The Design System: Engineering Precision & Academic Elegance

This design system is a high-end framework engineered specifically for the next generation of academic administrators. Moving away from the cluttered, "dashboard-in-a-box" aesthetic, this system prioritizes **Cognitive Clarity** and **Atmospheric Depth**. It treats data not as a series of rows, but as an editorial experience where whitespace is a functional tool and hierarchy is conveyed through tonal shifts rather than rigid lines.

---

## 1. Overview & Creative North Star

### The Creative North Star: "The Digital Curator"
The system is built on the philosophy of **The Digital Curator**. Unlike standard admin panels that overwhelm the user with "everything everywhere," this system uses intentional asymmetry and generous breathing room to guide the eye. We lean into the engineering mindset: precision, efficiency, and structural integrity, softened by a premium, human-centric "Editorial" layer.

**The Signature Look:**
*   **Intentional Asymmetry:** Avoid perfectly centered blocks. Use left-aligned, oversized headlines (`display-md`) against right-aligned utility actions to create a dynamic flow.
*   **Overlapping Elements:** Occasionally break the grid. Allow a floating `surface-container-highest` card to subtly overlap a `surface-container-low` header section to create a sense of physical stacking.
*   **Breathing Room:** If you think a section has enough padding, add one more increment from the spacing scale (e.g., move from `8` to `10`).

---

## 2. Colors & Surface Philosophy

This palette balances the analytical "Deep Professional Blue" with the creative "Vibrant Purple," creating a spectrum of productivity.

### The "No-Line" Rule
**Borders are forbidden for sectioning.** To separate the sidebar from the main content or a chart from a stat list, use background shifts. 
*   *Example:* Main Sidebar uses `surface-container-low`, while the Content Canvas uses `surface`. The contrast is felt, not seen.

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked, semi-transparent layers:
1.  **Base Layer:** `surface` (#f8f9ff) - The vast "paper" on which everything sits.
2.  **Sectioning Layer:** `surface-container-low` (#eff4ff) - Large background blocks for grouping related modules.
3.  **Component Layer:** `surface-container-lowest` (#ffffff) - Individual cards. This creates a "lift" effect without needing heavy shadows.

### The Glass & Gradient Rule
*   **Floating Elements:** Modals and dropdowns must use `surface-container-highest` with a `backdrop-blur` of 12px and 80% opacity.
*   **Signature Gradients:** For primary CTAs and Hero Stats, use a linear gradient: `primary` (#004ac6) to `secondary` (#712ae2) at a 135-degree angle. This injects "soul" into the mechanical nature of an admin panel.

---

## 3. Typography: Editorial Authority

We use a dual-sans serif approach to separate "Data" from "Direction."

*   **Headlines (Manrope):** Chosen for its geometric precision and modern flair. Use `display-md` for main page titles to create an editorial feel.
*   **UI & Data (Inter):** The workhorse. Inter provides maximum legibility for dense engineering metrics and complex navigation.

| Level | Token | Font | Size | Weight | Intent |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display** | `display-md` | Manrope | 2.75rem | 700 | Hero metrics or Page titles |
| **Headline** | `headline-sm` | Manrope | 1.5rem | 600 | Major section headers |
| **Title** | `title-md` | Inter | 1.125rem | 500 | Card titles / Modal headers |
| **Body** | `body-md` | Inter | 0.875rem | 400 | Standard reading / Data rows |
| **Label** | `label-sm` | Inter | 0.6875rem | 600 | All-caps, tracked-out metadata |

---

## 4. Elevation & Depth: Tonal Layering

Standard "Drop Shadows" are too aggressive for a premium experience. We use **Ambient Shadows** and **Tonal Lifts**.

*   **The Layering Principle:** Instead of a shadow, place a card (`surface-container-lowest`) on a background (`surface-container-low`). The subtle shift in hex code creates a sophisticated, "flat-depth" look.
*   **Ambient Shadows:** Where a floating effect is vital (e.g., a Top Navbar during scroll), use: `box-shadow: 0 8px 32px rgba(11, 28, 48, 0.06)`. This uses the `on-surface` color at a very low opacity for a natural, soft lift.
*   **Ghost Borders:** If a boundary is required for accessibility, use the `outline-variant` token at 15% opacity. Never use a 100% opaque border.

---

## 5. Components

### Buttons: The Interaction Hierarchy
*   **Primary:** Linear gradient (`primary` to `secondary`). Rounded `lg` (1rem). 
*   **Secondary:** `surface-container-high` background with `on-surface` text. No border.
*   **Tertiary/Ghost:** No background. `primary` text. Use for low-priority actions like "Cancel" or "View All."

### Cards: Data Vessels
*   **Styling:** Radius `lg` (12px / 1rem). Background `surface-container-lowest`.
*   **No Dividers:** Never use a horizontal line to separate a card header from its body. Use a `1.5` (0.5rem) spacing gap or a slight bolding of the title.
*   **Padding:** Use `6` (2rem) for internal card padding to ensure data "breathes."

### Inputs: Focused Precision
*   **Default:** `surface-container-low` background, no border, `md` (0.75rem) radius.
*   **Focus State:** A 2px "Ghost Border" using `primary` at 40% opacity and a subtle `primary` glow.

### Sidebar & Navigation
*   **The Signature Sidebar:** Use `surface-container-low`. Active states should not be a highlight box; instead, use a vertical "pill" of `primary` color (3px wide) on the far left and transition the icon/label color to `primary`.

---

## 6. Do's and Don'ts

### Do
*   **Do** use `20` (7rem) or `24` (8.5rem) spacing for top-level page margins. 
*   **Do** utilize `surface-dim` for "empty state" illustrations to keep them background-integrated.
*   **Do** mix font weights—pair a `headline-lg` (700 weight) with a `label-md` (400 weight) for a high-contrast, professional look.

### Don't
*   **Don't** use `#000000` for text. Always use `on-surface` (#0b1c30) to maintain a premium, navy-tinted depth.
*   **Don't** use standard 1px borders. If a section feels "lost," increase the background contrast between `surface` and `surface-container` instead.
*   **Don't** crowd the charts. A chart is an editorial piece of content; it needs at least `8` (2.75rem) of clear space on all sides.