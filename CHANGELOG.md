# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-10-31

### 🚀 Features

- Add Pygments for language detection and improve linting configuration
- Add web content parsing infrastructure with multiple specialized parsers

### 🚜 Refactor

- Remove MCP service provider and related configurations
- Update session context handling with new SessionContextModel
- Update lint configuration to support list-based command definition
- Update LSP and lint configurations to use language-based mapping
- Add pyright ignore comments and improve error handling
- Sort and organize imports and configurations
- Restructure config loading and LLM provider configuration
- Update config and file handling with system version and language detection

### 📚 Documentation

- Add LSP documentation and configuration details
- Update settings documentation with config changes and improvements
- Update commands reference with improved descriptions and formatting

### ⚙️ Miscellaneous Tasks

- Update project version to 0.2.3 and modify configuration
- Update CHANGELOG.md with version and configuration changes
- Reorganize logo and asset files, update references

## [0.2.3] - 2025-10-29

### ⚙️ Miscellaneous Tasks

- Update project version to 0.2.2 and modify configuration

## [0.2.2] - 2025-10-29

### 🚀 Features

- Add LSP support with Jedi language server for Python

### 🚜 Refactor

- Restructure research agent and extract node for better context handling
- Reorder placeholders in ask prompt and extract prompt templates

### ⚙️ Miscellaneous Tasks

- Update project version to 0.2.1 and modify configuration

## [0.2.1] - 2025-10-24

### 🚀 Features

- Switch default LLM to openai and enable streaming

### 🚜 Refactor

- Convert LLM schemas to Pydantic and pass model params

### ⚙️ Miscellaneous Tasks

- Update project version to 0.2.0 and add git-cliff configuration

## [0.2.0] - 2025-10-24

### 🚀 Features

- Add rich live spinner and markdown conversion to ChromiumService

### 💼 Other

- Improve documentation.

### 🚜 Refactor

- Simplify agent nodes and improve error handling
- Replace print logging with proper log exception handling
- Rename models.py to schemas.py and adjust config for message masking
- Update undo command console printing methods
- Update documentation and configuration images with PNG files

### 📚 Documentation

- Update commit documentation image references
- Rename and improve example flow documentation

### ⚙️ Miscellaneous Tasks

- Bump version to 0.1.11 and update CHANGELOG.md
- Bump version to 0.1.11 and update CHANGELOG.md
- Update release script comments with tag and push commands
- Refactor configuration loading and first boot initialization

## [0.1.11] - 2025-10-22

### 🚀 Features

- Add subprocess command execution support with shell integration

### 🚜 Refactor

- Update code handling for token usage, reinforcement, and config model
- Update lint service, agents, and main to improve error handling and code structure
- Update agent service, lint handling, and commit workflow
- Streamline agent state and analytics tracking
- Restructure and improve documentation in prompts and agent implementations

### ⚙️ Miscellaneous Tasks

- Add placeholder comment in release script

## [0.1.10] - 2025-10-21

### 🚀 Features

- Simplify agent architecture with context-based schema
- Modify event handling to support more flexible context gathering

### 🚜 Refactor

- Simplify agent state management and graph navigation
- Remove pyright ignore comments and simplify logging configuration

### 📚 Documentation

- Update CHANGELOG.md with latest release notes
- Update CHANGELOG.md and bump version to 0.1.10

### ⚙️ Miscellaneous Tasks

- Prepare release 0.1.9 with updated package version
- Update CHANGELOG.md with recent release notes

## [0.1.9] - 2025-10-20

### ⚙️ Miscellaneous Tasks

- Prepare release 0.1.8 with updated workflows and package configuration
- Update PyPI release workflow configuration

## [0.1.8] - 2025-10-20

### ⚙️ Miscellaneous Tasks

- Add GitHub Actions for PyPI publishing and release script
- Consolidate workflows by removing duplicate publish-to-pypi.yml
- Update package name to byte-ai-cli in project configuration
- Update release workflow for PyPI publication

## [0.1.7] - 2025-10-20

### ⚙️ Miscellaneous Tasks

- Update project development status classifier
- Update project version to 0.1.7 and add changelog

## [0.1.6] - 2025-10-20

### 🚀 Features

