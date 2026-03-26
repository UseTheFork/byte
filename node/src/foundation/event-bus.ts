import type { IApplication } from '../support/concerns/bootable.ts'
import { Payload } from '../support/concerns/eventable.ts'

export const EventType = {
  POST_BOOT: 'post_boot',
  PRE_PROMPT_TOOLKIT: 'pre_prompt_toolkit',
  POST_PROMPT_TOOLKIT: 'post_prompt_toolkit',
  GENERATE_FILE_CONTEXT: 'generate_file_context',
  FILE_ADDED: 'file_added',
  FILE_CHANGED: 'file_changed',
  PRE_AGENT_EXECUTION: 'pre_agent_execution',
  POST_AGENT_EXECUTION: 'post_agent_execution',
  END_NODE: 'end_node',
  PRE_ASSISTANT_NODE: 'pre_assistant_node',
  POST_ASSISTANT_NODE: 'post_assistant_node',
  GATHER_AVAILABLE_CONVENTIONS: 'gather_available_conventions',
  GATHER_PROJECT_CONTEXT: 'gather_project_context',
  GATHER_REINFORCEMENT: 'gather_reinforcement',
  TEST: 'test',
} as const

export type EventType = (typeof EventType)[keyof typeof EventType]

type EventListener = (payload: Payload) => Payload | Promise<Payload> | void | Promise<void>

export class EventBus {
  static token = Symbol('EventBus')
  private _listeners = new Map<string, EventListener[]>()

  constructor(private app: IApplication) {}

  on(eventName: string, callback: EventListener): void {
    if (!this._listeners.has(eventName)) this._listeners.set(eventName, [])
    this._listeners.get(eventName)!.push(callback)
  }

  async emit(payload: Payload): Promise<Payload> {
    const listeners = this._listeners.get(payload.eventType)
    if (!listeners?.length) return payload

    let current = payload
    for (const listener of listeners) {
      try {
        const result = await listener(current)
        if (result !== undefined) current = result
      } catch (e) {
        console.error(`Error in event listener for '${payload.eventType}':`, e)
      }
    }
    return current
  }
}
