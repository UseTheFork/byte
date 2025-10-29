# Commands

Byte provides a comprehensive set of commands for interacting with your codebase, managing context, and controlling the AI assistant. Commands are organized by category for easy reference.

---

## System

`!<command>` - Execute a shell command and optionally add output to conversation context

## Agent

`/ask` - Ask the AI agent a question or request assistance

`/research` - Research codebase patterns and gather insights

## Files

`/add` - Add file to context as editable

`/drop` - Remove file from context

`/ls` - List all files currently in the AI context

`/read-only` - Add file to context as read-only

## General

`/commit` - Create an AI-powered git commit with automatic staging and linting

`/copy` - Copy code blocks from the last message to clipboard

`/exit` - Exit the Byte application gracefully

`/lint` - Run configured linters on changed files or current context

## Memory

`/clear` - Clear conversation history and start a new thread

`/reset` - Reset conversation history and clear file context completely

`/undo` - Undo the last conversation step

## Session Context

`/context:drop` - Remove item from session context

`/context:ls` - List all session context items

`/web` - Scrape a webpage and convert it to markdown
