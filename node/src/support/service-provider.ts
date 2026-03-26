import type { IApplication, Newable } from './concerns/bootable.ts'
import type { Service } from './service.ts'

export abstract class ServiceProvider {
  protected app: IApplication

  constructor(app: IApplication) {
    this.app = app
  }

  services(): Newable<Service>[] {
    return []
  }

  commands(): Newable<unknown>[] {
    return []
  }

  registerServices(): void {
    for (const serviceClass of this.services()) {
      this.app.singleton(serviceClass)
    }
  }

  registerCommands(): void {
    // Command registry integration deferred to cli domain migration
  }

  register(): void {}

  async boot(): Promise<void> {}

  async shutdown(_app: IApplication): Promise<void> {}
}
