import { Bootable } from "./concerns/bootable.ts";
import type { Eventable } from "./concerns/eventable.ts";
import { Payload } from "./concerns/eventable.ts";

export abstract class Service extends Bootable implements Eventable {
  async validate(): Promise<boolean> {
    return true;
  }

  async handle(..._args: unknown[]): Promise<unknown> {
    return undefined;
  }

  async run(...args: unknown[]): Promise<unknown> {
    await this.validate();
    return this.handle(...args);
  }

  async emit(payload: Payload): Promise<Payload> {
    const eventBus = this.app.make<{ emit(p: Payload): Promise<Payload> }>(
      "event-bus",
    );
    return eventBus.emit(payload);
  }
}
