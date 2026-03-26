import { describe, it, expect } from 'bun:test'
import { Str } from '../../src/support/str.ts'

describe('Str', () => {
  describe('contains', () => {
    it('finds substring', () => expect(Str.contains('hello world', 'world')).toBe(true))
    it('returns false when absent', () => expect(Str.contains('hello', 'xyz')).toBe(false))
    it('handles null haystack', () => expect(Str.contains(null, 'x')).toBe(false))
    it('handles array of needles', () => expect(Str.contains('hello', ['world', 'hello'])).toBe(true))
    it('case insensitive', () => expect(Str.contains('Hello', 'hello', true)).toBe(true))
  })

  describe('snakeCase', () => {
    it('converts PascalCase', () => expect(Str.snakeCase('StartNode')).toBe('start_node'))
    it('converts camelCase', () => expect(Str.snakeCase('myClassName')).toBe('my_class_name'))
  })

  describe('slugify', () => {
    it('converts to slug', () => expect(Str.slugify('Hello World')).toBe('hello-world'))
    it('custom separator', () => expect(Str.slugify('Hello World', '_')).toBe('hello_world'))
  })

  describe('isPattern', () => {
    it('exact match', () => expect(Str.isPattern('hello', 'hello')).toBe(true))
    it('wildcard match', () => expect(Str.isPattern('library/*', 'library/foo')).toBe(true))
    it('no match', () => expect(Str.isPattern('foo', 'bar')).toBe(false))
    it('* matches everything', () => expect(Str.isPattern('*', 'anything')).toBe(true))
  })

  describe('beforeLast', () => {
    it('returns before last occurrence', () => expect(Str.beforeLast('foo:bar:baz', ':')).toBe('foo:bar'))
    it('returns original when not found', () => expect(Str.beforeLast('foo', ':')).toBe('foo'))
  })

  describe('afterLast', () => {
    it('returns after last occurrence', () => expect(Str.afterLast('foo:bar:baz', ':')).toBe('baz'))
    it('returns original when not found', () => expect(Str.afterLast('foo', ':')).toBe('foo'))
  })

  describe('substrCount', () => {
    it('counts occurrences', () => expect(Str.substrCount('aababab', 'ab')).toBe(3))
  })

  describe('classToString', () => {
    it('returns constructor name for class', () => {
      class MyService {}
      expect(Str.classToString(MyService)).toBe('MyService')
    })
    it('returns string as-is', () => expect(Str.classToString('my-key')).toBe('my-key'))
  })
})
