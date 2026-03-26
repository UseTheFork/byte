import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'
import { Yaml } from '../../support/yaml.ts'
import { ByteConfigSchema } from '../../config/schemas.ts'
import { ByteConfigException } from '../../config/exceptions.ts'
import path from 'path'

export class LoadConfiguration implements Bootstrapper {
  bootstrap(app: Application): void {
    const configPath = app.configPath()
    const raw = Yaml.loadAsDict(path.join(configPath, 'config.yaml'))

    const result = ByteConfigSchema.safeParse(raw)
    if (!result.success) {
      throw new ByteConfigException(
        `Invalid configuration: ${result.error.message}`
      )
    }

    app.instance('config', result.data)
    app.detectEnvironment(() => result.data.app.env)
  }
}
