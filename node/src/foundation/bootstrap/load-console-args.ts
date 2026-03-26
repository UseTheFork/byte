import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class LoadConsoleArgs implements Bootstrapper {
  bootstrap(app: Application): void {
    app.instance('args', process.argv.slice(2))
  }
}
