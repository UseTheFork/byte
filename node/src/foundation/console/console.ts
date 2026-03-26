import type { IApplication } from '../../support/concerns/bootable.ts'

export class Console {
  static token = Symbol('Console')

  constructor(private app: IApplication) {}

  print(message: string): void {
    process.stdout.write(message + '\n')
  }

  error(message: string): void {
    process.stderr.write(message + '\n')
  }
}
