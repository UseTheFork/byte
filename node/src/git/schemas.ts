import { z } from 'zod'

export const CommitMessageSchema = z.object({
  type:                    z.string(),
  scope:                   z.string().nullable().default(null),
  commit_message:          z.string(),
  breaking_change:         z.boolean().default(false),
  breaking_change_message: z.string().nullable().default(null),
  body:                    z.string().nullable().default(null),
})

export const CommitGroupSchema = CommitMessageSchema.extend({
  files: z.array(z.string()).default([]),
})

export const CommitPlanSchema = z.object({
  commits: z.array(CommitGroupSchema),
})

export type CommitMessage = z.infer<typeof CommitMessageSchema>
export type CommitGroup   = z.infer<typeof CommitGroupSchema>
export type CommitPlan    = z.infer<typeof CommitPlanSchema>
