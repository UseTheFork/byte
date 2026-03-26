# Foundation & Support Node/TS Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the `foundation` and `support` domains of the byte CLI from Python to TypeScript running under Bun, in a parallel `node/` directory at the repo root.

**Architecture:** Mirror the Python Laravel-inspired service provider / DI container pattern. `support` has zero dependencies on other byte domains and is built first. `foundation` depends on `support` and provides the application lifecycle. Domain boundaries are enforced by `index.ts` barrels.

**Tech Stack:** Bun (runtime + test runner), TypeScript strict mode, `js-yaml`, `simple-git`

**Reference:** Python source lives in `src/byte/` — read it when behavior is unclear.

---

## File Map

```
node/
  package.json
  tsconfig.json
  bunfig.toml
  src/
    index.ts
    support/
      index.ts
      array-store.ts
      str.ts
      boundary.ts
      boundary-extractor.ts
      yaml.ts
      service.ts
      service-provider.ts
      concerns/
        index.ts
        bootable.ts          ← IApplication interface also lives here
        eventable.ts         ← Payload class lives here
        configurable.ts
        conditionable.ts
      utils/
        index.ts
        dump.ts
        slugify.ts
        value.ts
        extract-content-from-message.ts
        extract-json-from-message.ts
        get-language-from-filename.ts
        get-last-ai-message.ts
        get-last-message.ts
        list-to-multiline-text.ts
        parse-partial-json.ts
    foundation/
      index.ts
      container.ts
      application.ts
      application-builder.ts
      event-bus.ts
      task-manager.ts
      kernel.ts
      exceptions.ts
      service-provider.ts    ← FoundationServiceProvider
      bootstrap/
        index.ts
        bootstrapper.ts      ← Bootstrapper interface
        register-providers.ts
        load-environment-variables.ts
        load-console-args.ts
        prepare-environment.ts
        load-configuration.ts
        set-context.ts
        handle-exceptions.ts
      console/
        index.ts
        console.ts
  tests/
    support/
      array-store.test.ts
      str.test.ts
      boundary.test.ts
      yaml.test.ts
      utils.test.ts
      concerns.test.ts
      service.test.ts
    foundation/
      container.test.ts
      event-bus.test.ts
      task-manager.test.ts
      application.test.ts
```

**Circular import note:** `support/concerns/bootable.ts` defines the `IApplication` interface. `support/concerns/eventable.ts` defines the `Payload` class. `foundation/` imports from `support/` freely. `support/service.ts` resolves `EventBus` via string key `'event-bus'` through the container — no runtime import of `foundation/` from `support/`.

---

## Task 1: Scaffold the `node/` project

**Files:**
- Create: `node/package.json`
- Create: `node/tsconfig.json`
- Create: `node/bunfig.toml`
- Create: `node/src/index.ts` (empty barrel for now)

- [ ] **Step 1: Create `node/package.json`**

```json
{
  "name": "byte-node",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "start": "bun run src/index.ts",
    "test": "bun test"
  },
  "dependencies": {
    "js-yaml": "^4.1.0",
    "simple-git": "^3.27.0"
  },
  "devDependencies": {
    "@types/js-yaml": "^4.0.9",
    "typescript": "^5.7.0",
    "bun-types": "latest"
  }
}
```

- [ ] **Step 2: Create `node/tsconfig.json`**

```json
{
  "compilerOptions": {
    "lib": ["ESNext"],
    "target": "ESNext",
    "module": "ESNext",
    "moduleDetection": "force",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "skipLibCheck": true,
    "types": ["bun-types"]
  },
  "include": ["src", "tests"]
}
```

- [ ] **Step 3: Create `node/bunfig.toml`**

```toml
[test]
root = "./tests"
```

- [ ] **Step 4: Create `node/src/index.ts`**

```typescript
// Root barrel — re-exports domain public APIs as they are built
export * from './support/index.ts'
```

- [ ] **Step 5: Install dependencies**

Run from `node/`:
```bash
cd node && bun install
```

Expected output: lock file created, `node_modules/` populated.

- [ ] **Step 6: Verify TypeScript config works**

```bash
cd node && bun run --smol src/index.ts
```

Expected: no output, no errors.

- [ ] **Step 7: Commit**

```bash
git add node/
git commit -m "feat: scaffold node/ project with Bun + TypeScript"
```

---

## Task 2: `support/array-store.ts`

**Files:**
- Create: `node/src/support/array-store.ts`
- Create: `node/tests/support/array-store.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `node/tests/support/array-store.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { ArrayStore } from '../../src/support/array-store.ts'

