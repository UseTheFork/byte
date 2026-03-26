import React, { useState, useCallback } from 'react'
import { Text, Box, useInput } from 'ink'
import chalk from 'chalk'
import { theme } from './theme.ts'
import type { ModalState } from '../store/console-store.ts'

const WINDOW_SIZE = 5

interface MenuProps {
  modal: ModalState
}

export function Menu({ modal }: MenuProps): React.ReactElement {
  if (modal.type === 'confirm') {
    return <ConfirmMenu modal={modal} />
  }
  return <SelectMenu modal={modal} />
}

function ConfirmMenu({ modal }: MenuProps): React.ReactElement {
  const defaultIndex = modal.default === false ? 1 : 0
  const [index, setIndex] = useState(defaultIndex)
  const options = ['Yes', 'No']

  useInput(useCallback((input, key) => {
    if (key.leftArrow || input === 'h') {
      setIndex((i) => (i - 1 + options.length) % options.length)
    } else if (key.rightArrow || input === 'l') {
      setIndex((i) => (i + 1) % options.length)
    } else if (key.return) {
      modal.resolve(index === 0)
    } else if (key.escape) {
      modal.resolve(false)
    }
  }, [index, modal]))

  return (
    <Box flexDirection="column">
      <Text color={theme.text}>{modal.message}</Text>
      <Box gap={2}>
        {options.map((opt, i) => (
          <Text key={opt} color={i === index ? theme.primary : theme.muted}>
            {i === index ? '◼' : '◻'} {opt}
          </Text>
        ))}
      </Box>
    </Box>
  )
}

function SelectMenu({ modal }: MenuProps): React.ReactElement {
  const choices = modal.choices ?? []
  const [index, setIndex] = useState(0)
  const windowStart = Math.max(0, Math.min(index - Math.floor(WINDOW_SIZE / 2), choices.length - WINDOW_SIZE))
  const visible = choices.slice(windowStart, windowStart + WINDOW_SIZE)

  useInput(useCallback((input, key) => {
    if (key.upArrow || input === 'k') {
      setIndex((i) => (i - 1 + choices.length) % choices.length)
    } else if (key.downArrow || input === 'j') {
      setIndex((i) => (i + 1) % choices.length)
    } else if (key.return) {
      modal.resolve(choices[index] ?? '')
    } else if (key.escape) {
      modal.resolve(choices[0] ?? '')
    }
  }, [index, choices, modal]))

  return (
    <Box flexDirection="column">
      <Text color={theme.text}>{modal.message}</Text>
      {visible.map((choice, visIdx) => {
        const absIdx = windowStart + visIdx
        const isSelected = absIdx === index
        return (
          <Text key={choice} color={isSelected ? theme.primary : theme.muted}>
            {isSelected ? '›' : ' '} {choice}
          </Text>
        )
      })}
      {choices.length > WINDOW_SIZE && (
        <Text color={theme.muted}>
          ({index + 1}/{choices.length})
        </Text>
      )}
    </Box>
  )
}
