import { describe, it, expect, beforeAll, afterAll } from 'bun:test'
import { Yaml } from '../../src/support/yaml.ts'
import { writeFileSync, unlinkSync } from 'fs'

const FIXTURE_PATH = '/tmp/byte-test-yaml.yaml'

beforeAll(() => {
  writeFileSync(FIXTURE_PATH, 'key: value\nnested:\n  inner: 42\n')
})

afterAll(() => {
  unlinkSync(FIXTURE_PATH)
})

describe('Yaml', () => {
  it('load returns parsed data', () => {
    const data = Yaml.load(FIXTURE_PATH)
    expect(data).toEqual({ key: 'value', nested: { inner: 42 } })
  })

  it('load returns null for missing file', () => {
    expect(Yaml.load('/tmp/does-not-exist.yaml')).toBeNull()
  })

  it('loadAsDict returns dict', () => {
    const data = Yaml.loadAsDict(FIXTURE_PATH)
    expect(data['key']).toBe('value')
  })

  it('loadAsDict returns empty dict for missing file', () => {
    expect(Yaml.loadAsDict('/tmp/does-not-exist.yaml')).toEqual({})
  })
})
