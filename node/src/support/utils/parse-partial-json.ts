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
