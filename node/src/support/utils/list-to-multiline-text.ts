export function listToMultilineText(lines: string[], separator = '\n'): string {
  if (!lines.length) return ''
  return lines.join(separator)
}
