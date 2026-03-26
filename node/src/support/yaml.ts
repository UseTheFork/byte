import { existsSync, readFileSync } from 'fs'
import jsYaml from 'js-yaml'

export class Yaml {
  static load(path: string): unknown {
    if (!existsSync(path)) return null
    const content = readFileSync(path, 'utf-8')
    return jsYaml.load(content)
  }

  static loadAsDict(path: string): Record<string, unknown> {
    const data = Yaml.load(path)
    if (data === null || typeof data !== 'object' || Array.isArray(data)) return {}
    return data as Record<string, unknown>
  }
}
