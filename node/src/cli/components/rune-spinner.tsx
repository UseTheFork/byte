import React, { useState, useEffect } from 'react'
import { Text, Box } from 'ink'
import chalk from 'chalk'
import { theme } from './theme.ts'

const RUNES = '0123456789abcdefABCDEF~!@#$%^&*()+=_'
const COLORS: (keyof typeof theme)[] = ['primary', 'secondary', 'text']
const SPINNER_SIZE = 6
const FRAME_INTERVAL_MS = 40

interface RuneSpinnerProps {
  message: string
}

export function RuneSpinner({ message }: RuneSpinnerProps): React.ReactElement {
  const [frame, setFrame] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setFrame((f) => f + 1)
    }, FRAME_INTERVAL_MS)
    return () => clearInterval(id)
  }, [])

  const chars = Array.from({ length: SPINNER_SIZE }, (_, i) => {
    const runeSeed = (frame + i) * 31
    const colorSeed = (frame + i) * 37
    const rune = RUNES[runeSeed % RUNES.length] ?? '?'
    const colorName = COLORS[colorSeed % COLORS.length] ?? 'text'
    return chalk.hex(theme[colorName])(rune)
  }).join('')

  return (
    <Box>
      <Text>{chars}{message ? ` ${message}` : ''}</Text>
    </Box>
  )
}
