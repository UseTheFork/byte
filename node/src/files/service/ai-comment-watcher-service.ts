import { Service } from '../../support/service.ts'
import { Payload } from '../../support/concerns/eventable.ts'

export class AICommentWatcherService extends Service {
  static token = Symbol('AICommentWatcherService')

  override boot(): void {}

  async handleFileChange(payload: Payload): Promise<Payload> {
    return payload
  }

  async modifyUserRequestHook(payload: Payload): Promise<Payload> {
    return payload
  }

  async addReinforcementHook(payload: Payload): Promise<Payload> {
    return payload
  }
}
