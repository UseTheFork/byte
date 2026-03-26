import { Service } from '../../support/service.ts'
import type { IApplication } from '../../support/concerns/bootable.ts'
import { ConsoleStore } from '../store/console-store.ts'

export class Console extends Service {
  static token = Symbol('Console')

  private readonly _store: ConsoleStore

  constructor(app: IApplication) {
    super(app)
    this._store = new ConsoleStore()
  }

  get store(): ConsoleStore {
    return this._store
  }

  get width(): number {
    return this._store.state.width
  }

  print(text: string, style?: string): void {
    this._store.appendMessage({ type: 'text', content: text, style })
  }

  rule(label?: string): void {
    this._store.appendMessage({ type: 'rule', label })
  }

  printError(text: string): void {
    this._store.appendMessage({ type: 'error', content: text })
  }

  startSpinner(message: string): void {
    this._store.setState({ spinner: { message } })
  }

  stopSpinner(): void {
    this._store.setState({ spinner: null })
  }

  clearLive(): void {
    this._store.setState({ live: null })
  }

  confirm(message: string, defaultValue = true): Promise<boolean> {
    return new Promise((resolve) => {
      this._store.setState({
        modal: {
          type: 'confirm',
          message,
          default: defaultValue,
          resolve: (v) => {
            this._store.setState({ modal: null })
            resolve(v as boolean)
          },
        },
      })
    })
  }

  select(message: string, ...choices: string[]): Promise<string> {
    return new Promise((resolve) => {
      this._store.setState({
        modal: {
          type: 'select',
          message,
          choices,
          resolve: (v) => {
            this._store.setState({ modal: null })
            resolve(v as string)
          },
        },
      })
    })
  }
}
