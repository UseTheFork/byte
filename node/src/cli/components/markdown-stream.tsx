import React, { useMemo } from 'react'
import { Text, Box } from 'ink'
import { marked } from 'marked'
// @ts-expect-error marked-terminal has no bundled types
import TerminalRenderer from 'marked-terminal'
import { ByteDisplay } from './byte-display.tsx'
import type { LiveContent } from '../store/console-store.ts'

// Pre-process agent_plan and operation_block tags — mirrors Python _preprocess_tags
function preprocessTags(content: string): string {
  return content
    .replace(/<agent_plan>([\s\S]*?)<\/agent_plan>/g, '\n```byte\n$1\n```\n')
    .replace(/<operation_block>([\s\S]*?)<\/operation_block>/g, '\n```byte\n$1\n```\n')
}

interface MarkdownStreamProps {
  live: LiveContent
}

export function MarkdownStream({ live }: MarkdownStreamProps): React.ReactElement {
  const rendered = useMemo(() => {
    marked.setOptions({ renderer: new TerminalRenderer() })
    const preprocessed = preprocessTags(live.content)
    return marked.parse(preprocessed) as string
  }, [live.content])

  // Split on ```byte blocks to render them with ByteDisplay
  const parts = rendered.split(/(```byte[\s\S]*?```)/g)

  return (
    <Box flexDirection="column">
      {parts.map((part, i) => {
        if (part.startsWith('```byte')) {
          const inner = part.replace(/^```byte\n?/, '').replace(/\n?```$/, '')
          return <ByteDisplay key={i} content={inner} />
        }
        return <Text key={i}>{part}</Text>
      })}
    </Box>
  )
}
