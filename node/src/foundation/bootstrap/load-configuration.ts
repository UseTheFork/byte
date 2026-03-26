import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'
import { Yaml } from '../../support/yaml.ts'
import path from 'path'

export class LoadConfiguration implements Bootstrapper {
  bootstrap(app: Application): void {
    const configPath = app.configPath()
    const config = Yaml.loadAsDict(path.join(configPath, 'config.yaml'))
    app.instance('config', config)
  }
}
