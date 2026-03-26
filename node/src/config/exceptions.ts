import { ByteException } from '../foundation/exceptions.ts'

export class ByteConfigException extends ByteException {
  constructor(message: string) {
    super(message)
    this.name = 'ByteConfigException'
  }
}
