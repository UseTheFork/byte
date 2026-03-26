import { describe, it, expect } from 'bun:test'
import {
  CommitMessageSchema,
  CommitGroupSchema,
  CommitPlanSchema,
} from '../../src/git/schemas.ts'

describe('CommitMessageSchema', () => {
  it('parses a minimal commit message with defaults', () => {
    const result = CommitMessageSchema.parse({ type: 'feat', commit_message: 'add thing' })
    expect(result.type).toBe('feat')
    expect(result.commit_message).toBe('add thing')
    expect(result.scope).toBeNull()
    expect(result.breaking_change).toBe(false)
    expect(result.breaking_change_message).toBeNull()
    expect(result.body).toBeNull()
  })

  it('parses a full commit message', () => {
    const result = CommitMessageSchema.parse({
      type: 'feat',
      scope: 'cli',
      commit_message: 'add thing',
      breaking_change: true,
      breaking_change_message: 'removed old API',
      body: 'this changes everything',
    })
    expect(result.scope).toBe('cli')
    expect(result.breaking_change).toBe(true)
    expect(result.breaking_change_message).toBe('removed old API')
    expect(result.body).toBe('this changes everything')
  })
})

describe('CommitGroupSchema', () => {
  it('extends CommitMessage with files', () => {
    const result = CommitGroupSchema.parse({
      type: 'fix',
      commit_message: 'patch bug',
      files: ['src/foo.ts', 'src/bar.ts'],
    })
    expect(result.files).toEqual(['src/foo.ts', 'src/bar.ts'])
    expect(result.scope).toBeNull()
  })

  it('defaults files to empty array', () => {
    const result = CommitGroupSchema.parse({ type: 'fix', commit_message: 'patch' })
    expect(result.files).toEqual([])
  })
})

describe('CommitPlanSchema', () => {
  it('parses a commit plan with multiple groups', () => {
    const result = CommitPlanSchema.parse({
      commits: [
        { type: 'feat', commit_message: 'add foo', files: ['foo.ts'] },
        { type: 'fix', commit_message: 'fix bar', files: ['bar.ts'] },
      ],
    })
    expect(result.commits).toHaveLength(2)
    expect(result.commits[0]?.type).toBe('feat')
    expect(result.commits[1]?.type).toBe('fix')
  })
})
