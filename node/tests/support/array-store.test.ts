import { describe, it, expect } from 'bun:test'
import { ArrayStore } from '../../src/support/array-store.ts'

describe('ArrayStore', () => {
  it('starts empty', () => {
    const store = new ArrayStore()
    expect(store.isEmpty()).toBe(true)
    expect(store.isNotEmpty()).toBe(false)
  })

  it('accepts initial data', () => {
    const store = new ArrayStore({ key: 'value' })
    expect(store.get('key')).toBe('value')
  })

  it('add and get', () => {
    const store = new ArrayStore<string>()
    store.add('name', 'byte')
    expect(store.get('name')).toBe('byte')
  })

  it('get returns default when missing', () => {
    const store = new ArrayStore()
    expect(store.get('missing', 'fallback')).toBe('fallback')
  })

  it('all returns underlying data', () => {
    const store = new ArrayStore({ a: 1, b: 2 })
    expect(store.all()).toEqual({ a: 1, b: 2 })
  })

  it('merge combines multiple dicts', () => {
    const store = new ArrayStore<unknown>({ a: 1 })
    store.merge({ b: 2 }, { c: 3 })
    expect(store.all()).toEqual({ a: 1, b: 2, c: 3 })
  })

  it('remove deletes a key', () => {
    const store = new ArrayStore({ a: 1, b: 2 })
    store.remove('a')
    expect(store.all()).toEqual({ b: 2 })
  })

  it('set replaces all data', () => {
    const store = new ArrayStore({ old: true })
    store.set({ new: true })
    expect(store.all()).toEqual({ new: true })
  })

  it('is fluent — add returns self', () => {
    const store = new ArrayStore<number>()
    const result = store.add('x', 1)
    expect(result).toBe(store)
  })
})
