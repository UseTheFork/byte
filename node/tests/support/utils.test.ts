import { describe, it, expect } from 'bun:test'
import { value } from '../../src/support/utils/value.ts'
import { slugify } from '../../src/support/utils/slugify.ts'
import { listToMultilineText } from '../../src/support/utils/list-to-multiline-text.ts'
import { parsePartialJson } from '../../src/support/utils/parse-partial-json.ts'

describe('value', () => {
  it('returns value as-is if not callable', () => expect(value(42)).toBe(42))
  it('calls callable and returns result', () => expect(value(() => 'hello')).toBe('hello'))
  it('passes args to callable', () => expect(value((x: number) => x * 2, 5)).toBe(10))
})

describe('slugify', () => {
  it('basic slugify', () => expect(slugify('Hello World')).toBe('hello-world'))
  it('custom separator', () => expect(slugify('Hello World', '_')).toBe('hello_world'))
  it('strips leading/trailing separators', () => expect(slugify('--hello--')).toBe('hello'))
})

describe('listToMultilineText', () => {
  it('joins with newline', () => expect(listToMultilineText(['a', 'b', 'c'])).toBe('a\nb\nc'))
  it('custom separator', () => expect(listToMultilineText(['a', 'b'], ', ')).toBe('a, b'))
  it('empty list returns empty string', () => expect(listToMultilineText([])).toBe(''))
})

describe('parsePartialJson', () => {
  it('parses valid JSON', () => expect(parsePartialJson('{"a":1}')).toEqual({ a: 1 }))
  it('parses partial JSON missing closing brace', () => expect(parsePartialJson('{"a":1')).toEqual({ a: 1 }))
  it('parses partial JSON missing closing bracket', () => expect(parsePartialJson('["a","b"')).toEqual(['a', 'b']))
})