describe('ArrayStore', () => {
  it('starts empty', () => {
    const store = new ArrayStore()
    expect(store.isEmpty()).toBe(true)
    expect(store.isNotEmpty()).toBe(false)
  })

  it('accepts initial data', () => {
    const store = new ArrayStore({ key: 'value' })
    expect(store.get('key')).toBe('value')
  })

  it('add and get', () => {
    const store = new ArrayStore<string>()
    store.add('name', 'byte')
    expect(store.get('name')).toBe('byte')
  })

  it('get returns default when missing', () => {
    const store = new ArrayStore()
    expect(store.get('missing', 'fallback')).toBe('fallback')
  })

  it('all returns underlying data', () => {
    const store = new ArrayStore({ a: 1, b: 2 })
    expect(store.all()).toEqual({ a: 1, b: 2 })
  })

  it('merge combines multiple dicts', () => {
    const store = new ArrayStore<unknown>({ a: 1 })
    store.merge({ b: 2 }, { c: 3 })
    expect(store.all()).toEqual({ a: 1, b: 2, c: 3 })
  })

  it('remove deletes a key', () => {
    const store = new ArrayStore({ a: 1, b: 2 })
    store.remove('a')
    expect(store.all()).toEqual({ b: 2 })
  })

  it('set replaces all data', () => {
    const store = new ArrayStore({ old: true })
    store.set({ new: true })
    expect(store.all()).toEqual({ new: true })
  })

  it('is fluent — add returns self', () => {
    const store = new ArrayStore<number>()
    const result = store.add('x', 1)
    expect(result).toBe(store)
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/support/array-store.test.ts
```

Expected: `Cannot find module '../../src/support/array-store.ts'`

- [ ] **Step 3: Implement `node/src/support/array-store.ts`**

```typescript
export class ArrayStore<T = unknown> {
  private _data: Record<string, T>

  constructor(data?: Record<string, T>) {
    this._data = data ? { ...data } : {}
  }

  add(key: string, value: T): this {
    this._data[key] = value
    return this
  }

  get(key: string, defaultValue?: T): T | undefined {
    return key in this._data ? this._data[key] : defaultValue
  }

  all(): Record<string, T> {
    return this._data
  }

  isEmpty(): boolean {
    return Object.keys(this._data).length === 0
  }

  isNotEmpty(): boolean {
    return !this.isEmpty()
  }

  merge(...dicts: Record<string, T>[]): this {
    for (const dict of dicts) {
      Object.assign(this._data, dict)
    }
    return this
  }

  remove(key: string): this {
    delete this._data[key]
    return this
  }

  set(data: Record<string, T>): this {
    this._data = { ...data }
    return this
  }
}
```

- [ ] **Step 4: Run tests to confirm pass**

```bash
cd node && bun test tests/support/array-store.test.ts
```

Expected: all 9 tests pass.

- [ ] **Step 5: Commit**

```bash
git add node/src/support/array-store.ts node/tests/support/array-store.test.ts
git commit -m "feat(node): add ArrayStore"
```

---

## Task 3: `support/str.ts`

**Files:**
- Create: `node/src/support/str.ts`
- Create: `node/tests/support/str.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `node/tests/support/str.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { Str } from '../../src/support/str.ts'

describe('Str', () => {
  describe('contains', () => {
    it('finds substring', () => expect(Str.contains('hello world', 'world')).toBe(true))
    it('returns false when absent', () => expect(Str.contains('hello', 'xyz')).toBe(false))
    it('handles null haystack', () => expect(Str.contains(null, 'x')).toBe(false))
    it('handles array of needles', () => expect(Str.contains('hello', ['world', 'hello'])).toBe(true))
    it('case insensitive', () => expect(Str.contains('Hello', 'hello', true)).toBe(true))
  })

  describe('snakeCase', () => {
    it('converts PascalCase', () => expect(Str.snakeCase('StartNode')).toBe('start_node'))
    it('converts camelCase', () => expect(Str.snakeCase('myClassName')).toBe('my_class_name'))
  })

  describe('slugify', () => {
    it('converts to slug', () => expect(Str.slugify('Hello World')).toBe('hello-world'))
    it('custom separator', () => expect(Str.slugify('Hello World', '_')).toBe('hello_world'))
  })

  describe('isPattern', () => {
    it('exact match', () => expect(Str.isPattern('hello', 'hello')).toBe(true))
    it('wildcard match', () => expect(Str.isPattern('library/*', 'library/foo')).toBe(true))
    it('no match', () => expect(Str.isPattern('foo', 'bar')).toBe(false))
    it('* matches everything', () => expect(Str.isPattern('*', 'anything')).toBe(true))
  })

  describe('beforeLast', () => {
    it('returns before last occurrence', () => expect(Str.beforeLast('foo:bar:baz', ':')).toBe('foo:bar'))
    it('returns original when not found', () => expect(Str.beforeLast('foo', ':')).toBe('foo'))
  })

  describe('afterLast', () => {
    it('returns after last occurrence', () => expect(Str.afterLast('foo:bar:baz', ':')).toBe('baz'))
    it('returns original when not found', () => expect(Str.afterLast('foo', ':')).toBe('foo'))
  })

  describe('substrCount', () => {
    it('counts occurrences', () => expect(Str.substrCount('aababab', 'ab')).toBe(3))
  })

  describe('classToString', () => {
    it('returns constructor name for class', () => {
      class MyService {}
      expect(Str.classToString(MyService)).toBe('MyService')
    })
    it('returns string as-is', () => expect(Str.classToString('my-key')).toBe('my-key'))
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/support/str.test.ts
```

Expected: `Cannot find module '../../src/support/str.ts'`

- [ ] **Step 3: Implement `node/src/support/str.ts`**

```typescript
export class Str {
  static contains(haystack: string | null, needles: string | string[], ignoreCase = false): boolean {
    if (haystack === null) return false
    const h = ignoreCase ? haystack.toLowerCase() : haystack
    const arr = Array.isArray(needles) ? needles : [needles]
    return arr.some(n => {
      const needle = ignoreCase ? n.toLowerCase() : n
      return needle !== '' && h.includes(needle)
    })
  }

  static snakeCase(value: string): string {
    const s1 = value.replace(/(.)([A-Z][a-z]+)/g, '$1_$2')
    const s2 = s1.replace(/([a-z0-9])([A-Z])/g, '$1_$2')
    return s2.toLowerCase()
  }

  static slugify(text: string, separator = '-'): string {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, separator)
      .replace(new RegExp(`^${separator}|${separator}$`, 'g'), '')
  }

  static isPattern(pattern: string | string[], value: string, ignoreCase = false): boolean {
    const patterns = Array.isArray(pattern) ? pattern : [pattern]
    const v = String(value)
    for (const p of patterns) {
      const ps = String(p)
      if (ps === '*' || ps === v) return true
      if (ignoreCase && ps.toLowerCase() === v.toLowerCase()) return true
      const escaped = ps.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*')
      const flags = ignoreCase ? 'is' : 's'
      if (new RegExp(`^${escaped}$`, flags).test(v)) return true
    }
    return false
  }

  static beforeLast(subject: string, search: string): string {
    if (search === '') return subject
    const pos = subject.lastIndexOf(search)
    return pos === -1 ? subject : subject.slice(0, pos)
  }

  static afterLast(subject: string, search: string): string {
    if (search === '') return subject
    const pos = subject.lastIndexOf(search)
    return pos === -1 ? subject : subject.slice(pos + search.length)
  }

  static substrCount(haystack: string, needle: string, offset = 0, length?: number): number {
    const slice = length !== undefined ? haystack.slice(offset, offset + length) : haystack.slice(offset)
    let count = 0
    let start = 0
    while ((start = slice.indexOf(needle, start)) !== -1) {
      count++
      start += needle.length
    }
    return count
  }

  static classToString(abstract: (new (...args: unknown[]) => unknown) | string): string {
    if (typeof abstract === 'string') return abstract
    return abstract.name
  }

  static classToSnakeCase(abstract: (new (...args: unknown[]) => unknown) | string): string {
    return Str.snakeCase(Str.classToString(abstract))
  }

  static parseCallback(callback: string, defaultMethod?: string): [string, string | undefined] {
    if (Str.contains(callback, ':')) {
      const idx = callback.indexOf(':')
      return [callback.slice(0, idx), callback.slice(idx + 1)]
    }
    return [callback, defaultMethod]
  }

  static lower(value: string): string {
    return value.toLowerCase()
  }
}
```

- [ ] **Step 4: Run tests**

```bash
cd node && bun test tests/support/str.test.ts
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add node/src/support/str.ts node/tests/support/str.test.ts
git commit -m "feat(node): add Str utility class"
```

---

## Task 4: `support/boundary.ts` and `support/boundary-extractor.ts`

**Files:**
- Create: `node/src/support/boundary.ts`
- Create: `node/src/support/boundary-extractor.ts`
- Create: `node/tests/support/boundary.test.ts`

- [ ] **Step 1: Write failing tests**

Create `node/tests/support/boundary.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { Boundary, BoundaryType } from '../../src/support/boundary.ts'
import { BoundaryExtractor } from '../../src/support/boundary-extractor.ts'

describe('BoundaryType', () => {
  it('has string values', () => {
    expect(BoundaryType.ROLE).toBe('role')
    expect(BoundaryType.TASK).toBe('task')
    expect(BoundaryType.FILE).toBe('file')
  })
})

describe('Boundary', () => {
  describe('open', () => {
    it('xml no meta', () => expect(Boundary.open(BoundaryType.ROLE)).toBe('<role>'))
    it('xml with meta', () => expect(Boundary.open(BoundaryType.CONVENTION, { title: 'Guide' })).toBe('<convention title="Guide">'))
    it('markdown no meta', () => expect(Boundary.open(BoundaryType.ROLE, undefined, 'markdown')).toBe('## Role'))
    it('markdown with title', () => expect(Boundary.open(BoundaryType.CONVENTION, { title: 'Guide' }, 'markdown')).toBe('## Convention: Guide'))
    it('throws on invalid format', () => {
      // @ts-expect-error intentional
      expect(() => Boundary.open(BoundaryType.ROLE, undefined, 'html')).toThrow()
    })
  })

  describe('close', () => {
    it('xml', () => expect(Boundary.close(BoundaryType.ROLE)).toBe('</role>'))
    it('markdown returns empty', () => expect(Boundary.close(BoundaryType.ROLE, 'markdown')).toBe(''))
  })

  describe('notice', () => {
    it('xml wraps in comment', () => expect(Boundary.notice('heads up')).toBe('<!-- NOTICE: heads up -->'))
    it('markdown returns content', () => expect(Boundary.notice('heads up', 'markdown')).toBe('heads up'))
  })
})

describe('BoundaryExtractor', () => {
  it('extracts first match', () => {
    const text = '<role>assistant</role>'
    expect(BoundaryExtractor.extract(text, BoundaryType.ROLE)).toBe('assistant')
  })

  it('returns null when not found', () => {
    expect(BoundaryExtractor.extract('<role>x</role>', BoundaryType.TASK)).toBeNull()
  })

  it('extracts all matches', () => {
    const text = '<file>a.ts</file><file>b.ts</file>'
    expect(BoundaryExtractor.extractAll(text, BoundaryType.FILE)).toEqual(['a.ts', 'b.ts'])
  })

  it('handles tags with attributes', () => {
    const text = '<convention title="Guide">content here</convention>'
    expect(BoundaryExtractor.extract(text, BoundaryType.CONVENTION)).toBe('content here')
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/support/boundary.test.ts
```

Expected: module not found errors.

- [ ] **Step 3: Implement `node/src/support/boundary.ts`**

```typescript
export const BoundaryType = {
  ROLE: 'role',
  TASK: 'task',
  USER_INPUT: 'user_input',
  CORE_MANDATES: 'core_mandates',
  GOAL: 'goal',
  RESPONSE_FORMAT: 'response_format',
  RULES: 'rules',
  ERROR: 'error',
  NAME: 'name',
  DESCRIPTION: 'description',
  LOCATION: 'location',
  AVAILABLE_CONVENTIONS: 'available_conventions',
  CONVENTION: 'convention',
  REFERENCE: 'reference',
  SESSION_CONTEXT: 'session_context',
  SHELL_COMMAND: 'shell_command',
  FILE: 'file',
  EDIT_BLOCK: 'operation_block',
  SEARCH: 'search',
  REPLACE: 'replace',
  EXAMPLE: 'example',
  REINFORCEMENT: 'reinforcement',
  PROJECT_HIERARCHY: 'project_hierarchy',
  CONSTRAINTS: 'constraints',
  PLAN: 'agent_plan',
  GUIDELINES: 'guidelines',
  OPERATING_CONSTRAINTS: 'operating_constraints',
  OPERATING_PRINCIPLES: 'operating_principles',
  CRITICAL_REQUIREMENTS: 'response_requirements',
  RECOVERY_STEPS: 'recovery_steps',
  RESPONSE_TEMPLATE: 'response_template',
  CONTEXT: 'context',
  STDOUT: 'stdout',
  STDERR: 'stderr',
  SYSTEM_CONTEXT: 'system_context',
  NOTE: 'note',
  HEADING: 'heading',
  CONVERSATION_HISTORY: 'conversation_history',
  AGENT_MESSAGE: 'agent_message',
  USER_MESSAGE: 'user_message',
} as const

export type BoundaryType = (typeof BoundaryType)[keyof typeof BoundaryType]

type FormatStyle = 'xml' | 'markdown'

export class Boundary {
  static open(type: BoundaryType, meta?: Record<string, string>, format: FormatStyle = 'xml'): string {
    if (format !== 'xml' && format !== 'markdown') throw new Error(`format must be 'xml' or 'markdown', got '${format}'`)
    if (format === 'xml') {
      const metaStr = meta ? ' ' + Object.entries(meta).map(([k, v]) => `${k}="${v}"`).join(' ') : ''
      return `<${type}${metaStr}>`
    }
    const titleStr = meta?.['title'] ? `: ${meta['title']}` : ''
    const label = type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
    return `## ${label}${titleStr}`
  }

  static close(type: BoundaryType, format: FormatStyle = 'xml'): string {
    if (format !== 'xml' && format !== 'markdown') throw new Error(`format must be 'xml' or 'markdown', got '${format}'`)
    return format === 'xml' ? `</${type}>` : ''
  }

  static notice(content: string, format: FormatStyle = 'xml'): string {
    return format === 'xml' ? `<!-- NOTICE: ${content} -->` : content
  }

  static critical(content: string, format: FormatStyle = 'xml'): string {
    return format === 'xml' ? `<!-- **CRITICAL: ${content}** -->` : `**${content}**`
  }

  static important(content: string, format: FormatStyle = 'xml'): string {
    return format === 'xml' ? `<!-- **IMPORTANT: ${content}** -->` : `**${content}**`
  }

  static warning(content: string, format: FormatStyle = 'xml'): string {
    return format === 'xml' ? `<!-- **WARNING:${content}** -->` : `**${content}**`
  }

  static comment(content: string): string {
    return `<!-- \n${content}\n -->`
  }
}
```

- [ ] **Step 4: Implement `node/src/support/boundary-extractor.ts`**

```typescript
import type { BoundaryType } from './boundary.ts'

export class BoundaryExtractor {
  static extract(text: string, boundaryType: BoundaryType): string | null {
    const escaped = boundaryType.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const pattern = new RegExp(`<${escaped}(?:\\s+[^>]*)?>([\\s\\S]+?)<\\/${escaped}>`)
    const match = pattern.exec(text)
    return match ? match[1]!.trim() : null
  }

  static extractAll(text: string, boundaryType: BoundaryType): string[] {
    const escaped = boundaryType.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const pattern = new RegExp(`<${escaped}(?:\\s+[^>]*)?>([\\s\\S]+?)<\\/${escaped}>`, 'g')
    const results: string[] = []
    let match: RegExpExecArray | null
    while ((match = pattern.exec(text)) !== null) {
      results.push(match[1]!.trim())
    }
    return results
  }
}
```

- [ ] **Step 5: Run tests**

```bash
cd node && bun test tests/support/boundary.test.ts
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add node/src/support/boundary.ts node/src/support/boundary-extractor.ts node/tests/support/boundary.test.ts
git commit -m "feat(node): add Boundary, BoundaryType, BoundaryExtractor"
```

---

## Task 5: `support/yaml.ts`

**Files:**
- Create: `node/src/support/yaml.ts`
- Create: `node/tests/support/yaml.test.ts`

- [ ] **Step 1: Write failing tests**

Create `node/tests/support/yaml.test.ts`:

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'bun:test'
import { Yaml } from '../../src/support/yaml.ts'
import { writeFileSync, unlinkSync } from 'fs'

const FIXTURE_PATH = '/tmp/byte-test-yaml.yaml'

beforeAll(() => {
  writeFileSync(FIXTURE_PATH, 'key: value\nnested:\n  inner: 42\n')
})

afterAll(() => {
  unlinkSync(FIXTURE_PATH)
})

describe('Yaml', () => {
  it('load returns parsed data', () => {
    const data = Yaml.load(FIXTURE_PATH)
    expect(data).toEqual({ key: 'value', nested: { inner: 42 } })
  })

  it('load returns null for missing file', () => {
    expect(Yaml.load('/tmp/does-not-exist.yaml')).toBeNull()
  })

  it('loadAsDict returns dict', () => {
    const data = Yaml.loadAsDict(FIXTURE_PATH)
    expect(data['key']).toBe('value')
  })

  it('loadAsDict returns empty dict for missing file', () => {
    expect(Yaml.loadAsDict('/tmp/does-not-exist.yaml')).toEqual({})
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/support/yaml.test.ts
```

Expected: module not found.

- [ ] **Step 3: Implement `node/src/support/yaml.ts`**

```typescript
import { existsSync, readFileSync } from 'fs'
import jsYaml from 'js-yaml'

export class Yaml {
  static load(path: string): unknown {
    if (!existsSync(path)) return null
    const content = readFileSync(path, 'utf-8')
    return jsYaml.load(content)
  }

  static loadAsDict(path: string): Record<string, unknown> {
    const data = Yaml.load(path)
    if (data === null || typeof data !== 'object' || Array.isArray(data)) return {}
    return data as Record<string, unknown>
  }
}
```

- [ ] **Step 4: Run tests**

```bash
cd node && bun test tests/support/yaml.test.ts
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add node/src/support/yaml.ts node/tests/support/yaml.test.ts
git commit -m "feat(node): add Yaml utility"
```

---

## Task 6: `support/utils/`

**Files:**
- Create: `node/src/support/utils/value.ts`
- Create: `node/src/support/utils/slugify.ts`
- Create: `node/src/support/utils/list-to-multiline-text.ts`
- Create: `node/src/support/utils/parse-partial-json.ts`
- Create: `node/src/support/utils/dump.ts`
- Create: `node/src/support/utils/extract-content-from-message.ts`
- Create: `node/src/support/utils/extract-json-from-message.ts`
- Create: `node/src/support/utils/get-language-from-filename.ts`
- Create: `node/src/support/utils/get-last-ai-message.ts`
- Create: `node/src/support/utils/get-last-message.ts`
- Create: `node/src/support/utils/index.ts`
- Create: `node/tests/support/utils.test.ts`

- [ ] **Step 1: Write failing tests**

Create `node/tests/support/utils.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { value } from '../../src/support/utils/value.ts'
import { slugify } from '../../src/support/utils/slugify.ts'
import { listToMultilineText } from '../../src/support/utils/list-to-multiline-text.ts'
import { parsePartialJson } from '../../src/support/utils/parse-partial-json.ts'

describe('value', () => {
  it('returns value as-is if not callable', () => expect(value(42)).toBe(42))
  it('calls callable and returns result', () => expect(value(() => 'hello')).toBe('hello'))
  it('passes args to callable', () => expect(value((x: number) => x * 2, 5)).toBe(10))
})

describe('slugify', () => {
  it('basic slugify', () => expect(slugify('Hello World')).toBe('hello-world'))
  it('custom separator', () => expect(slugify('Hello World', '_')).toBe('hello_world'))
  it('strips leading/trailing separators', () => expect(slugify('--hello--')).toBe('hello'))
})

describe('listToMultilineText', () => {
  it('joins with newline', () => expect(listToMultilineText(['a', 'b', 'c'])).toBe('a\nb\nc'))
  it('custom separator', () => expect(listToMultilineText(['a', 'b'], ', ')).toBe('a, b'))
  it('empty list returns empty string', () => expect(listToMultilineText([])).toBe(''))
})

describe('parsePartialJson', () => {
  it('parses valid JSON', () => expect(parsePartialJson('{"a":1}')).toEqual({ a: 1 }))
  it('parses partial JSON missing closing brace', () => expect(parsePartialJson('{"a":1')).toEqual({ a: 1 }))
  it('parses partial JSON missing closing bracket', () => expect(parsePartialJson('["a","b"')).toEqual(['a', 'b']))
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/support/utils.test.ts
```

Expected: module not found errors.

- [ ] **Step 3: Implement all utility files**

Create `node/src/support/utils/value.ts`:
```typescript
export function value<T>(val: T | ((...args: unknown[]) => T), ...args: unknown[]): T {
  return typeof val === 'function' ? (val as (...args: unknown[]) => T)(...args) : val
}
```

Create `node/src/support/utils/slugify.ts`:
```typescript
export function slugify(text: string, separator = '-'): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, separator)
    .replace(new RegExp(`^${separator}|${separator}$`, 'g'), '')
}
```

Create `node/src/support/utils/list-to-multiline-text.ts`:
```typescript
export function listToMultilineText(lines: string[], separator = '\n'): string {
  if (!lines.length) return ''
  return lines.join(separator)
}
```

Create `node/src/support/utils/parse-partial-json.ts`:
```typescript
export function parsePartialJson(s: string): unknown {
  try { return JSON.parse(s) } catch { /* continue */ }

  const newChars: string[] = []
  const stack: string[] = []
  let insideString = false
  let escaped = false

  for (const char of s) {
    let newChar = char
    if (insideString) {
      if (char === '"' && !escaped) insideString = false
      else if (char === '\n' && !escaped) newChar = '\\n'
      else if (char === '\\') escaped = !escaped
      else escaped = false
    } else if (char === '"') {
      insideString = true; escaped = false
    } else if (char === '{') stack.push('}')
    else if (char === '[') stack.push(']')
    else if (char === '}' || char === ']') {
      if (stack.length && stack[stack.length - 1] === char) stack.pop()
      else return null
    }
    newChars.push(newChar)
  }

  if (insideString) { if (escaped) newChars.pop(); newChars.push('"') }
  stack.reverse()

  while (newChars.length) {
    try { return JSON.parse(newChars.join('') + stack.join('')) } catch { newChars.pop() }
  }
  return JSON.parse(s)
}
```

Create `node/src/support/utils/dump.ts`:
```typescript
export function dump(...args: unknown[]): void {
  console.dir(args.length === 1 ? args[0] : args, { depth: null, colors: true })
}

export function dd(...args: unknown[]): never {
  dump(...args)
  process.exit(1)
}
```

Create `node/src/support/utils/extract-content-from-message.ts`:
```typescript
export function extractContentFromMessage(message: { content: string | Array<{ text?: string }> }): string {
  if (typeof message.content === 'string') return message.content
  if (Array.isArray(message.content) && message.content.length > 0) {
    return message.content[0]?.text ?? ''
  }
  throw new Error(`Unable to extract content from message: ${typeof message.content}`)
}
```

Create `node/src/support/utils/extract-json-from-message.ts`:
```typescript
export function extractJsonFromMessage(message: { content: string | Array<{ partial_json?: string }> }): string | null {
  if (Array.isArray(message.content) && message.content.length > 0) {
    return message.content[0]?.partial_json ?? null
  }
  return null
}
```

Create `node/src/support/utils/get-language-from-filename.ts`:
```typescript
const EXTENSION_MAP: Record<string, string> = {
  ts: 'typescript', tsx: 'typescript', js: 'javascript', jsx: 'javascript',
  py: 'python', rb: 'ruby', rs: 'rust', go: 'go', java: 'java',
  cs: 'csharp', cpp: 'cpp', c: 'c', h: 'c', php: 'php',
  swift: 'swift', kt: 'kotlin', sh: 'bash', bash: 'bash',
  zsh: 'bash', md: 'markdown', yaml: 'yaml', yml: 'yaml',
  json: 'json', toml: 'toml', html: 'html', css: 'css',
  scss: 'scss', sql: 'sql', xml: 'xml',
}

export function getLanguageFromFilename(filename: string): string | null {
  const ext = filename.split('.').pop()?.toLowerCase()
  if (!ext) return null
  return EXTENSION_MAP[ext] ?? null
}
```

Create `node/src/support/utils/get-last-ai-message.ts`:
```typescript
export function getLastAiMessage<T extends { _getType?(): string; type?: string }>(messages: T[]): T {
  if (!messages.length) throw new Error('No messages found in empty list')
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i]!
    if (msg._getType?.() === 'ai' || msg.type === 'ai') return msg
  }
  throw new Error('No AIMessage found in messages list')
}
```

Create `node/src/support/utils/get-last-message.ts`:
```typescript
export function getLastMessage<T>(state: T[] | { scratch_messages?: T[] }): T {
  if (Array.isArray(state)) {
    if (!state.length) throw new Error('No messages found in empty list state')
    return state[state.length - 1]!
  }
  const messages = state.scratch_messages
  if (messages?.length) return messages[messages.length - 1]!
  throw new Error(`No messages found in input state: ${JSON.stringify(state)}`)
}
```

- [ ] **Step 4: Create `node/src/support/utils/index.ts`**

```typescript
export { value } from './value.ts'
export { slugify } from './slugify.ts'
export { listToMultilineText } from './list-to-multiline-text.ts'
export { parsePartialJson } from './parse-partial-json.ts'
export { dump, dd } from './dump.ts'
export { extractContentFromMessage } from './extract-content-from-message.ts'
export { extractJsonFromMessage } from './extract-json-from-message.ts'
export { getLanguageFromFilename } from './get-language-from-filename.ts'
export { getLastAiMessage } from './get-last-ai-message.ts'
export { getLastMessage } from './get-last-message.ts'
```

- [ ] **Step 5: Run tests**

```bash
cd node && bun test tests/support/utils.test.ts
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add node/src/support/utils/
git commit -m "feat(node): add support/utils"
```

---

## Task 7: `support/concerns/` — `IApplication`, `Bootable`, `Eventable`, `Configurable`, `Conditionable`

**Files:**
- Create: `node/src/support/concerns/bootable.ts` (contains `IApplication` interface)
- Create: `node/src/support/concerns/eventable.ts` (contains `Payload` class)
- Create: `node/src/support/concerns/configurable.ts`
- Create: `node/src/support/concerns/conditionable.ts`
- Create: `node/src/support/concerns/index.ts`
- Create: `node/tests/support/concerns.test.ts`

- [ ] **Step 1: Write failing tests**

Create `node/tests/support/concerns.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { Bootable, type IApplication } from '../../src/support/concerns/bootable.ts'
import { Payload } from '../../src/support/concerns/eventable.ts'
import { Configurable } from '../../src/support/concerns/configurable.ts'
import { Conditionable } from '../../src/support/concerns/conditionable.ts'
import { ArrayStore } from '../../src/support/array-store.ts'

const mockApp = {} as IApplication

describe('Bootable', () => {
  it('boot() is called once via ensureBooted()', () => {
    let callCount = 0
    class MyService extends Bootable {
      override boot() { callCount++ }
    }
    const svc = new MyService(mockApp)
    svc.ensureBooted()
    svc.ensureBooted() // second call should be no-op
    expect(callCount).toBe(1)
  })

  it('bootConcerns() is called before boot()', () => {
    const order: string[] = []
    class MyService extends Bootable {
      protected override bootConcerns() { order.push('concerns') }
      override boot() { order.push('boot') }
    }
    new MyService(mockApp).ensureBooted()
    expect(order).toEqual(['concerns', 'boot'])
  })
})

describe('Payload', () => {
  it('wraps data in ArrayStore', () => {
    const p = new Payload('test_event', { key: 'val' })
    expect(p.get('key')).toBe('val')
  })

  it('accepts ArrayStore directly', () => {
    const store = new ArrayStore<string>({ x: 'y' })
    const p = new Payload('test_event', store as ArrayStore<unknown>)
    expect(p.get('x')).toBe('y')
  })

  it('set returns self for chaining', () => {
    const p = new Payload('test')
    const result = p.set('a', 1)
    expect(result).toBe(p)
    expect(p.get('a')).toBe(1)
  })

  it('update merges multiple keys', () => {
    const p = new Payload('test')
    p.update({ a: 1, b: 2 })
    expect(p.get('a')).toBe(1)
    expect(p.get('b')).toBe(2)
  })
})

describe('Configurable', () => {
  it('config() returns an ArrayStore', () => {
    class MyService extends Configurable {}
    const svc = new MyService()
    expect(svc.config()).toBeInstanceOf(ArrayStore)
  })

  it('config persists across calls', () => {
    class MyService extends Configurable {}
    const svc = new MyService()
    svc.config().add('key', 'val')
    expect(svc.config().get('key')).toBe('val')
  })
})

describe('Conditionable', () => {
  it('when executes callback when condition truthy', () => {
    let called = false
    class MyObj extends Conditionable {}
    new MyObj().when(true, () => { called = true })
    expect(called).toBe(true)
  })

  it('when skips callback when condition falsy', () => {
    let called = false
    class MyObj extends Conditionable {}
    new MyObj().when(false, () => { called = true })
    expect(called).toBe(false)
  })

  it('unless executes callback when condition falsy', () => {
    let called = false
    class MyObj extends Conditionable {}
    new MyObj().unless(false, () => { called = true })
    expect(called).toBe(true)
  })

  it('when returns self for chaining', () => {
    class MyObj extends Conditionable {}
    const obj = new MyObj()
    expect(obj.when(true, () => {})).toBe(obj)
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/support/concerns.test.ts
```

Expected: module not found errors.

- [ ] **Step 3: Implement `node/src/support/concerns/bootable.ts`**

```typescript
/**
 * IApplication is defined here (in support/) to avoid circular imports.
 * Application (foundation/) implements this interface.
 * ServiceProvider (support/) depends on this interface.
 */
export interface IApplication {
  make<T = unknown>(abstract: Newable<T> | string): T
  singleton(cls: Newable<unknown>, factory?: () => unknown): void
  bind(cls: Newable<unknown>, factory?: () => unknown): void
  instance(abstract: Newable<unknown> | string, value: unknown): unknown
  running_unit_tests(): boolean
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Newable<T> = new (...args: any[]) => T

export abstract class Bootable {
  protected app: IApplication
  private _isBooted = false

  constructor(app: IApplication) {
    this.app = app
  }

  ensureBooted(): void {
    if (this._isBooted) return
    this.bootConcerns()
    this.boot()
    this._isBooted = true
  }

  /** Override in subclasses to call per-concern boot methods. */
  protected bootConcerns(): void {}

  /** Override to perform initialization after construction. */
  boot(): void {}
}
```

- [ ] **Step 4: Implement `node/src/support/concerns/eventable.ts`**

```typescript
import { ArrayStore } from '../array-store.ts'

export class Payload {
  readonly eventType: string
  readonly timestamp: number
  readonly data: ArrayStore<unknown>

  constructor(
    eventType: string,
    data?: ArrayStore<unknown> | Record<string, unknown>,
    timestamp?: number,
  ) {
    this.eventType = eventType
    this.timestamp = timestamp ?? Date.now()
    if (data instanceof ArrayStore) {
      this.data = data
    } else if (data && typeof data === 'object') {
      this.data = new ArrayStore(data)
    } else {
      this.data = new ArrayStore()
    }
  }

  get(key: string, defaultValue?: unknown): unknown {
    return this.data.get(key, defaultValue)
  }

  set(key: string, value: unknown): this {
    this.data.add(key, value)
    return this
  }

  update(updates: Record<string, unknown>): this {
    this.data.merge(updates)
    return this
  }
}

/** Implemented by Service — requires this.app to be available (from Bootable). */
export interface Eventable {
  emit(payload: Payload): Promise<Payload>
}
```

- [ ] **Step 5: Implement `node/src/support/concerns/configurable.ts`**

```typescript
import { ArrayStore } from '../array-store.ts'

export abstract class Configurable {
  private _config = new ArrayStore<unknown>()

  config(): ArrayStore<unknown> {
    return this._config
  }

  protected bootConfigurable(): void {}
}
```

- [ ] **Step 6: Implement `node/src/support/concerns/conditionable.ts`**

```typescript
import { value } from '../utils/value.ts'

export abstract class Conditionable {
  when<V>(
    condition: V | (() => V),
    callback: (self: this, val: V) => void,
    defaultCb?: (self: this, val: V) => void,
  ): this {
    const val = value(condition) as V
    if (val) callback(this, val)
    else if (defaultCb) defaultCb(this, val)
    return this
  }

  unless<V>(
    condition: V | (() => V),
    callback: (self: this, val: V) => void,
    defaultCb?: (self: this, val: V) => void,
  ): this {
    const val = value(condition) as V
    if (!val) callback(this, val)
    else if (defaultCb) defaultCb(this, val)
    return this
  }
}
```

- [ ] **Step 7: Create `node/src/support/concerns/index.ts`**

```typescript
export { Bootable, type IApplication, type Newable } from './bootable.ts'
export { Payload, type Eventable } from './eventable.ts'
export { Configurable } from './configurable.ts'
export { Conditionable } from './conditionable.ts'
```

- [ ] **Step 8: Run tests**

```bash
cd node && bun test tests/support/concerns.test.ts
```

Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
git add node/src/support/concerns/ node/tests/support/concerns.test.ts
git commit -m "feat(node): add support/concerns (Bootable, Payload, Eventable, Configurable, Conditionable)"
```

---

## Task 8: `support/service.ts` and `support/service-provider.ts`

**Files:**
- Create: `node/src/support/service.ts`
- Create: `node/src/support/service-provider.ts`
- Create: `node/tests/support/service.test.ts`

- [ ] **Step 1: Write failing tests**

Create `node/tests/support/service.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { Service } from '../../src/support/service.ts'
import { ServiceProvider } from '../../src/support/service-provider.ts'
import type { IApplication } from '../../src/support/concerns/bootable.ts'

const mockApp = {
  make: () => ({ on: () => {}, emit: async (p: unknown) => p }),
  singleton: () => {},
  bind: () => {},
  instance: () => {},
  running_unit_tests: () => false,
} as unknown as IApplication

describe('Service', () => {
  it('run() calls validate then handle', async () => {
    const order: string[] = []
    class TestService extends Service {
      override async validate() { order.push('validate'); return true }
      override async handle() { order.push('handle') }
    }
    const svc = new TestService(mockApp)
    await svc.run()
    expect(order).toEqual(['validate', 'handle'])
  })

  it('validate() returns true by default', async () => {
    class TestService extends Service {}
    const svc = new TestService(mockApp)
    expect(await svc.validate()).toBe(true)
  })
})

describe('ServiceProvider', () => {
  it('services() returns empty array by default', () => {
    class TestProvider extends ServiceProvider {}
    const p = new TestProvider(mockApp)
    expect(p.services()).toEqual([])
  })

  it('commands() returns empty array by default', () => {
    class TestProvider extends ServiceProvider {}
    const p = new TestProvider(mockApp)
    expect(p.commands()).toEqual([])
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/support/service.test.ts
```

Expected: module not found errors.

- [ ] **Step 3: Implement `node/src/support/service.ts`**

Note: `Service.emit()` resolves `EventBus` via the string key `'event-bus'` to avoid a circular import from `support/` into `foundation/`. The actual `EventBus` class is registered under this key by `FoundationServiceProvider`.

```typescript
import { Bootable } from './concerns/bootable.ts'
import type { Eventable } from './concerns/eventable.ts'
import { Payload } from './concerns/eventable.ts'

export abstract class Service extends Bootable implements Eventable {
  async validate(): Promise<boolean> {
    return true
  }

  async handle(..._args: unknown[]): Promise<unknown> {
    return undefined
  }

  async run(...args: unknown[]): Promise<unknown> {
    await this.validate()
    return this.handle(...args)
  }

  async emit(payload: Payload): Promise<Payload> {
    const eventBus = this.app.make<{ emit(p: Payload): Promise<Payload> }>('event-bus')
    return eventBus.emit(payload)
  }
}
```

- [ ] **Step 4: Implement `node/src/support/service-provider.ts`**

```typescript
import type { IApplication, Newable } from './concerns/bootable.ts'
import type { Service } from './service.ts'

export abstract class ServiceProvider {
  protected app: IApplication

  constructor(app: IApplication) {
    this.app = app
  }

  services(): Newable<Service>[] {
    return []
  }

  commands(): Newable<unknown>[] {
    return []
  }

  registerServices(): void {
    for (const serviceClass of this.services()) {
      this.app.singleton(serviceClass)
    }
  }

  registerCommands(): void {
    // Command registry integration deferred to cli domain migration
  }

  register(): void {}

  async boot(): Promise<void> {}

  async shutdown(_app: IApplication): Promise<void> {}
}
```

- [ ] **Step 5: Run tests**

```bash
cd node && bun test tests/support/service.test.ts
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add node/src/support/service.ts node/src/support/service-provider.ts node/tests/support/service.test.ts
git commit -m "feat(node): add Service and ServiceProvider base classes"
```

---

## Task 9: `support/index.ts` barrel

**Files:**
- Create: `node/src/support/index.ts`

- [ ] **Step 1: Create the support barrel**

Create `node/src/support/index.ts`:

```typescript
export { ArrayStore } from './array-store.ts'
export { Boundary, BoundaryType } from './boundary.ts'
export { BoundaryExtractor } from './boundary-extractor.ts'
export { Service } from './service.ts'
export { ServiceProvider } from './service-provider.ts'
export { Str } from './str.ts'
export { Yaml } from './yaml.ts'
export * from './concerns/index.ts'
export * from './utils/index.ts'
```

- [ ] **Step 2: Verify barrel compiles**

```bash
cd node && bun run --smol -e "import * as s from './src/support/index.ts'; console.log(Object.keys(s).length + ' exports')"
```

Expected: prints a number of exports (no errors).

- [ ] **Step 3: Update root barrel `node/src/index.ts`**

```typescript
export * from './support/index.ts'
```

- [ ] **Step 4: Commit**

```bash
git add node/src/support/index.ts node/src/index.ts
git commit -m "feat(node): add support/index.ts barrel"
```

---

## Task 10: `foundation/container.ts`

**Files:**
- Create: `node/src/foundation/container.ts`
- Create: `node/tests/foundation/container.test.ts`

- [ ] **Step 1: Write failing tests**

Create `node/tests/foundation/container.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { Container } from '../../src/foundation/container.ts'

class ServiceA {
  static token = Symbol('ServiceA')
  value = 'a'
}
class ServiceB {
  static token = Symbol('ServiceB')
  constructor(public dep: ServiceA) {}
}

describe('Container', () => {
  it('instance() stores and make() retrieves by string key', () => {
    const c = new Container()
    c.instance('app', { name: 'byte' })
    expect(c.make<{ name: string }>('app').name).toBe('byte')
  })

  it('singleton() creates once, caches', () => {
    const c = new Container()
    let count = 0
    c.singleton(ServiceA, () => { count++; return new ServiceA() })
    c.make(ServiceA)
    c.make(ServiceA)
    expect(count).toBe(1)
  })

  it('bind() creates new instance each time', () => {
    const c = new Container()
    c.bind(ServiceA, () => new ServiceA())
    const a1 = c.make(ServiceA)
    const a2 = c.make(ServiceA)
    expect(a1).not.toBe(a2)
  })

  it('bound() returns true when registered', () => {
    const c = new Container()
    c.instance('env', 'testing')
    expect(c.bound('env')).toBe(true)
    expect(c.bound('missing')).toBe(false)
  })

  it('flush() clears all state', () => {
    const c = new Container()
    c.instance('env', 'test')
    c.flush()
    expect(c.bound('env')).toBe(false)
  })

  it('make() by class uses token as key', () => {
    const c = new Container()
    const instance = new ServiceA()
    c.instance(ServiceA, instance)
    expect(c.make(ServiceA)).toBe(instance)
  })

  it('get() and set() work like make/instance', () => {
    const c = new Container()
    c.set('key', 'value')
    expect(c.get('key')).toBe('value')
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/foundation/container.test.ts
```

Expected: module not found.

- [ ] **Step 3: Implement `node/src/foundation/container.ts`**

```typescript
import type { IApplication, Newable } from '../support/concerns/bootable.ts'

type TokenKey = symbol | string

interface Tokenable<T> extends Newable<T> {
  token: symbol
}

function getKey(abstract: Tokenable<unknown> | string): TokenKey {
  if (typeof abstract === 'string') return abstract
  return abstract.token
}

type Factory<T = unknown> = () => T

export class Container implements IApplication {
  protected _singletons = new Map<TokenKey, Factory>()
  protected _transients = new Map<TokenKey, Factory>()
  protected _instances = new Map<TokenKey, unknown>()

  bind<T>(cls: Tokenable<T>, factory?: () => T): void {
    const key = getKey(cls)
    this._transients.set(key, factory ?? (() => new cls()))
  }

  singleton<T>(cls: Tokenable<T>, factory?: () => T): void {
    const key = getKey(cls)
    this._singletons.set(key, factory ?? (() => new cls()))
  }

  instance<T>(abstract: Tokenable<T> | string, value: T): T {
    const key = typeof abstract === 'string' ? abstract : getKey(abstract as Tokenable<T>)
    this._instances.set(key, value)
    return value
  }

  make<T = unknown>(abstract: Tokenable<T> | string): T {
    const key = typeof abstract === 'string' ? abstract : getKey(abstract as Tokenable<T>)

    if (this._instances.has(key)) return this._instances.get(key) as T

    if (this._singletons.has(key)) {
      const instance = (this._singletons.get(key) as Factory<T>)()
      this._instances.set(key, instance)
      return instance
    }

    if (this._transients.has(key)) {
      return (this._transients.get(key) as Factory<T>)()
    }

    if (typeof abstract !== 'string') {
      return new (abstract as Tokenable<T>)()
    }

    throw new Error(`No binding found for ${String(key)}`)
  }

  bound(abstract: Tokenable<unknown> | string): boolean {
    const key = typeof abstract === 'string' ? abstract : getKey(abstract as Tokenable<unknown>)
    return this._instances.has(key) || this._singletons.has(key) || this._transients.has(key)
  }

  flush(): void {
    this._singletons.clear()
    this._transients.clear()
    this._instances.clear()
  }

  get<T = unknown>(key: string): T {
    return this.make<T>(key)
  }

  set(key: string, value: unknown): void {
    this.instance(key, value)
  }

  running_unit_tests(): boolean {
    try { return this.make<string>('env') === 'testing' } catch { return false }
  }
}
```

- [ ] **Step 4: Run tests**

```bash
cd node && bun test tests/foundation/container.test.ts
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add node/src/foundation/container.ts node/tests/foundation/container.test.ts
git commit -m "feat(node): add Container DI container"
```

---

## Task 11: `foundation/event-bus.ts`

**Files:**
- Create: `node/src/foundation/event-bus.ts`
- Create: `node/tests/foundation/event-bus.test.ts`

- [ ] **Step 1: Write failing tests**

Create `node/tests/foundation/event-bus.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { EventBus, EventType } from '../../src/foundation/event-bus.ts'
import { Payload } from '../../src/support/concerns/eventable.ts'
import type { IApplication } from '../../src/support/concerns/bootable.ts'

const mockApp = { make: () => ({ exception: () => {} }), singleton: () => {}, bind: () => {}, instance: () => {}, running_unit_tests: () => false } as unknown as IApplication

describe('EventType', () => {
  it('has string values', () => {
    expect(EventType.POST_BOOT).toBe('post_boot')
    expect(EventType.FILE_ADDED).toBe('file_added')
  })
})

describe('EventBus', () => {
  it('emits to registered listener', async () => {
    const bus = new EventBus(mockApp)
    const received: Payload[] = []
    bus.on(EventType.TEST, (p: Payload) => { received.push(p); return p })
    const payload = new Payload(EventType.TEST, { key: 'val' })
    await bus.emit(payload)
    expect(received.length).toBe(1)
    expect(received[0]!.get('key')).toBe('val')
  })

  it('returns payload unchanged when no listeners', async () => {
    const bus = new EventBus(mockApp)
    const payload = new Payload(EventType.TEST)
    const result = await bus.emit(payload)
    expect(result).toBe(payload)
  })

  it('chains multiple listeners sequentially', async () => {
    const bus = new EventBus(mockApp)
    const order: number[] = []
    bus.on(EventType.TEST, (p: Payload) => { order.push(1); return p })
    bus.on(EventType.TEST, async (p: Payload) => { order.push(2); return p })
    await bus.emit(new Payload(EventType.TEST))
    expect(order).toEqual([1, 2])
  })

  it('listener can transform payload', async () => {
    const bus = new EventBus(mockApp)
    bus.on(EventType.TEST, (p: Payload) => { p.set('added', true); return p })
    const result = await bus.emit(new Payload(EventType.TEST))
    expect(result.get('added')).toBe(true)
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/foundation/event-bus.test.ts
```

Expected: module not found.

- [ ] **Step 3: Implement `node/src/foundation/event-bus.ts`**

```typescript
import type { IApplication } from '../support/concerns/bootable.ts'
import { Payload } from '../support/concerns/eventable.ts'

export const EventType = {
  POST_BOOT: 'post_boot',
  PRE_PROMPT_TOOLKIT: 'pre_prompt_toolkit',
  POST_PROMPT_TOOLKIT: 'post_prompt_toolkit',
  GENERATE_FILE_CONTEXT: 'generate_file_context',
  FILE_ADDED: 'file_added',
  FILE_CHANGED: 'file_changed',
  PRE_AGENT_EXECUTION: 'pre_agent_execution',
  POST_AGENT_EXECUTION: 'post_agent_execution',
  END_NODE: 'end_node',
  PRE_ASSISTANT_NODE: 'pre_assistant_node',
  POST_ASSISTANT_NODE: 'post_assistant_node',
  GATHER_AVAILABLE_CONVENTIONS: 'gather_available_conventions',
  GATHER_PROJECT_CONTEXT: 'gather_project_context',
  GATHER_REINFORCEMENT: 'gather_reinforcement',
  TEST: 'test',
} as const

export type EventType = (typeof EventType)[keyof typeof EventType]

type EventListener = (payload: Payload) => Payload | Promise<Payload> | void | Promise<void>

export class EventBus {
  static token = Symbol('EventBus')
  private _listeners = new Map<string, EventListener[]>()

  constructor(private app: IApplication) {}

  on(eventName: string, callback: EventListener): void {
    if (!this._listeners.has(eventName)) this._listeners.set(eventName, [])
    this._listeners.get(eventName)!.push(callback)
  }

  async emit(payload: Payload): Promise<Payload> {
    const listeners = this._listeners.get(payload.eventType)
    if (!listeners?.length) return payload

    let current = payload
    for (const listener of listeners) {
      try {
        const result = await listener(current)
        if (result !== undefined) current = result
      } catch (e) {
        console.error(`Error in event listener for '${payload.eventType}':`, e)
      }
    }
    return current
  }
}
```

- [ ] **Step 4: Run tests**

```bash
cd node && bun test tests/foundation/event-bus.test.ts
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add node/src/foundation/event-bus.ts node/tests/foundation/event-bus.test.ts
git commit -m "feat(node): add EventBus and EventType"
```

---

## Task 12: `foundation/task-manager.ts`

**Files:**
- Create: `node/src/foundation/task-manager.ts`
- Create: `node/tests/foundation/task-manager.test.ts`

- [ ] **Step 1: Write failing tests**

Create `node/tests/foundation/task-manager.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { TaskManager } from '../../src/foundation/task-manager.ts'
import type { IApplication } from '../../src/support/concerns/bootable.ts'

const mockApp = { make: () => ({}), singleton: () => {}, bind: () => {}, instance: () => {}, running_unit_tests: () => false } as unknown as IApplication

describe('TaskManager', () => {
  it('dispatchTask returns a promise', () => {
    const tm = new TaskManager(mockApp)
    const result = tm.dispatchTask(Promise.resolve('done'))
    expect(result).toBeInstanceOf(Promise)
  })

  it('startTask registers a named task', () => {
    const tm = new TaskManager(mockApp)
    tm.startTask('test', Promise.resolve())
    expect(tm.hasTask('test')).toBe(true)
  })

  it('stopTask removes the task', () => {
    const tm = new TaskManager(mockApp)
    tm.startTask('test', Promise.resolve())
    tm.stopTask('test')
    expect(tm.hasTask('test')).toBe(false)
  })

  it('shutdown resolves all tasks', async () => {
    const tm = new TaskManager(mockApp)
    tm.startTask('a', Promise.resolve('done'))
    await tm.shutdown()
    expect(tm.hasTask('a')).toBe(false)
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/foundation/task-manager.test.ts
```

Expected: module not found.

- [ ] **Step 3: Implement `node/src/foundation/task-manager.ts`**

```typescript
import { Bootable } from '../support/concerns/bootable.ts'
import type { IApplication } from '../support/concerns/bootable.ts'

export class TaskManager extends Bootable {
  static token = Symbol('TaskManager')
  private _tasks = new Map<string, Promise<unknown>>()

  constructor(app: IApplication) {
    super(app)
  }

  startTask(name: string, promise: Promise<unknown>): Promise<unknown> {
    this._tasks.set(name, promise.finally(() => this._tasks.delete(name)))
    return this._tasks.get(name)!
  }

  stopTask(name: string): void {
    this._tasks.delete(name)
  }

  hasTask(name: string): boolean {
    return this._tasks.has(name)
  }

  dispatchTask(promise: Promise<unknown>): Promise<unknown> {
    const name = `task_${Math.random().toString(36).slice(2, 10)}`
    return this.startTask(name, promise)
  }

  async shutdown(): Promise<void> {
    await Promise.allSettled(this._tasks.values())
    this._tasks.clear()
  }
}
```

- [ ] **Step 4: Run tests**

```bash
cd node && bun test tests/foundation/task-manager.test.ts
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add node/src/foundation/task-manager.ts node/tests/foundation/task-manager.test.ts
git commit -m "feat(node): add TaskManager"
```

---

## Task 13: `foundation/application.ts` and `foundation/application-builder.ts`

**Files:**
- Create: `node/src/foundation/exceptions.ts`
- Create: `node/src/foundation/application.ts`
- Create: `node/src/foundation/application-builder.ts`
- Create: `node/tests/foundation/application.test.ts`

- [ ] **Step 1: Write failing tests**

Create `node/tests/foundation/application.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { Application } from '../../src/foundation/application.ts'
import path from 'path'

const testBasePath = path.resolve(process.cwd(), '..')

describe('Application', () => {
  it('create() returns an Application instance', () => {
    const app = Application.configure(testBasePath).create()
    expect(app).toBeInstanceOf(Application)
  })

  it('rootPath() returns a string path', () => {
    const app = Application.configure(testBasePath).create()
    expect(typeof app.rootPath()).toBe('string')
  })

  it('configPath() returns path ending in .byte', () => {
    const app = Application.configure(testBasePath).create()
    expect(app.configPath()).toContain('.byte')
  })

  it('instance() and make() round-trip', () => {
    const app = Application.configure(testBasePath).create()
    app.instance('test-key', 'hello')
    expect(app.make('test-key')).toBe('hello')
  })

  it('is not booted initially', () => {
    const app = Application.configure(testBasePath).create()
    expect(app.isBooted()).toBe(false)
  })

  it('isDevelopment() works after env is set', () => {
    const app = Application.configure(testBasePath).create()
    app.instance('env', 'development')
    expect(app.isDevelopment()).toBe(true)
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd node && bun test tests/foundation/application.test.ts
```

Expected: module not found.

- [ ] **Step 3: Create `node/src/foundation/exceptions.ts`**

```typescript
export class ByteException extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ByteException'
  }
}
```

- [ ] **Step 4: Implement `node/src/foundation/application.ts`**

```typescript
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
    this.singleton(ProviderClass as never)
    const provider = this.make(ProviderClass as never) as ServiceProvider
    provider.register()
    provider.registerServices()
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
```

- [ ] **Step 5: Implement `node/src/foundation/application-builder.ts`**

```typescript
import type { Application } from './application.ts'
import type { Newable } from '../support/concerns/bootable.ts'
import type { ServiceProvider } from '../support/service-provider.ts'

export class ApplicationBuilder {
  constructor(private _application: Application) {}

  withKernels(): this {
    // Kernel singleton registered here once Kernel is implemented
    return this
  }

  withProviders(providers?: Newable<ServiceProvider>[]): this {
    if (providers?.length) {
      for (const P of providers) this._application.register(P)
    }
    return this
  }

  create(): Application {
    return this._application
  }
}
```

- [ ] **Step 6: Run tests**

```bash
cd node && bun test tests/foundation/application.test.ts
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add node/src/foundation/exceptions.ts node/src/foundation/application.ts node/src/foundation/application-builder.ts node/tests/foundation/application.test.ts
git commit -m "feat(node): add Application, ApplicationBuilder"
```

---

## Task 14: Bootstrap sequence and `foundation/kernel.ts`

**Files:**
- Create: `node/src/foundation/bootstrap/bootstrapper.ts`
- Create: `node/src/foundation/bootstrap/load-environment-variables.ts`
- Create: `node/src/foundation/bootstrap/load-console-args.ts`
- Create: `node/src/foundation/bootstrap/prepare-environment.ts`
- Create: `node/src/foundation/bootstrap/load-configuration.ts`
- Create: `node/src/foundation/bootstrap/set-context.ts`
- Create: `node/src/foundation/bootstrap/handle-exceptions.ts`
- Create: `node/src/foundation/bootstrap/register-providers.ts`
- Create: `node/src/foundation/bootstrap/index.ts`
- Create: `node/src/foundation/kernel.ts`

No new tests for this task — bootstrap is exercised through Application integration tests.

- [ ] **Step 1: Create `node/src/foundation/bootstrap/bootstrapper.ts`**

```typescript
import type { Application } from '../application.ts'

export interface Bootstrapper {
  bootstrap(app: Application): void | Promise<void>
}
```

- [ ] **Step 2: Create `node/src/foundation/bootstrap/load-environment-variables.ts`**

```typescript
import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class LoadEnvironmentVariables implements Bootstrapper {
  bootstrap(_app: Application): void {
    // Bun auto-loads .env files — process.env is populated at startup.
    // Nothing to do here unless a custom .env path is needed.
  }
}
```

- [ ] **Step 3: Create `node/src/foundation/bootstrap/load-console-args.ts`**

```typescript
import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class LoadConsoleArgs implements Bootstrapper {
  bootstrap(app: Application): void {
    app.instance('args', process.argv.slice(2))
  }
}
```

- [ ] **Step 4: Create `node/src/foundation/bootstrap/prepare-environment.ts`**

```typescript
import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class PrepareEnvironment implements Bootstrapper {
  bootstrap(app: Application): void {
    const env = process.env['BYTE_ENV'] ?? process.env['NODE_ENV'] ?? 'production'
    app.instance('env', env)
  }
}
```

- [ ] **Step 5: Create `node/src/foundation/bootstrap/load-configuration.ts`**

```typescript
import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'
import { Yaml } from '../../support/yaml.ts'
import path from 'path'

export class LoadConfiguration implements Bootstrapper {
  bootstrap(app: Application): void {
    const configPath = app.configPath()
    const config = Yaml.loadAsDict(path.join(configPath, 'config.yaml'))
    app.instance('config', config)
  }
}
```

- [ ] **Step 6: Create `node/src/foundation/bootstrap/set-context.ts`**

```typescript
import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class SetContext implements Bootstrapper {
  bootstrap(app: Application): void {
    app.instance('path.session_context', app.sessionContextPath())
  }
}
```

- [ ] **Step 7: Create `node/src/foundation/bootstrap/handle-exceptions.ts`**

```typescript
import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'

export class HandleExceptions implements Bootstrapper {
  bootstrap(_app: Application): void {
    process.on('uncaughtException', (err) => {
      console.error('Uncaught exception:', err)
    })
    process.on('unhandledRejection', (reason) => {
      console.error('Unhandled rejection:', reason)
    })
  }
}
```

- [ ] **Step 8: Create `node/src/foundation/bootstrap/register-providers.ts`**

```typescript
import type { Application } from '../application.ts'
import type { Bootstrapper } from './bootstrapper.ts'
import type { Newable } from '../../support/concerns/bootable.ts'
import type { ServiceProvider } from '../../support/service-provider.ts'

export class RegisterProviders implements Bootstrapper {
  static _merge: Newable<ServiceProvider>[] = []

  static merge(providers: Newable<ServiceProvider>[]): void {
    RegisterProviders._merge = [...RegisterProviders._merge, ...providers]
  }

  bootstrap(app: Application): void {
    for (const P of RegisterProviders._merge) {
      app.register(P)
    }
  }
}
```

- [ ] **Step 9: Create `node/src/foundation/bootstrap/index.ts`**

```typescript
export { type Bootstrapper } from './bootstrapper.ts'
export { LoadEnvironmentVariables } from './load-environment-variables.ts'
export { LoadConsoleArgs } from './load-console-args.ts'
export { PrepareEnvironment } from './prepare-environment.ts'
export { LoadConfiguration } from './load-configuration.ts'
export { SetContext } from './set-context.ts'
export { HandleExceptions } from './handle-exceptions.ts'
export { RegisterProviders } from './register-providers.ts'
```

- [ ] **Step 10: Create `node/src/foundation/kernel.ts`**

```typescript
import type { Application } from './application.ts'
import type { Bootstrapper } from './bootstrap/bootstrapper.ts'
import type { Newable } from '../support/concerns/bootable.ts'
import {
  LoadEnvironmentVariables,
  LoadConsoleArgs,
  PrepareEnvironment,
  LoadConfiguration,
  SetContext,
  HandleExceptions,
  RegisterProviders,
} from './bootstrap/index.ts'

export class Kernel {
  static token = Symbol('Kernel')

  constructor(private app: Application) {}

  bootstrappers(): Newable<Bootstrapper>[] {
    return [
      LoadEnvironmentVariables,
      LoadConsoleArgs,
      PrepareEnvironment,
      LoadConfiguration,
      SetContext,
      HandleExceptions,
      RegisterProviders,
    ]
  }

  bootstrap(): void {
    if (!this.app.hasBeenBootstrapped()) {
      this.app.bootstrapWith(this.bootstrappers())
    }
  }

  async handle(input: string[]): Promise<number> {
    this.bootstrap()
    await this.app.boot()
    return this.app.run()
  }

  terminate(): void {
    this.app.terminate()
  }
}
```

- [ ] **Step 11: Verify it compiles**

```bash
cd node && bun run --smol -e "import { Kernel } from './src/foundation/kernel.ts'; console.log('ok')"
```

Expected: `ok`

- [ ] **Step 12: Commit**

```bash
git add node/src/foundation/bootstrap/ node/src/foundation/kernel.ts
git commit -m "feat(node): add bootstrap sequence and Kernel"
```

---

## Task 15: `foundation/service-provider.ts` (FoundationServiceProvider) and `foundation/console/`

**Files:**
- Create: `node/src/foundation/service-provider.ts`
- Create: `node/src/foundation/console/console.ts`
- Create: `node/src/foundation/console/index.ts`

- [ ] **Step 1: Create `node/src/foundation/console/console.ts`**

A minimal Console stub — full implementation deferred to cli domain migration.

```typescript
import type { IApplication } from '../../support/concerns/bootable.ts'

export class Console {
  static token = Symbol('Console')

  constructor(private app: IApplication) {}

  print(message: string): void {
    process.stdout.write(message + '\n')
  }

  error(message: string): void {
    process.stderr.write(message + '\n')
  }
}
```

- [ ] **Step 2: Create `node/src/foundation/console/index.ts`**

```typescript
export { Console } from './console.ts'
```

- [ ] **Step 3: Create `node/src/foundation/service-provider.ts`**

```typescript
import { ServiceProvider } from '../support/service-provider.ts'
import { EventBus } from './event-bus.ts'
import { TaskManager } from './task-manager.ts'
import { Console } from './console/console.ts'
import type { IApplication } from '../support/concerns/bootable.ts'

export class FoundationServiceProvider extends ServiceProvider {
  constructor(app: IApplication) {
    super(app)
  }

  override register(): void {
    this.app.singleton(EventBus as never, () => new EventBus(this.app))
    this.app.instance('event-bus', this.app.make(EventBus as never))

    this.app.singleton(TaskManager as never, () => new TaskManager(this.app))
    this.app.make(TaskManager as never)

    this.app.singleton(Console as never, () => new Console(this.app))
  }
}
```

- [ ] **Step 4: Verify it compiles**

```bash
cd node && bun run --smol -e "import { FoundationServiceProvider } from './src/foundation/service-provider.ts'; console.log('ok')"
```

Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add node/src/foundation/service-provider.ts node/src/foundation/console/
git commit -m "feat(node): add FoundationServiceProvider and Console stub"
```

---

## Task 16: `foundation/index.ts` barrel and `node/src/index.ts` — plus full integration test

**Files:**
- Create: `node/src/foundation/index.ts`
- Modify: `node/src/index.ts`
- Create: `node/tests/foundation/integration.test.ts`

- [ ] **Step 1: Create `node/src/foundation/index.ts`**

```typescript
export { Application } from './application.ts'
export { ApplicationBuilder } from './application-builder.ts'
export { Container } from './container.ts'
export { EventBus, EventType } from './event-bus.ts'
export { TaskManager } from './task-manager.ts'
export { Kernel } from './kernel.ts'
export { ByteException } from './exceptions.ts'
export { FoundationServiceProvider } from './service-provider.ts'
export * from './bootstrap/index.ts'
export * from './console/index.ts'
```

- [ ] **Step 2: Update `node/src/index.ts`**

```typescript
export * from './support/index.ts'
export * from './foundation/index.ts'
```

- [ ] **Step 3: Write integration test**

Create `node/tests/foundation/integration.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { Application } from '../../src/foundation/application.ts'
import { FoundationServiceProvider } from '../../src/foundation/service-provider.ts'
import { EventBus } from '../../src/foundation/event-bus.ts'
import { TaskManager } from '../../src/foundation/task-manager.ts'
import { Payload } from '../../src/support/concerns/eventable.ts'
import path from 'path'

const testBasePath = path.resolve(process.cwd(), '..')

describe('Application + FoundationServiceProvider integration', () => {
  it('resolves EventBus after FoundationServiceProvider registers', () => {
    const app = Application.configure(testBasePath)
      .withProviders([FoundationServiceProvider as never])
      .create()
    const bus = app.make(EventBus as never) as EventBus
    expect(bus).toBeInstanceOf(EventBus)
  })

  it('event-bus string key resolves to EventBus', () => {
    const app = Application.configure(testBasePath)
      .withProviders([FoundationServiceProvider as never])
      .create()
    const bus = app.make<EventBus>('event-bus')
    expect(bus).toBeInstanceOf(EventBus)
  })

  it('TaskManager is available after registration', () => {
    const app = Application.configure(testBasePath)
      .withProviders([FoundationServiceProvider as never])
      .create()
    const tm = app.make(TaskManager as never) as TaskManager
    expect(tm).toBeInstanceOf(TaskManager)
  })

  it('EventBus emits and returns transformed payload', async () => {
    const app = Application.configure(testBasePath)
      .withProviders([FoundationServiceProvider as never])
      .create()
    const bus = app.make<EventBus>('event-bus')
    bus.on('test', (p: Payload) => { p.set('touched', true); return p })
    const result = await bus.emit(new Payload('test'))
    expect(result.get('touched')).toBe(true)
  })
})
```

- [ ] **Step 4: Run integration tests**

```bash
cd node && bun test tests/foundation/integration.test.ts
```

Expected: all tests pass.

- [ ] **Step 5: Run full test suite**

```bash
cd node && bun test
```

Expected: all tests pass, no failures.

- [ ] **Step 6: Commit**

```bash
git add node/src/foundation/index.ts node/src/index.ts node/tests/foundation/integration.test.ts
git commit -m "feat(node): add foundation/index.ts barrel and integration tests"
```

---

## Self-Review Checklist (run before marking done)

- [ ] All spec requirements covered:
  - [x] `node/` top-level directory
  - [x] Bun runtime, `bun test`
  - [x] `support/` domain: ArrayStore, Str, Boundary, BoundaryExtractor, Yaml, all utils, concerns, Service, ServiceProvider
  - [x] `foundation/` domain: Container, EventBus, TaskManager, Application, ApplicationBuilder, Kernel, bootstrap sequence, FoundationServiceProvider, Console stub
  - [x] `IApplication` in `support/` to break circular import
  - [x] `Payload` in `support/concerns/eventable.ts`
  - [x] String key `'event-bus'` for circular-import-safe EventBus resolution from Service
  - [x] `as const` + union types for BoundaryType and EventType
  - [x] Symbol tokens for DI keys
  - [x] `index.ts` barrels for both domains
  - [x] Python source untouched
- [ ] No placeholder steps (all steps have actual code)
- [ ] Type consistency: `Payload` from `support/concerns/eventable.ts` used throughout, `IApplication` from `support/concerns/bootable.ts` used throughout
