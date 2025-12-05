## Description
This PR implements the Block Renderer and all associated React components for the frontend, completing the GEN-9 Work Order.

## Key Changes
- **Core Rendering Logic:**
  - Implemented `BlockRenderer` with dynamic imports.
  - Added `PageRenderer` and `SiteRenderer`.
  - Added `ThemeProvider` for dynamic styling.

- **New Block Components:**
  - `AboutBlock`
  - `ServicesBlock`
  - `ContactBlock` (with form)
  - `TestimonialsBlock`
  - `GalleryBlock`
  - `CTABlock`
  - `HeaderBlock`

- **Enhanced Existing Blocks:**
  - `HeroBlock` updated with new props (alignment, overlay).
  - `FooterBlock` updated (multi-column support).
  - `FeaturesBlock` updated (dynamic icons).

- **Infrastructure:**
  - Added Jest configuration and smoke tests (`BlockRenderer.test.tsx`).
  - Fixed `lucide-react` imports for Next.js compatibility.

## Verification
- **Smoke Tests:** Included in `src/__tests__/components/BlockRenderer.test.tsx`.
- **Manual Verification:** Code integrity validated via `npm run build` (after fixing Docker env issues).
