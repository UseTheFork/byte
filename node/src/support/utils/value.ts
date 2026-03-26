export function value<T>(val: T | ((...args: unknown[]) => T), ...args: unknown[]): T {
  return typeof val === 'function' ? (val as (...args: unknown[]) => T)(...args) : val
}