- Initialize ByteSmith CLI project with basic structure and dependencies
- Add initial ByteSmith project structure with commands and context management
- Add initial agent structure with DCR-focused assistant and prompts
- Add pre-prompt info display for file context and commands
- Add exit command to ByteSmith application
- Add Langchain dependencies with Anthropic, OpenAI, and Google GenAI support
- Add exit command to ByteSmith CLI
- Add system commands and interactive prompt with command completion
- Add event system with dispatcher, events, and service provider
- Add multi-provider LLM support with OpenAI, Anthropic, and Gemini
- Add LLM service provider with dynamic provider selection
- Add commit command with AI-generated commit messages
- Add graph and prompt modules for commit logic
- Add comment style guide and update UI service provider
- Add configuration management system with config service and providers
- Add type hints to mixin base classes
- Add memory and knowledge management domains with SQLite persistence
- Add async support and coder agent domain with LangGraph integration
- Add bootable mixin for async initialization and boot sequence
- Add response handling infrastructure for agent interactions
- Add loading spinner while waiting for LLM response
- Add interaction tools and services for user communication
- Add context management and improve response handling
- Add git and lint domains with configuration support
- Implement lint command and add gradient logo to UI
- Add pre-commit linting event handler in lint service
- Enhance event system with middleware support and improved file context display
- Add file watcher service with AI comment detection and file change tracking
- Implement actor-based architecture with message bus and core actors
- Add register_services method to bootstrap and service providers
- Implement command registry and enhance input handling with new actor interactions
- Enhance commit agent with improved state management and extraction
- Add file operation batching and messaging for file context management
- Enhance streaming and tool call handling in agent system
- Enhance commit agent with stream rendering and improved execution flow
- Add display mode option for agent streaming and rendering
- Add pytest and grandalf to dev dependencies, update project configuration
- Add custom RuneSpinner for animated CLI thinking indicator
- Add AskAgent and enhance agent service with more flexible execution
- Add MCP support with tool filtering for agents
- Add user interaction and custom panel, modify file watcher service
- Add analytics provider and usage tracking for AI agent interactions
- Enable knowledge, system context, and pre/post assistant node events
- Add new clear command for resetting conversation history
- Add web scraping, markdown conversion, and session context services
- Add CleanerAgent and related user interaction methods to improve content extraction
- Update dependencies, add Nix flake support, and enhance package configuration
- Add project root display in CLI service provider
- Add context management commands for session knowledge tracking
- Add ripgrepy search tool and initialize command for project documentation
- Add first-boot initialization and remove ripgrepy dependency
- Add dotenv loading to Byte CLI initialization
- Add API key validation and auto-configuration for LLM providers
- Add OpenAI support and pytest-asyncio dependency
- Add ripgrep search tool and refactor research/initialization agent
- Add fixture recording service for capturing agent responses
- Add API key validation and fixture recording service
- Add research prompt for agent with comprehensive capabilities
- Add file tracking and improve edit format service interactions
- Add edit format configuration and shell command support to edit format workflow
- Add copy command to extract and copy code blocks to clipboard
- Add enhanced command output display with rich panels and syntax highlighting
- Add commented configuration options for lint, files, web, and mcp settings
- Add byte cache directory and update checkpointer path resolution
- Add configuration files and update project tooling documentation
- Add todo for unfinished MCP tool command implementation
- Add dotenv loading for config initialization
- Add Catppuccin themes and improve CLI theme configuration
- Improve user interaction selection with more robust menu handling
- Enhance initialization, add web configuration, and introduce custom exceptions
- Add scrolling menu with window and scrollbar support
- Add unselected color and improve menu cancellation styling
- Add horizontal menu support for confirmation dialogs with Yes/No options
- Add edit format config and modify user interaction prompt methods

### 🐛 Bug Fixes

- Add small sleep to prevent high CPU usage in input actor
- Return state instead of empty dict in EndNode
- Remove `.from_ansi()` method call in markdown stream formatting
- Remove redundant success tag in console print message

### 💼 Other

- Add dill package to dev dependencies for serialization support
- Update mkdocs site directory configuration

### 🚜 Refactor

