import { Bootable } from '../support/concerns/bootable.ts'
import type { IApplication } from '../support/concerns/bootable.ts'

export class TaskManager extends Bootable {
  static token = Symbol('TaskManager')
  private _tasks = new Map<string, Promise<unknown>>()

  constructor(app: IApplication) {
    super(app)
  }

  startTask(name: string, promise: Promise<unknown>): Promise<unknown> {
    this._tasks.set(name, promise.finally(() => this._tasks.delete(name)))
    return this._tasks.get(name)!
  }

  stopTask(name: string): void {
    this._tasks.delete(name)
  }

  hasTask(name: string): boolean {
    return this._tasks.has(name)
  }

  dispatchTask(promise: Promise<unknown>): Promise<unknown> {
    const name = `task_${Math.random().toString(36).slice(2, 10)}`
    return this.startTask(name, promise)
  }

  async shutdown(): Promise<void> {
    await Promise.allSettled(this._tasks.values())
    this._tasks.clear()
  }
}
