import type { Application } from './application.ts'
import type { Newable } from '../support/concerns/bootable.ts'
import type { ServiceProvider } from '../support/service-provider.ts'

export class ApplicationBuilder {
  constructor(private _application: Application) {}

  withKernels(): this {
    // Kernel singleton registered here once Kernel is implemented
    return this
  }

  withProviders(providers?: Newable<ServiceProvider>[]): this {
    if (providers?.length) {
      for (const P of providers) this._application.register(P)
    }
    return this
  }

  create(): Application {
    return this._application
  }
}
