import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class LoadEnvironmentVariables implements Bootstrapper {
  bootstrap(_app: Application): void {
    // Bun auto-loads .env files — process.env is populated at startup.
    // Nothing to do here unless a custom .env path is needed.
  }
}
