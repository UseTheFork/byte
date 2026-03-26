import { simpleGit } from 'simple-git'
import path from 'path'
import { Container } from './container.ts'
import type { ServiceProvider } from '../support/service-provider.ts'
import type { Newable } from '../support/concerns/bootable.ts'

type BootCallback = (app: Application) => void | Promise<void>

export class Application extends Container {
  static token = Symbol('Application')

  private _basePath: string
  private _gitRootPath: string | null = null
  private _booted = false
  private _hasBeenBootstrapped = false
  private _bootingCallbacks: BootCallback[] = []
  private _bootedCallbacks: BootCallback[] = []
  private _registeredProviders: ServiceProvider[] = []

  constructor(basePath?: string) {
    super()
    this._basePath = basePath ?? process.cwd()
    this._registerBaseBindings()
    this._registerBaseServiceProviders()
  }

  private _registerBaseBindings(): void {
    this.instance('app', this)
    this.instance(Application, this)
  }

  private _registerBaseServiceProviders(): void {
    // LogServiceProvider and FoundationServiceProvider registered during bootstrap
  }

  static configure(basePath?: string, providers?: Newable<ServiceProvider>[]): import('./application-builder.ts').ApplicationBuilder {
    const { ApplicationBuilder } = require('./application-builder.ts')
    return new ApplicationBuilder(new Application(basePath)).withKernels().withProviders(providers)
  }

  async initGitRoot(): Promise<void> {
    try {
      const git = simpleGit(this._basePath)
      const root = await git.revparse(['--show-toplevel'])
      this._gitRootPath = root.trim()
    } catch {
      throw new Error(`No Git repository found starting from ${this._basePath}`)
    }
  }

  rootPath(p = ''): string {
    const root = this._gitRootPath ?? this._basePath
    return p ? path.join(root, p) : root
  }

  appPath(p = ''): string {
    const appDir = path.resolve(import.meta.dir, '..')
    return p ? path.join(appDir, p) : appDir
  }

  basePath(p = ''): string {
    return p ? path.join(this._basePath, p) : this._basePath
  }

  configPath(p = ''): string {
    const base = path.join(this.rootPath(), '.byte')
    return p ? path.join(base, p) : base
  }

  cachePath(p = ''): string {
    const base = this.configPath('cache')
    return p ? path.join(base, p) : base
  }

  conventionsPath(p = ''): string {
    const base = this.configPath('conventions')
    return p ? path.join(base, p) : base
  }

  sessionContextPath(p = ''): string {
    const base = this.configPath('session_context')
    return p ? path.join(base, p) : base
  }

  bindPathsInContainer(): void {
    this.instance('path', this.rootPath())
    this.instance('path.app', this.appPath())
    this.instance('path.root', this.rootPath())
    this.instance('path.config', this.configPath())
    this.instance('path.cache', this.cachePath())
    this.instance('path.conventions', this.conventionsPath())
    this.instance('path.session_context', this.sessionContextPath())
  }

  isBooted(): boolean { return this._booted }
  hasBeenBootstrapped(): boolean { return this._hasBeenBootstrapped }

  isDevelopment(): boolean {
    try { const e = this.make<string>('env'); return e === 'development' || e === 'dev' } catch { return false }
  }
  isProduction(): boolean {
    try { return this.make<string>('env') === 'production' } catch { return false }
  }
  override running_unit_tests(): boolean {
    try { return this.make<string>('env') === 'testing' } catch { return false }
  }

  detectEnvironment(callback: (app: Application) => string): string {
    const env = callback(this)
    this.instance('env', env)
    return env
  }

  register(ProviderClass: Newable<ServiceProvider>): ServiceProvider {
    this.singleton(ProviderClass as never, () => new ProviderClass(this))
    const provider = this.make(ProviderClass as never) as ServiceProvider
    provider.register()
    provider.registerServices()
    this.addProvider(provider)
    return provider
  }

  booting(callback: BootCallback): void { this._bootingCallbacks.push(callback) }
  booted(callback: BootCallback): void { this._bootedCallbacks.push(callback) }

  bootstrapWith(bootstrappers: Newable<{ bootstrap(app: Application): void | Promise<void> }>[]): void {
    this._hasBeenBootstrapped = true
    for (const B of bootstrappers) {
      const instance = new B()
      instance.bootstrap(this)
    }
  }

  async boot(): Promise<void> {
    if (this._booted) return

    for (const cb of this._bootingCallbacks) await cb(this)

    for (const provider of this._registeredProviders) {
      await this.bootProvider(provider)
    }

    this._booted = true
    for (const cb of this._bootedCallbacks) await cb(this)
  }

  async bootProvider(provider: ServiceProvider): Promise<void> {
    await provider.boot()
  }

  addProvider(provider: ServiceProvider): void {
    this._registeredProviders.push(provider)
  }

  dispatchTask(promise: Promise<unknown>): Promise<unknown> {
    const { TaskManager } = require('./task-manager.ts')
    return this.make<InstanceType<typeof TaskManager>>(TaskManager).dispatchTask(promise)
  }

  async run(): Promise<number> {
    // Interactive prompt loop — deferred to cli domain migration
    return 0
  }

  terminate(): void {}
}
