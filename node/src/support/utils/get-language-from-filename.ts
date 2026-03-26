const EXTENSION_MAP: Record<string, string> = {
  ts: 'typescript', tsx: 'typescript', js: 'javascript', jsx: 'javascript',
  py: 'python', rb: 'ruby', rs: 'rust', go: 'go', java: 'java',
  cs: 'csharp', cpp: 'cpp', c: 'c', h: 'c', php: 'php',
  swift: 'swift', kt: 'kotlin', sh: 'bash', bash: 'bash',
  zsh: 'bash', md: 'markdown', yaml: 'yaml', yml: 'yaml',
  json: 'json', toml: 'toml', html: 'html', css: 'css',
  scss: 'scss', sql: 'sql', xml: 'xml',
}

export function getLanguageFromFilename(filename: string): string | null {
  const ext = filename.split('.').pop()?.toLowerCase()
  if (!ext) return null
  return EXTENSION_MAP[ext] ?? null
}
