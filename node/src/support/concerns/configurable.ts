import { ArrayStore } from '../array-store.ts'

export abstract class Configurable {
  private _config = new ArrayStore<unknown>()

  config(): ArrayStore<unknown> {
    return this._config
  }

  protected bootConfigurable(): void {}
}
