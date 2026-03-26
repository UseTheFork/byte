import { ServiceProvider } from '../support/service-provider.ts'
import { EventBus } from './event-bus.ts'
import { TaskManager } from './task-manager.ts'
import { Console } from './console/console.ts'
import type { IApplication } from '../support/concerns/bootable.ts'

export class FoundationServiceProvider extends ServiceProvider {
  constructor(app: IApplication) {
    super(app)
  }

  override register(): void {
    ;(this.app as import('./application.ts').Application).bindPathsInContainer()

    this.app.singleton(EventBus as never, () => new EventBus(this.app))
    this.app.instance('event-bus', this.app.make(EventBus as never))

    this.app.singleton(TaskManager as never, () => new TaskManager(this.app))
    this.app.make(TaskManager as never)

    this.app.singleton(Console as never, () => new Console(this.app))
  }
}
