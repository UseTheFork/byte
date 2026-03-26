import type { BoundaryType } from './boundary.ts'

export class BoundaryExtractor {
  static extract(text: string, boundaryType: BoundaryType): string | null {
    const escaped = boundaryType.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const pattern = new RegExp(`<${escaped}(?:\\s+[^>]*)?>([\\s\\S]+?)<\\/${escaped}>`)
    const match = pattern.exec(text)
    return match ? match[1]!.trim() : null
  }

  static extractAll(text: string, boundaryType: BoundaryType): string[] {
    const escaped = boundaryType.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const pattern = new RegExp(`<${escaped}(?:\\s+[^>]*)?>([\\s\\S]+?)<\\/${escaped}>`, 'g')
    const results: string[] = []
    let match: RegExpExecArray | null
    while ((match = pattern.exec(text)) !== null) {
      results.push(match[1]!.trim())
    }
    return results
  }
}
