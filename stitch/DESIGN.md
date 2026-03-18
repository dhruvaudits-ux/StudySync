# Design System Strategy: Engineering Precision & Academic Flow

## 1. Overview & Creative North Star: "The Cognitive Sanctuary"
For engineering students, the UI must do more than just display content; it must facilitate mental modeling. Our North Star is **"The Cognitive Sanctuary."** We move away from the "busy" aesthetics of traditional EdTech. Instead, we embrace a high-end editorial feel that balances the rigor of engineering with the fluidity of deep work.

To break the "template" look, we utilize **Intentional Asymmetry**. We pair expansive, airy white space with dense, technically precise data clusters. Elements should feel like they are floating on a coordinated plane rather than being locked into a rigid, boxed-in grid.

## 2. Color & Surface Architecture
The color palette is built on a foundation of "Oxygenated Blues" and "Engineered Greys." We avoid the "default web" look by using tonal depth instead of decorative color.

### The "No-Line" Rule
**Borders are prohibited for sectioning.** To separate a sidebar from a main content area, or a header from a hero, you must use a background shift. 
*   *Example:* Use `surface` (#f8f9fa) for the main background and `surface_container_low` (#f3f4f5) for the sidebar. The transition should be felt, not seen as a stroke.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of technical papers and frosted glass:
*   **Base Layer:** `surface` (#f8f9fa) – The desk.
*   **Section Layer:** `surface_container` (#edeeef) – The organized zones.
*   **Interactive Layer:** `surface_container_lowest` (#ffffff) – The active "paper" the student is working on.
By nesting a white card (`surface_container_lowest`) inside a light grey section (`surface_container_low`), we create a sophisticated lift without a single drop shadow.

### Signature Textures: The "Engineered Gradient"
Main CTAs and high-level progress indicators should not be flat. Use a subtle linear gradient (135°) transitioning from `primary` (#005dac) to `primary_container` (#1976d2). This adds a "lithographic" quality that feels premium and custom.

## 3. Typography: Editorial Technicality
We pair **Manrope** (Display/Headlines) with **Inter** (Body/Labels) to create a "Technical Journal" aesthetic.

*   **Display (Manrope):** Set with tight letter-spacing (-0.02em). This is your "Editorial" voice. Use `display-md` (2.75rem) for module titles to create a sense of authority.
*   **Body (Inter):** The "Workhorse." Use `body-lg` (1rem) for reading-heavy content. Inter’s high x-height ensures clarity during late-night study sessions.
*   **Label (Inter):** Use `label-md` (0.75rem) in all-caps with +0.05em tracking for technical metadata (e.g., "STRENGTH OF MATERIALS • 45 MINS") to mimic blueprint annotations.

## 4. Elevation & Depth: Tonal Layering
We reject the standard Material Design "shadow-heavy" look in favor of **Tonal Layering.**

*   **The Layering Principle:** Depth is achieved by "stacking." A card (`surface_container_lowest`) sitting on a section (`surface_container_low`) creates a natural, soft lift.
*   **Ambient Shadows:** If an element must float (like a FAB or a Modal), use an extra-diffused shadow: `box-shadow: 0 12px 32px rgba(25, 28, 29, 0.04)`. The shadow color is a 4% tint of `on_surface`, making it feel like ambient occlusion rather than a "drop shadow."
*   **The "Ghost Border" Fallback:** If a border is required for accessibility in input fields, use `outline_variant` (#c1c6d4) at 20% opacity. 100% opaque borders are strictly forbidden.
*   **Glassmorphism:** For top navigation bars, use `surface` at 80% opacity with a `backdrop-filter: blur(12px)`. This keeps the student oriented within the page scroll without breaking their focus with a hard line.

## 5. Components & Interface Patterns

### Buttons
*   **Primary:** Gradient fill (`primary` to `primary_container`), `xl` (1.5rem) corner radius. No border.
*   **Secondary:** Ghost style. No background, no border. Use `primary` text weight 600.
*   **Tertiary:** `surface_container_high` background with `on_surface` text.

### Cards & Study Modules
*   **Constraint:** Never use a divider line. 
*   **Layout:** Use a `1.5rem` (`6` on the spacing scale) internal padding. 
*   **Grouping:** Use `surface_container_highest` for a small "header" area within a card to separate titles from content via a subtle background shift.

### Input Fields
*   **Style:** `surface_container_low` background, `xl` corner radius, no border.
*   **Focus State:** The background shifts to `surface_container_lowest` (pure white) with a 1px `primary` ghost border (20% opacity).

### Specialized EdTech Components
*   **The "Focus Progress" Bar:** A thin (4px) track using `secondary_container` with a `primary` fill. Place it at the very top of a card to indicate completion without occupying "content real estate."
*   **Formula Blocks:** Nested containers using `tertiary_fixed` (#ffdbc7) at 10% opacity to highlight engineering equations in a way that feels distinct from standard text.

## 6. Do’s and Don’ts

### Do
*   **Do** use the `24` (6rem) spacing token between major content sections to allow the student's eyes to "reset."
*   **Do** use `tertiary` (#944700) sparingly for "Aha!" moments or critical insights. It should be a rare "technical gold" accent.
*   **Do** lean into the `xl` (1.5rem) corner radius for large containers to soften the "industrial" feel of engineering data.

### Don't
*   **Don't** use 1px solid #CCCCCC borders. This is the fastest way to make the platform look like a generic bootstrap template.
*   **Don't** use pure black (#000000) for text. Always use `on_surface` (#191c1d) to maintain a soft, paper-like contrast.
*   **Don't** crowd the interface. If a screen feels "full," increase the surface nesting depth instead of adding more lines or boxes.