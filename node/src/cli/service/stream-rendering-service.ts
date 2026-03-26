import { Service } from '../../support/service.ts'

export class StreamRenderingService extends Service {
  static token = Symbol('StreamRenderingService')

  async handleMessage(_chunk: unknown, _agentName: string): Promise<void> {}
  async startSpinner(_message?: string): Promise<void> {}
  async stopSpinner(): Promise<void> {}
  async endStream(): Promise<void> {}
  setDisplayMode(_mode: string): void {}
}
