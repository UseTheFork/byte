export function extractContentFromMessage(message: { content: string | Array<{ text?: string }> }): string {
  if (typeof message.content === 'string') return message.content
  if (Array.isArray(message.content) && message.content.length > 0) {
    return message.content[0]?.text ?? ''
  }
  throw new Error(`Unable to extract content from message: ${typeof message.content}`)
}
