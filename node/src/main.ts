import React from 'react'
import { render } from 'ink'
import { Application } from './foundation/application.ts'
import { FoundationServiceProvider } from './foundation/service-provider.ts'
import { CLIServiceProvider } from './cli/service-provider.ts'
import { GitServiceProvider } from './git/service-provider.ts'
import { FilesServiceProvider } from './files/service-provider.ts'
import { LoadConfiguration } from './foundation/bootstrap/load-configuration.ts'
import { Console } from './cli/service/console.ts'
import { PromptService } from './cli/service/prompt-service.ts'
import { App } from './cli/components/app.tsx'

const app = Application.configure(process.cwd(), [
  FoundationServiceProvider as never,
  CLIServiceProvider as never,
  GitServiceProvider as never,
  FilesServiceProvider as never,
]).create()

new LoadConfiguration().bootstrap(app)

await app.boot()

const consoleService = app.make<Console>('console')
const promptService = app.make<PromptService>(PromptService as never)
const cachePath = app.make<string>('path.cache')

render(React.createElement(App, { consoleService, promptService, cachePath }))
