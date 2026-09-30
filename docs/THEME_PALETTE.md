# TRACE Theme Palette

TRACE uses the two supplied Realtime Colors palettes as product themes.

## Dark mode

- Text: `#caced3`
- Background: `#060709`
- Primary: `#28406d`
- Secondary: `#611a3d`
- Accent: `#5a271e`

## Bright mode

- Text: `#090c10`
- Background: `#f6f7f9`
- Primary: `#5e77a6`
- Secondary: `#cca3b7`
- Accent: `#be9189`

The selected theme is persisted in local storage under `trace_theme` and can be switched from the top navigation or authentication screen.

## Typography

Fraunces (display headings), IBM Plex Sans (interface text) and IBM Plex Mono (technical metadata), all bundled locally through `@fontsource` so no network font request is needed. The supplied video assets are not hue-shifted or brightness-filtered; only a transparency overlay is used to preserve text legibility.
