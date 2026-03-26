export function dump(...args: unknown[]): void {
  console.dir(args.length === 1 ? args[0] : args, { depth: null, colors: true })
}

export function dd(...args: unknown[]): never {
  dump(...args)
  process.exit(1)
}
