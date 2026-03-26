import { describe, it, expect } from 'bun:test'
import { TaskManager } from '../../src/foundation/task-manager.ts'
import type { IApplication } from '../../src/support/concerns/bootable.ts'

const mockApp = { make: () => ({}), singleton: () => {}, bind: () => {}, instance: () => {}, running_unit_tests: () => false } as unknown as IApplication

describe('TaskManager', () => {
  it('dispatchTask returns a promise', () => {
    const tm = new TaskManager(mockApp)
    const result = tm.dispatchTask(Promise.resolve('done'))
    expect(result).toBeInstanceOf(Promise)
  })

  it('startTask registers a named task', () => {
    const tm = new TaskManager(mockApp)
    tm.startTask('test', Promise.resolve())
    expect(tm.hasTask('test')).toBe(true)
  })

  it('stopTask removes the task', () => {
    const tm = new TaskManager(mockApp)
    tm.startTask('test', Promise.resolve())
    tm.stopTask('test')
    expect(tm.hasTask('test')).toBe(false)
  })

  it('shutdown resolves all tasks', async () => {
    const tm = new TaskManager(mockApp)
    tm.startTask('a', Promise.resolve('done'))
    await tm.shutdown()
    expect(tm.hasTask('a')).toBe(false)
  })
})
