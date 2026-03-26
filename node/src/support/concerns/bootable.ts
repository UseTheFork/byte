/**
 * IApplication is defined here (in support/) to avoid circular imports.
 * Application (foundation/) implements this interface.
 * ServiceProvider (support/) depends on this interface.
 */
export interface IApplication {
  make<T = unknown>(abstract: Newable<T> | string): T
  singleton(cls: Newable<unknown>, factory?: () => unknown): void
  bind(cls: Newable<unknown>, factory?: () => unknown): void
  instance(abstract: Newable<unknown> | string, value: unknown): unknown
  running_unit_tests(): boolean
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Newable<T> = new (...args: any[]) => T

export abstract class Bootable {
  protected app: IApplication
  private _isBooted = false

  constructor(app: IApplication) {
    this.app = app
  }

  ensureBooted(): void {
    if (this._isBooted) return
    this.bootConcerns()
    this.boot()
    this._isBooted = true
  }

  /** Override in subclasses to call per-concern boot methods. */
  protected bootConcerns(): void {}

  /** Override to perform initialization after construction. */
  boot(): void {}
}
