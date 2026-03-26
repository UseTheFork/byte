import type { Application } from '../application.ts'
import type { Bootstrapper } from './bootstrapper.ts'
import type { Newable } from '../../support/concerns/bootable.ts'
import type { ServiceProvider } from '../../support/service-provider.ts'

export class RegisterProviders implements Bootstrapper {
  static _merge: Newable<ServiceProvider>[] = []

  static merge(providers: Newable<ServiceProvider>[]): void {
    RegisterProviders._merge = [...RegisterProviders._merge, ...providers]
  }

  bootstrap(app: Application): void {
    for (const P of RegisterProviders._merge) {
      app.register(P)
    }
  }
}
