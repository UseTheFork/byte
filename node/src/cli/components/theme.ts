// Catppuccin Mocha palette mapped to semantic names.
// Source: foundation/console/console.py setup_console()
export const theme = {
  primary: '#89b4fa',        // base0D — blue (Functions, Headings)
  secondary: '#cba6f7',      // base0E — mauve (Keywords, Italic)
  muted: '#45475a',          // base03 — surface1 (Comments, Invisibles)
  error: '#f38ba8',          // base08 — red (Variables, Tags)
  text: '#cdd6f4',           // base05 — text (Default Foreground)
  active_border: '#b4befe',  // base07 — lavender (Light Background)
  inactive_border: '#45475a', // base03 — surface1 (Comments)
  danger: '#f38ba8',         // base08 — red
} as const

export type ThemeColor = keyof typeof theme
