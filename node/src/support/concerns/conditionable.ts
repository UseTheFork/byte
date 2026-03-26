import { value } from '../utils/value.ts'

export abstract class Conditionable {
  when<V>(
    condition: V | (() => V),
    callback: (self: this, val: V) => void,
    defaultCb?: (self: this, val: V) => void,
  ): this {
    const val = value(condition) as V
    if (val) callback(this, val)
    else if (defaultCb) defaultCb(this, val)
    return this
  }

  unless<V>(
    condition: V | (() => V),
    callback: (self: this, val: V) => void,
    defaultCb?: (self: this, val: V) => void,
  ): this {
    const val = value(condition) as V
    if (!val) callback(this, val)
    else if (defaultCb) defaultCb(this, val)
    return this
  }
}
