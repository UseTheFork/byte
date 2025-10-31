# Commands

Byte provides a comprehensive set of commands for interacting with your codebase, managing context, and controlling the AI assistant. Commands are organized by category for easy reference.

---

## System

`!<command>` - Execute a shell command and optionally add output to conversation context

## Agent

`/ask` - Ask the AI agent a question or request assistance

`/research` - Execute research agent to gather codebase insights, analyze patterns, and save detailed findings to session context for other agents

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

`/ctx:drop` - Remove items from session context to clean up and reduce noise, improving AI focus on current task

`/ctx:file` - Read a file from disk and add its contents to the session context, making it available to the AI for reference during the conversation

`/ctx:ls` - List all session context items

`/web` - Fetch webpage using headless Chrome, convert HTML to markdown, display for review, and optionally add to LLM context
