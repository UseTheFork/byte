import { ServiceProvider } from "../support/service-provider.ts";
import type { CommandRegistry } from "../cli/service/command-registry.ts";

export class AgentServiceProvider extends ServiceProvider {
  override register(): void {
    //
  }

  override async boot(): Promise<void> {
    //
  }
}
