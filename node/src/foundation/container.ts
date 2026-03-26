import type { IApplication, Newable } from '../support/concerns/bootable.ts'

type TokenKey = symbol | string

interface Tokenable<T> extends Newable<T> {
  token: symbol
}

function getKey(abstract: Tokenable<unknown> | string): TokenKey {
  if (typeof abstract === 'string') return abstract
  return abstract.token
}

type Factory<T = unknown> = () => T

export class Container implements IApplication {
  protected _singletons = new Map<TokenKey, Factory>()
  protected _transients = new Map<TokenKey, Factory>()
  protected _instances = new Map<TokenKey, unknown>()

  bind<T>(cls: Tokenable<T>, factory?: () => T): void {
    const key = getKey(cls)
    this._transients.set(key, factory ?? (() => new cls()))
  }

  singleton<T>(cls: Tokenable<T>, factory?: () => T): void {
    const key = getKey(cls)
    this._singletons.set(key, factory ?? (() => new cls()))
  }

  instance<T>(abstract: Tokenable<T> | string, value: T): T {
    const key = typeof abstract === 'string' ? abstract : getKey(abstract as Tokenable<T>)
    this._instances.set(key, value)
    return value
  }

  make<T = unknown>(abstract: Tokenable<T> | string): T {
    const key = typeof abstract === 'string' ? abstract : getKey(abstract as Tokenable<T>)

    if (this._instances.has(key)) return this._instances.get(key) as T

    if (this._singletons.has(key)) {
      const instance = (this._singletons.get(key) as Factory<T>)()
      this._instances.set(key, instance)
      return instance
    }

    if (this._transients.has(key)) {
      return (this._transients.get(key) as Factory<T>)()
    }

    if (typeof abstract !== 'string') {
      return new (abstract as Tokenable<T>)()
    }

    throw new Error(`No binding found for ${String(key)}`)
  }

  bound(abstract: Tokenable<unknown> | string): boolean {
    const key = typeof abstract === 'string' ? abstract : getKey(abstract as Tokenable<unknown>)
    return this._instances.has(key) || this._singletons.has(key) || this._transients.has(key)
  }

  flush(): void {
    this._singletons.clear()
    this._transients.clear()
    this._instances.clear()
  }

  get<T = unknown>(key: string): T {
    return this.make<T>(key)
  }

  set(key: string, value: unknown): void {
    this.instance(key, value)
  }

  running_unit_tests(): boolean {
    try { return this.make<string>('env') === 'testing' } catch { return false }
  }
}
