import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class PrepareEnvironment implements Bootstrapper {
  bootstrap(app: Application): void {
    const env = process.env['BYTE_ENV'] ?? process.env['NODE_ENV'] ?? 'production'
    app.instance('env', env)
  }
}
