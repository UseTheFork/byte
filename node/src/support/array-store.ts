export class ArrayStore<T = unknown> {
  private _data: Record<string, T>

  constructor(data?: Record<string, T>) {
    this._data = data ? { ...data } : {}
  }

  add(key: string, value: T): this {
    this._data[key] = value
    return this
  }

  get(key: string, defaultValue?: T): T | undefined {
    return key in this._data ? this._data[key] : defaultValue
  }

  all(): Record<string, T> {
    return this._data
  }

  isEmpty(): boolean {
    return Object.keys(this._data).length === 0
  }

  isNotEmpty(): boolean {
    return !this.isEmpty()
  }

  merge(...dicts: Record<string, T>[]): this {
    for (const dict of dicts) {
      Object.assign(this._data, dict)
    }
    return this
  }

  remove(key: string): this {
    delete this._data[key]
    return this
  }

  set(data: Record<string, T>): this {
    this._data = { ...data }
    return this
  }
}
