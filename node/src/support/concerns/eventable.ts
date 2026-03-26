import { ArrayStore } from '../array-store.ts'

export class Payload {
  readonly eventType: string
  readonly timestamp: number
  readonly data: ArrayStore<unknown>

  constructor(
    eventType: string,
    data?: ArrayStore<unknown> | Record<string, unknown>,
    timestamp?: number,
  ) {
    this.eventType = eventType
    this.timestamp = timestamp ?? Date.now()
    if (data instanceof ArrayStore) {
      this.data = data
    } else if (data && typeof data === 'object') {
      this.data = new ArrayStore(data)
    } else {
      this.data = new ArrayStore()
    }
  }

  get(key: string, defaultValue?: unknown): unknown {
    return this.data.get(key, defaultValue)
  }

  set(key: string, value: unknown): this {
    this.data.add(key, value)
    return this
  }

  update(updates: Record<string, unknown>): this {
    this.data.merge(updates)
    return this
  }
}

/** Implemented by Service — requires this.app to be available (from Bootable). */
export interface Eventable {
  emit(payload: Payload): Promise<Payload>
}
