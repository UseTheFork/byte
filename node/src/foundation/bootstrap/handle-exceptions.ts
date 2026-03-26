import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class HandleExceptions implements Bootstrapper {
  bootstrap(_app: Application): void {
    process.on('uncaughtException', (err) => {
      console.error('Uncaught exception:', err)
    })
    process.on('unhandledRejection', (reason) => {
      console.error('Unhandled rejection:', reason)
    })
  }
}
