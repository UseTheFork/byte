import React, { useState, useEffect, useCallback } from 'react'
import { Text, Box, useInput } from 'ink'
import { readFileSync, appendFileSync } from 'fs'
import chalk from 'chalk'
import { theme } from './theme.ts'
import type { ConsoleStore } from '../store/console-store.ts'

function loadHistory(historyPath: string): string[] {
  try {
    const content = readFileSync(historyPath, 'utf-8')
    return content.split('\n').filter(Boolean).reverse()
  } catch {
    return []
  }
}

function saveToHistory(historyPath: string, input: string): void {
  try {
    appendFileSync(historyPath, input + '\n')
  } catch {
    // ignore — cache dir may not exist yet
  }
}

interface PromptProps {
  store: ConsoleStore
  historyPath: string
  onConfirmQuit: () => Promise<boolean>
}

export function Prompt({ store, historyPath, onConfirmQuit }: PromptProps): React.ReactElement {
  const [buffer, setBuffer] = useState(store.state.promptDefault)
  const [history] = useState<string[]>(() => loadHistory(historyPath))
  const [historyIndex, setHistoryIndex] = useState(-1)

  // Reset buffer when promptDefault changes (interrupt-restore)
  useEffect(() => {
    setBuffer(store.state.promptDefault)
  }, [store.state.promptDefault])

  useInput(useCallback((input, key) => {
    if (key.return) {
      const value = buffer
      setBuffer('')
      setHistoryIndex(-1)
      if (value.trim()) {
        saveToHistory(historyPath, value)
      }
      store.emit('submit', value)
      return
    }

    if (key.ctrl && input === 'c') {
      void onConfirmQuit().then((confirmed) => {
        if (confirmed) process.exit(0)
      })
      return
    }

    if (key.backspace || key.delete) {
      setBuffer((b) => b.slice(0, -1))
      return
    }

    if (key.upArrow) {
      const next = Math.min(historyIndex + 1, history.length - 1)
      setHistoryIndex(next)
      setBuffer(history[next] ?? '')
      return
    }

    if (key.downArrow) {
      const next = historyIndex - 1
      if (next < 0) {
        setHistoryIndex(-1)
        setBuffer('')
      } else {
        setHistoryIndex(next)
        setBuffer(history[next] ?? '')
      }
      return
    }

    // Tab: emit 'tab' on store so PromptService can handle completion
    if (key.tab && buffer.startsWith('/')) {
      store.emit('tab', buffer)
      return
    }

    // Alt+Enter: newline in buffer
    if (key.meta && key.return) {
      setBuffer((b) => b + '\n')
      return
    }

    // Printable characters
    if (input && !key.ctrl && !key.meta) {
      setBuffer((b) => b + input)
    }
  }, [buffer, historyIndex, history, historyPath, store, onConfirmQuit]))

  const cursor = chalk.hex(theme.primary)('❯ ')

  return (
    <Box>
      <Text>{cursor}{buffer}</Text>
    </Box>
  )
}
