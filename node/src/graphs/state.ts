import { StateSchema, MessagesValue } from "@langchain/langgraph";
import { BaseMessage } from "@langchain/core/messages";
import { z } from "zod";
import {
  MetadataSchema,
  ConstraintSchema,
  type Metadata,
  type Constraint,
} from "./schemas.ts";

// Custom reducers for state management
const addConstraints = (
  current: Constraint[],
  update: Constraint | Constraint[],
): Constraint[] => {
  const updates = Array.isArray(update) ? update : [update];
  return [...current, ...updates];
};

const replaceStr = (
  current: string | null,
  update: string | null,
): string | null => {
  return update;
};

const updateMetadata = (
  current: Metadata,
  update: Partial<Metadata>,
): Metadata => {
  return { ...current, ...update };
};

// Base state schema that all agents inherit
export const BaseStateSchema = new StateSchema({
  // Persistent conversation history from memory store
  history_messages: MessagesValue,

  // Ephemeral messages for current execution only (validation, errors, etc.)
  scratch_messages: MessagesValue,

  // Current user request being processed by the agent
  user_request: z.string(),

  constraints: z.array(ConstraintSchema).default(() => []),

  masked_messages: z.array(z.custom<BaseMessage>()).default(() => []),

  agent: z.string(),

  errors: z.string().nullable().default(null),

  examples: z.array(z.custom<BaseMessage>()).default(() => []),

  extracted_content: z
    .union([z.string(), z.record(z.unknown())])
    .nullable()
    .default(null),

  // These are specific to Coder
  parsed_blocks: z.array(z.record(z.unknown())).default(() => []),

  // This is specific to subprocess
  command: z.string().default(""),

  metadata: MetadataSchema.default({}),
});

// Export the state type
export type BaseState = typeof BaseStateSchema.State;
