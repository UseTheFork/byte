import React from 'react'
import { Text, Box } from 'ink'
import chalk from 'chalk'
import { theme } from './theme.ts'

interface ByteDisplayProps {
  content: string
}

export function ByteDisplay({ content }: ByteDisplayProps): React.ReactElement {
  const lines = content.split('\n')
  const border =
    chalk.hex(theme.primary)('▌') + chalk.hex(theme.secondary)('▌')

  return (
    <Box flexDirection="column">
      {lines.map((line, i) => (
        <Text key={i}>
          {border}{line}
        </Text>
      ))}
    </Box>
  )
}
