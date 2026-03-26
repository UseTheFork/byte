import type { Application } from './application.ts'
import type { Bootstrapper } from './bootstrap/bootstrapper.ts'
import type { Newable } from '../support/concerns/bootable.ts'
import {
  LoadEnvironmentVariables,
  LoadConsoleArgs,
  PrepareEnvironment,
  LoadConfiguration,
  SetContext,
  HandleExceptions,
  RegisterProviders,
} from './bootstrap/index.ts'

export class Kernel {
  static token = Symbol('Kernel')

  constructor(private app: Application) {}

  bootstrappers(): Newable<Bootstrapper>[] {
    return [
      LoadEnvironmentVariables,
      LoadConsoleArgs,
      PrepareEnvironment,
      LoadConfiguration,
      SetContext,
      HandleExceptions,
      RegisterProviders,
    ]
  }

  bootstrap(): void {
    if (!this.app.hasBeenBootstrapped()) {
      this.app.bootstrapWith(this.bootstrappers())
    }
  }

  async handle(input: string[]): Promise<number> {
    this.bootstrap()
    await this.app.boot()
    return this.app.run()
  }

  terminate(): void {
    this.app.terminate()
  }
}
