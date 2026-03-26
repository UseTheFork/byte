export class ByteException extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ByteException'
  }
}
