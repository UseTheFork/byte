import { EventEmitter } from 'events'

export type PrintItem =
  | { type: 'text'; content: string; style?: string }
  | { type: 'rule'; label?: string }
  | { type: 'error'; content: string }
  | { type: 'markdown'; content: string }

export interface SpinnerState {
  message: string
}

export interface LiveContent {
  content: string
  final: boolean
}

export interface ModalState {
  type: 'confirm' | 'select'
  message: string
  choices?: string[]
  default?: boolean | string
  resolve: (value: unknown) => void
}

export interface ConsoleState {
  messages: PrintItem[]
  spinner: SpinnerState | null
  promptVisible: boolean
  promptDefault: string
  modal: ModalState | null
  live: LiveContent | null
  width: number
}

export class ConsoleStore extends EventEmitter {
  private _state: ConsoleState = {
    messages: [],
    spinner: null,
    promptVisible: false,
    promptDefault: '',
    modal: null,
    live: null,
    width: process.stdout.columns ?? 80,
  }

  get state(): Readonly<ConsoleState> {
    return this._state
  }

  setState(patch: Partial<ConsoleState>): void {
    this._state = { ...this._state, ...patch }
    this.emit('change', this._state)
  }

  appendMessage(item: PrintItem): void {
    this.setState({ messages: [...this._state.messages, item] })
  }
}