- Improve command completion logic in prompt.py
- Improve file listing display using Rich Columns
- Rename project from bytesmith to byte
- Reorganize project structure and clean up unused files
- Restructure project layout and consolidate service providers
- Remove file_repository and reorder event imports
- Improve code documentation and event system architecture
- Update pre-commit config and code formatting
- Enhance file context management with comprehensive documentation and type safety
- Improve LLM service and commit command with better typing and documentation
- Update command processing and event handling flow
- Consolidate config into domain-specific modules
- Remove git detection and simplify project root discovery
- Migrate codebase to async initialization and service resolution
- Remove deprecated agent modules and update service initialization
- Simplify response handler with Rich Live display
- Simplify response handler and interactions with rich prompts
- Remove unused response types and simplify response handling
- Reorganize coder agent into agent domain module
- Simplify coder agent architecture and remove unnecessary graph components
- Remove GitConfig and implement git changed files detection
- Restructure config system and simplify service providers
- Convert Event from dataclass to Pydantic model and reorganize imports
- Restructure commit command to use dedicated service
- Move events module from core to domain directory
- Restructure agent domain with base agent and modular service providers
- Modernize dependency injection and service registration
- Convert completion methods to async for better async support
- Restructure file discovery service and improve file search
- Restructure agent services and improve type handling
- Improve event handling and service registration across multiple domains
- Simplify context imports and add injectable mixins
- Simplify markdown streaming and improve UI rendering
- Simplify coder agent and remove unnecessary logging
- Restructure actor system and improve service provider actor registration
- Update actor subscription method from setup_subscriptions to subscriptions
- Restructure project architecture and remove unused event system
- Restructure project files and update import paths
- Restructure file domain with new actor, commands, and service organization
- Restructure user interaction and input handling in actors
- Remove redundant command_completed() calls and unused code
- Improve command execution and state management in input and coordinator actors
- Improve actor message handling and state management
- Restructure application architecture to use service-based approach
- Update stream rendering to display stream ID and remove empty terminal session file
- Remove deprecated actor and messaging system
- Reorganize agent implementation directory structure
- Restructure agent base classes and improve stream rendering
- Reorganize mixins into separate files and update imports
- Restructure coder agent with edit format and parsing logic
- Move project structure from byte/ to src/byte/
- Update RuneSpinner with improved color randomization and animation speed
- Enhance AI comment parsing and file watching logic
- Restructure memory and agent services for improved modularity
- Improve error handling, UI, and code organization in various services
- Update token usage display in agent analytics service
- Improve agent stream handling and add error resilience
- Restructure edit_format domain and clean up architecture files
- Simplify agent architecture and remove redundant code
- Update file watcher and git service with minor adjustments
- Enhance command handling, input validation, and documentation in CLI services
- Consolidate CLI input and output services into single domain
- Replace panel-based context display with markdown formatting
- Remove debug log statements from watcher and lint services
- Update token tracking and cost calculation model
- Add web configuration and improve display services
- Improve comment handling and event processing in file services
- Extract search/replace block handling in EditFormatService
- Remove manual dotenv loading and add automatic loading with logging
- Update file context and listing commands with improved functionality
- Rename InitilizieAgent to ResearchAgent for clarity and consistency
- Update historic messages fixture and test for edit format service
- Restructure analytics service with improved token tracking and display
- Remove border styles and color formatting from panels
- Update CopyNode preview display with dynamic line length and custom Rule
- Extract ignore pattern management into dedicated FileIgnoreService
- Improve docstrings and code formatting for web modules
- Standardize indentation to tabs in tool modules
- Convert tabs to spaces in system domain files
- Update code to use consistent 4-space indentation
- Remove unused knowledge domain files and clean up imports
- Standardize indentation to tabs in git-related files
- Standardize indentation to tabs across file services and providers
- Normalize indentation in domain edit format files
- Normalize indentation to tabs in analytics services
- Standardize indentation to tabs across multiple Python files
- Improve configuration, logging, and type hints
- Restructure LLM configuration and schemas for better modularity
- Update config structure and CLI configuration settings
- Use rich Text for improved markdown stream rendering
- Replace ByteCheckpointer with InMemorySaver in memory service
- Simplify agent architecture with new AssistantRunnable schema
- Extract console service and replace rich.console usage
- Remove custom rich panel and rule classes, consolidate styling in console service
- Improve console rendering and add newline after user input
- Update Menu and Console services with improved UI and interaction methods
- Improve menu handling with transient option and error state
- Update console display and type handling in git and lint services
- Enhance exception handling and add config validation in services
- Modularize menu implementation with state, rendering, and input handling
- Simplify confirm methods and remove redundant dependencies

### 📚 Documentation

- Add Python style guide with best practices and conventions
- Add comprehensive architecture guide for Byte CLI project
- Update architecture with mixin boot pattern and auto-initialization
- Update architecture guide with refined patterns and structure
- Update README with project description and inspiration sources
- Add initial documentation for Byte's commands and configuration
- Replace configuration.md with comprehensive settings documentation
- Reorganize and structure documentation site
- Reorganize and structure documentation site
- Update documentation structure and content
- Consolidate and refactor documentation structure
- Consolidate and refactor documentation structure
- Remove outdated links and simplify documentation structure
- Add reference documentation for commands and settings
- Update settings documentation with new UI theme options
- Add web scraping concept page to documentation
- Add markdown formatting to web documentation section headers

### 🎨 Styling

- Apply consistent indentation and formatting across Python files
- Normalize code formatting with consistent indentation

### 🧪 Testing

- Remove incomplete test file for blocked fence edit format

### ⚙️ Miscellaneous Tasks

- Add pre-commit configuration with ruff and hooks
- Remove memory.db database file
- Update project configuration and service implementations
- Add ruff cache to gitignore and enhance documentation for memory and file services
- Remove version.py and update version to 0.1.1a
- Bump version to 0.1.2 and remove commented log line
- Add keep-sorted config and pyright diagnostic settings
- Standardize indentation to tabs in LLM domain files
- Standardize indentation to tabs and improve code formatting
- Standardize indentation to tabs in agent domain files
- Bump version to 0.1.3
- Bump version to 0.1.4 and modify markdown rendering
- Add GitHub Actions workflow for deploying docs site
- Add GitHub Actions workflow for deploying docs site
- Update GitHub Actions workflow for documentation deployment
- Add release workflow for PyPI and TestPyPI publishing
- Add license, contributing guide, and update project metadata
<!-- generated by git-cliff -->
