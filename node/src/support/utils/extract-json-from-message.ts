export function extractJsonFromMessage(message: { content: string | Array<{ partial_json?: string }> }): string | null {
  if (Array.isArray(message.content) && message.content.length > 0) {
    return message.content[0]?.partial_json ?? null
  }
  return null
}
