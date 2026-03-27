import { z } from "zod";

const PromptSettingsSchema = z
  .object({
    has_project_hierarchy: z.boolean().default(true),
    has_project_information_and_context: z.boolean().default(true),
    has_file_context: z.boolean().default(true),
    has_masked_messages: z.boolean().default(true),
  })
  .strict();

const MetadataSchema = z
  .object({
    iteration: z.number().int().default(0),
    erase_history: z.boolean().default(false),
    mode: z.enum(["main", "weak", "none"]).default("main"),
    prompt_settings: PromptSettingsSchema.default({}),
  })
  .strict()
  .transform((data) => ({
    iteration: data.iteration,
    erase_history: data.erase_history,
    mode: data.mode,
    prompt_settings: PromptSettingsSchema.parse(data.prompt_settings),
  }));

const ConstraintSchema = z
  .object({
    type: z.enum(["avoid", "require"]),
    description: z.string(),
    source: z.string().nullable().default(null),
  })
  .strict();

const AgentConfigSchema = z
  .object({
    name: z.string(),
    description: z.string(),
  })
  .strict();

const AgentConfigBoolSchema = AgentConfigSchema.extend({
  value: z.boolean().default(false),
}).strict();

const AgentConfigStringSchema = AgentConfigSchema.extend({
  value: z.string().default(""),
}).strict();

const AssistantContextSchema = z
  .object({
    mode: z.enum(["main", "weak", "none"]),
    prompt: z.any().nullable(),
    main: z.any().nullable(),
    weak: z.any().nullable(),
    agent: z.string(),
    user_template: z.array(z.string()),
    prompt_settings: PromptSettingsSchema.default({}),
    tools: z.array(z.any()).nullable().default(null),
    enforcement: z.array(z.string()).nullable().default(null),
  })
  .strict()
  .transform((data) => ({
    mode: data.mode,
    prompt: data.prompt,
    main: data.main,
    weak: data.weak,
    agent: data.agent,
    user_template: data.user_template,
    prompt_settings: PromptSettingsSchema.parse(data.prompt_settings),
    tools: data.tools,
    enforcement: data.enforcement,
  }));

const TokenUsageSchema = z
  .object({
    input_tokens: z.number().int().default(0),
    output_tokens: z.number().int().default(0),
    total_tokens: z.number().int().default(0),
  })
  .strict();

export {
  PromptSettingsSchema,
  MetadataSchema,
  ConstraintSchema,
  AgentConfigSchema,
  AgentConfigBoolSchema,
  AgentConfigStringSchema,
  AssistantContextSchema,
  TokenUsageSchema,
};

export type PromptSettings = z.infer<typeof PromptSettingsSchema>;
export type Metadata = z.infer<typeof MetadataSchema>;
export type Constraint = z.infer<typeof ConstraintSchema>;
export type AgentConfig = z.infer<typeof AgentConfigSchema>;
export type AgentConfigBool = z.infer<typeof AgentConfigBoolSchema>;
export type AgentConfigString = z.infer<typeof AgentConfigStringSchema>;
export type AssistantContext = z.infer<typeof AssistantContextSchema>;
export type TokenUsage = z.infer<typeof TokenUsageSchema>;
