import { describe, it, expect } from 'bun:test'
import { Boundary, BoundaryType } from '../../src/support/boundary.ts'
import { BoundaryExtractor } from '../../src/support/boundary-extractor.ts'

describe('BoundaryType', () => {
  it('has string values', () => {
    expect(BoundaryType.ROLE).toBe('role')
    expect(BoundaryType.TASK).toBe('task')
    expect(BoundaryType.FILE).toBe('file')
  })
})

describe('Boundary', () => {
  describe('open', () => {
    it('xml no meta', () => expect(Boundary.open(BoundaryType.ROLE)).toBe('<role>'))
    it('xml with meta', () => expect(Boundary.open(BoundaryType.CONVENTION, { title: 'Guide' })).toBe('<convention title="Guide">'))
    it('markdown no meta', () => expect(Boundary.open(BoundaryType.ROLE, undefined, 'markdown')).toBe('## Role'))
    it('markdown with title', () => expect(Boundary.open(BoundaryType.CONVENTION, { title: 'Guide' }, 'markdown')).toBe('## Convention: Guide'))
    it('throws on invalid format', () => {
      // @ts-expect-error intentional
      expect(() => Boundary.open(BoundaryType.ROLE, undefined, 'html')).toThrow()
    })
  })

  describe('close', () => {
    it('xml', () => expect(Boundary.close(BoundaryType.ROLE)).toBe('</role>'))
    it('markdown returns empty', () => expect(Boundary.close(BoundaryType.ROLE, 'markdown')).toBe(''))
  })

  describe('notice', () => {
    it('xml wraps in comment', () => expect(Boundary.notice('heads up')).toBe('<!-- NOTICE: heads up -->'))
    it('markdown returns content', () => expect(Boundary.notice('heads up', 'markdown')).toBe('heads up'))
  })
})

describe('BoundaryExtractor', () => {
  it('extracts first match', () => {
    const text = '<role>assistant</role>'
    expect(BoundaryExtractor.extract(text, BoundaryType.ROLE)).toBe('assistant')
  })

  it('returns null when not found', () => {
    expect(BoundaryExtractor.extract('<role>x</role>', BoundaryType.TASK)).toBeNull()
  })

  it('extracts all matches', () => {
    const text = '<file>a.ts</file><file>b.ts</file>'
    expect(BoundaryExtractor.extractAll(text, BoundaryType.FILE)).toEqual(['a.ts', 'b.ts'])
  })

  it('handles tags with attributes', () => {
    const text = '<convention title="Guide">content here</convention>'
    expect(BoundaryExtractor.extract(text, BoundaryType.CONVENTION)).toBe('content here')
  })
})
