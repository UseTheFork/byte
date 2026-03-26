export function getLastMessage<T>(state: T[] | { scratch_messages?: T[] }): T {
  if (Array.isArray(state)) {
    if (!state.length) throw new Error('No messages found in empty list state')
    return state[state.length - 1]!
  }
  const messages = state.scratch_messages
  if (messages?.length) return messages[messages.length - 1]!
  throw new Error(`No messages found in input state: ${JSON.stringify(state)}`)
}
