import React, { useState, useEffect, useCallback } from 'react'
import { Text, Box } from 'ink'
import { theme } from './theme.ts'
import { RuneSpinner } from './rune-spinner.tsx'
import { Menu } from './menu.tsx'
import { Prompt } from './prompt.tsx'
import { MarkdownStream } from './markdown-stream.tsx'
import type { Console } from '../service/console.ts'
import type { PromptService } from '../service/prompt-service.ts'
import type { ConsoleState, PrintItem } from '../store/console-store.ts'

interface AppProps {
  consoleService: Console
  promptService: PromptService
  cachePath: string
}

function renderPrintItem(item: PrintItem, index: number): React.ReactElement {
  switch (item.type) {
    case 'text':
      return (
        <Text key={index} color={item.style ? theme[item.style as keyof typeof theme] ?? theme.text : theme.text}>
          {item.content}
        </Text>
      )
    case 'error':
      return <Text key={index} color={theme.error}>{item.content}</Text>
    case 'rule':
      return (
        <Text key={index} color={theme.muted}>
          {item.label
            ? `─── ${item.label} ${'─'.repeat(Math.max(0, (process.stdout.columns ?? 80) - item.label.length - 5))}`
            : '─'.repeat(process.stdout.columns ?? 80)}
        </Text>
      )
    case 'markdown':
      return <Text key={index}>{item.content}</Text>
    default:
      return <Text key={index}>{(item as { content?: string }).content ?? ''}</Text>
  }
}

export function App({ consoleService, promptService, cachePath }: AppProps): React.ReactElement {
  const [state, setState] = useState<ConsoleState>(consoleService.store.state)

  useEffect(() => {
    const handler = (newState: ConsoleState) => setState(newState)
    consoleService.store.on('change', handler)

    // Start the REPL loop — fire and forget
    void promptService.run()

    return () => {
      consoleService.store.off('change', handler)
    }
  }, [consoleService, promptService])

  const historyPath = cachePath + '/.input_history'

  const onConfirmQuit = useCallback(
    () => consoleService.confirm('Do you want to quit?'),
    [consoleService],
  )

  return (
    <Box flexDirection="column">
      {/* Past messages */}
      {state.messages.map((item, i) => renderPrintItem(item, i))}

      {/* One active element */}
      {state.spinner && <RuneSpinner message={state.spinner.message} />}
      {state.live && !state.spinner && <MarkdownStream live={state.live} />}
      {state.modal && !state.spinner && (
        <Menu modal={state.modal} />
      )}
      {state.promptVisible && !state.spinner && !state.modal && (
        <Prompt
          store={consoleService.store}
          historyPath={historyPath}
          onConfirmQuit={onConfirmQuit}
        />
      )}
    </Box>
  )
}
