import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class SetContext implements Bootstrapper {
  bootstrap(app: Application): void {
    app.instance('path.session_context', app.sessionContextPath())
  }
}
