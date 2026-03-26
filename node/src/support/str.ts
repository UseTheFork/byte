export class Str {
  static contains(haystack: string | null, needles: string | string[], ignoreCase = false): boolean {
    if (haystack === null) return false
    const h = ignoreCase ? haystack.toLowerCase() : haystack
    const arr = Array.isArray(needles) ? needles : [needles]
    return arr.some(n => {
      const needle = ignoreCase ? n.toLowerCase() : n
      return needle !== '' && h.includes(needle)
    })
  }

  static snakeCase(value: string): string {
    const s1 = value.replace(/(.)([A-Z][a-z]+)/g, '$1_$2')
    const s2 = s1.replace(/([a-z0-9])([A-Z])/g, '$1_$2')
    return s2.toLowerCase()
  }

  static slugify(text: string, separator = '-'): string {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, separator)
      .replace(new RegExp(`^${separator}|${separator}$`, 'g'), '')
  }

  static isPattern(pattern: string | string[], value: string, ignoreCase = false): boolean {
    const patterns = Array.isArray(pattern) ? pattern : [pattern]
    const v = String(value)
    for (const p of patterns) {
      const ps = String(p)
      if (ps === '*' || ps === v) return true
      if (ignoreCase && ps.toLowerCase() === v.toLowerCase()) return true
      const escaped = ps.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*')
      const flags = ignoreCase ? 'is' : 's'
      if (new RegExp(`^${escaped}$`, flags).test(v)) return true
    }
    return false
  }

  static beforeLast(subject: string, search: string): string {
    if (search === '') return subject
    const pos = subject.lastIndexOf(search)
    return pos === -1 ? subject : subject.slice(0, pos)
  }

  static afterLast(subject: string, search: string): string {
    if (search === '') return subject
    const pos = subject.lastIndexOf(search)
    return pos === -1 ? subject : subject.slice(pos + search.length)
  }

  static substrCount(haystack: string, needle: string, offset = 0, length?: number): number {
    const slice = length !== undefined ? haystack.slice(offset, offset + length) : haystack.slice(offset)
    let count = 0
    let start = 0
    while ((start = slice.indexOf(needle, start)) !== -1) {
      count++
      start += needle.length
    }
    return count
  }

  static classToString(abstract: (new (...args: unknown[]) => unknown) | string): string {
    if (typeof abstract === 'string') return abstract
    return abstract.name
  }

  static classToSnakeCase(abstract: (new (...args: unknown[]) => unknown) | string): string {
    return Str.snakeCase(Str.classToString(abstract))
  }

  static parseCallback(callback: string, defaultMethod?: string): [string, string | undefined] {
    if (Str.contains(callback, ':')) {
      const idx = callback.indexOf(':')
      return [callback.slice(0, idx), callback.slice(idx + 1)]
    }
    return [callback, defaultMethod]
  }

  static lower(value: string): string {
    return value.toLowerCase()
  }
}
