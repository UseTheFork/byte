export function getLastAiMessage<T extends { _getType?(): string; type?: string }>(messages: T[]): T {
  if (!messages.length) throw new Error('No messages found in empty list')
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i]!
    if (msg._getType?.() === 'ai' || msg.type === 'ai') return msg
  }
  throw new Error('No AIMessage found in messages list')
}
