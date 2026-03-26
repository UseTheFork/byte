import type { Application } from '../application.ts'

export interface Bootstrapper {
  bootstrap(app: Application): void | Promise<void>
}
