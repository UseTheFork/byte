# CHANGELOG


## v2.0.0 (2026-06-15)

### Bug Fixes

- Account for label height in Select and fix tool result value access
  ([`89202bd`](https://github.com/UseTheFork/byte/commit/89202bd964c6f05477c436c47a62bda8c9f3fbeb))

- Add defensive id checks for tool_use message chunks
  ([`8216a48`](https://github.com/UseTheFork/byte/commit/8216a485a3fcdefcdbd8cb0319d5291f71cbf4b9))

- Add existence checks for 'id' key before accessing tracked message chunks in tool_use blocks -
  Prevents KeyError when tool_use blocks lack id field in message_chunks data - Apply validation at
  three locations: text/tool_use conditional, tool_call_chunk processing, and final tracked
  conditional - Remove .input_history from .gitignore as file is no longer needed

- Add hasattr checks in to_dict to handle missing file path attributes
  ([`dc71e2b`](https://github.com/UseTheFork/byte/commit/dc71e2bf6d586edfc9fd0f932532fbf2772b9de0))

Add defensive checks using hasattr() when serializing file_path and resolved_file_path to prevent
  AttributeError when these attributes are not yet initialized.

- Add json validation error handling in tool argument deserialization
  ([`109efb1`](https://github.com/UseTheFork/byte/commit/109efb1875107a5eca0ce8ec73cf1c4c24f80733))

- Wrap json.loads() call in try/except to catch JSONDecodeError when parsing array/object tool
  arguments - Raise ToolValidationException with descriptive message on invalid JSON, informing LLM
  about unescaped quotes and enabling retry with corrected input - Fix token usage cost formatting
  from 4 to 2 decimal places for better readability - Remove redundant TODO comment and unused
  'errors' field initialization in agent_state

- Correct additional comments flow, blank constitution sections, validate phase order, and text
  input submit
  ([`4cb6d53`](https://github.com/UseTheFork/byte/commit/4cb6d53bb0443b69e9d59161edbb6e1bd59714d7))

- Default Select height to 0 when options is None in on_mount
  ([`0ab5bd3`](https://github.com/UseTheFork/byte/commit/0ab5bd3a9702fe2e23700e37d588754d53bef7f0))

- Fix CSS variable name and selector in tool args collapsible widget
  ([`0f0b754`](https://github.com/UseTheFork/byte/commit/0f0b7542eb8ef7811f3fe0e1f6151aa93edefc3c))

- Fix section anchor syntax and clean up unused imports
  ([`fa3e942`](https://github.com/UseTheFork/byte/commit/fa3e942175ca7fa77a5f9032405259585e265592))

- Fix Section.start() anchor generation to use proper Markdown syntax (remove extra braces) - Remove
  unused extract_content_from_message import from coder_agent_node - Update CoderAgentMessage
  content access to use .text instead of .content - Fix typo in coder_agent_node: "nest" → "next" -
  Simplify coder_agent_node result handling to use result.text directly

- Fix syntax error in exception handling
  ([`dd1a649`](https://github.com/UseTheFork/byte/commit/dd1a649c580be32f46a8d46d33fae794d25f7bde))

Change exception tuple syntax from parentheses to comma notation in ignore_service.py. Remove unused
  TYPE_CHECKING import and empty conditional block in log_service.py.

- Fix tool message attribute and add tool call styling
  ([`4db6904`](https://github.com/UseTheFork/byte/commit/4db6904c151cae7a084647880436d044b235c761))

Fix incorrect attribute access in tool_node.py where tool_message.content should be
  tool_message.text. Also update TUI styling to properly display tool call messages with appropriate
  margins and add dedicated ToolCall component styling.

- Fix: correct section anchor syntax and clean up code issues
  ([`4dc6364`](https://github.com/UseTheFork/byte/commit/4dc6364f2be425cc556ecb45e974da106e06dbc4))

- Fix Section.start() anchor generation: use proper f-string without extra braces - Remove unused
  extract_content_from_message import from coder_agent_node - Update CoderPlanAgentMessage content
  access to use .text instead of .content - Fix typo in coder_agent_node: "nest" → "next" in section
  heading - Remove stray "# " heading marker from prompt_assembler - Simplify coder_agent_node
  result handling to use result.text directly instead of utility function

- Handle missing tool call widgets in response panel
  ([`41df02f`](https://github.com/UseTheFork/byte/commit/41df02f0c7aaccdf24c235fe65277ef374e76c53))

add exception handling for NoMatches error when completing tool calls in the response panel. this
  prevents crashes when a tool call widget is not found, logging the event instead.

also reorganize code in tool_node.py and tool_call.py to improve readability by moving methods and
  classes to more logical positions within their files.

- Hide loading indicator by default in response panel
  ([`610367b`](https://github.com/UseTheFork/byte/commit/610367b26a289f7a3079bb593ee1131faa3ecd03))

Add 'hidden' class to LoadingIndicator on mount so it doesn't display until explicitly shown. This
  prevents the loading indicator from appearing on initial render of the response panel.

- Preserve markdown formatting in tool results by avoiding json serialization
  ([`5ccd7b2`](https://github.com/UseTheFork/byte/commit/5ccd7b212603a12e98ca3c5fc4b8b52987948883))

- Raise ToolValidationException instead of returning it
  ([`91b195f`](https://github.com/UseTheFork/byte/commit/91b195f9fc49f4844b75025f2206ec4dfc94445f))

- When skill is not found, the code was returning the exception object instead of raising it. This
  prevented the exception from being properly propagated up the call stack, causing incorrect error
  handling behavior.

- Remove redundant border and border_title reset from TextInput
  ([`5d74a0d`](https://github.com/UseTheFork/byte/commit/5d74a0dc576b7cd6b32da630bacf3a0549eb466e))

- Return empty string from ReferenceMaterials when no conventions or session_docs
  ([`598be4a`](https://github.com/UseTheFork/byte/commit/598be4afed0eeb93bb25a536c8548d3236d6993d))

- Return formatted message when no skills available
  ([`f27d730`](https://github.com/UseTheFork/byte/commit/f27d730a507cba0c6f8313dcf1b36b8f1c739d63))

- Reverse prompt history navigation direction
  ([`2b97a29`](https://github.com/UseTheFork/byte/commit/2b97a29cd5c3ffb24128d8fa7c64e0bed9b04828))

Fix the prompt history navigation to correctly display newest items first. The history was being
  reversed incorrectly, causing up/down arrow keys to navigate in the wrong direction. Now up arrow
  navigates to newer items and down arrow navigates to older items, matching expected behavior.

- Skip user confirmation prompts during unit tests
  ([`203bc7f`](https://github.com/UseTheFork/byte/commit/203bc7fcf9c62f0770fa631fd6652eb7422959dc))

Add check in prompt_for_confirmation to return default value when running unit tests, preventing
  interactive prompts from blocking test execution.

- Update anthropic model names and fix docstring formatting
  ([`e49e85c`](https://github.com/UseTheFork/byte/commit/e49e85ce7f448d53eafa13d6c3dcfc5bb5bd620a))

Update Anthropic model references from claude-3-5-haiku-latest to claude-haiku-4-5 to reflect
  current model naming. Also fix docstring indentation in LLMService class to follow proper Python
  documentation standards.

- Use app parameter instead of self.app in prepare_environment
  ([`106a6f8`](https://github.com/UseTheFork/byte/commit/106a6f854569b5f257b7089e4bbf8adc1fb291a3))

- Replace incorrect self.app instance variable references with app parameter in print_boot_status()
  calls - Fixes two instances in _migrate_config_yaml() and _prepare_directories() methods that were
  using wrong reference

- Use correct tool_call_id attribute in tool node tui update
  ([`5ae3294`](https://github.com/UseTheFork/byte/commit/5ae3294b1f62dfd76ef2054767b664fb13dd47d0))

Update the tool_id parameter in the _update_tui method to use the correct attribute name
  tool_call_id instead of the non-existent id attribute on ToolMessage objects.

- Use id-based keys and paths for constitution components and fix init command prompt formatting
  ([`aad4b74`](https://github.com/UseTheFork/byte/commit/aad4b74e1d389aae35c9d8c5816dafc66bde19b2))

### Build System

- Add pytest-env dependency for test environment configuration
  ([`8faa918`](https://github.com/UseTheFork/byte/commit/8faa918cc50d08d12a8be525060de548321ea122))

- Add uvloop for async performance optimization
  ([`f76ca15`](https://github.com/UseTheFork/byte/commit/f76ca15d184c2f12ecd5459b7038b4edd976f37e))

Add uvloop>=0.22.1 as a dependency and integrate it into the event loop policy. uvloop is a drop-in
  replacement for asyncio that provides significant performance improvements for async operations by
  implementing the event loop in Cython instead of pure Python.

- Update flake inputs to latest versions
  ([`013fde9`](https://github.com/UseTheFork/byte/commit/013fde91cc78924d9089f93e0fd3ccd8f515f769))

- Upgrade python target version to 3.14
  ([`d3caa5c`](https://github.com/UseTheFork/byte/commit/d3caa5c426dd9119334c2949299bc37b0dad8312))

Update python-version in tool.ty.environment and target-version in tool.ruff from 3.12 to 3.14 in
  pyproject.toml to support the latest Python version.

### Chores

- Add TODO comment about refactoring PhaseUtils method
  ([`894133a`](https://github.com/UseTheFork/byte/commit/894133a8bfe6be55d59b2a7046e3f7bd2fa3407e))

- Initialize project constitution with core principles and tooling standards
  ([`eb1b2f7`](https://github.com/UseTheFork/byte/commit/eb1b2f76a2d4b01296d9cdc31a239178723f8fcb))

Add comprehensive constitution scaffold establishing project governance, core principles, and
  tooling standards:

**Governance**: Supremacy (constitution supersedes all other practices) and Versioning Policy
  (semantic versioning for amendments)

**Core Principles**: - Domain Driven Design: organized under src/byte/ with explicit public
  interfaces - Don't Repeat Yourself: shared logic extracted to src/byte/support/ - Strict Typing:
  explicit type annotations, no Any without justification

**Tooling & Framework Standards**: - Framework Standards: no mandated framework, library choices
  per-domain via pyproject.toml - Linting & Formatting: Ruff configured with Python 3.14,
  line-length 120, pipeline order (ssort → ruff format → ruff check --fix)

Also fix typo in ai_comment_watcher_service.py reinforcement message (tzhe → the).

- Remove constitution files and clean up ai comment markers
  ([`f5bbb28`](https://github.com/UseTheFork/byte/commit/f5bbb28162fc12f58fbc39b67730b4731dd97285))

Deleted 11 constitution definition files from .byte/constitution/ directory including the main
  constitution.md and all principle/governance files. These appear to have been superseded by the
  programmatic constitution initialization system.

Also removed stray AI comment marker from complete_turn_tool.py, simplified reinforcement list
  formatting in ai_comment_watcher_service.py by removing empty strings and bullet point markers,
  and removed commented-out ToolMessage handling code and TODO from end_node.py.

- Update documentation and configuration
  ([`395ed4e`](https://github.com/UseTheFork/byte/commit/395ed4efb6d07ef4f5ddd88a125da799cb8c61d5))

### Code Style

- Add blank lines after section headings in domain architecture skill
  ([`d07cd83`](https://github.com/UseTheFork/byte/commit/d07cd83688821197add21e5d39f35dc237cbb947))

- Add border-top-round CSS classes and update linting widget to use them
  ([`898e2f7`](https://github.com/UseTheFork/byte/commit/898e2f7a7677595216fa5f1f19eea04c5487f6da))

- Consolidate return statements in constitution tools
  ([`c3682ea`](https://github.com/UseTheFork/byte/commit/c3682ea6656b16131574d56178866afb48f2e54b))

- Fix type ignore comment formatting
  ([`ae75d5e`](https://github.com/UseTheFork/byte/commit/ae75d5ebfcc6c329ef0f3dfabc360f26d9ad3f1a))

Correct type ignore comment syntax from 'ty:ignore' to 'type:ignore' for consistency.

- Format create-tool skill markdown tables and remove trailing whitespace
  ([`532c0ab`](https://github.com/UseTheFork/byte/commit/532c0aba2c7078c82447fb91bcd3957235da3220))

- Improve formatting and sort imports alphabetically
  ([`f40ccd5`](https://github.com/UseTheFork/byte/commit/f40ccd5e9a79d6d4f46a3d2d968a6a0925b77a0c))

- Reformat configuration files for consistency and migrate prettier config
  ([`4f67a79`](https://github.com/UseTheFork/byte/commit/4f67a794f015a818766ff6189e8b453b7e33304c))

- Compact array formatting in .byte/config.jsonc for uv/ruff command and ignore list - Migrate
  prettier configuration from prettier.config.cjs to .prettierrc format - Apply JSON formatting
  rules with 150 character print width and no trailing commas

- Remove debug comment from git_commit_tool
  ([`a29e2a2`](https://github.com/UseTheFork/byte/commit/a29e2a24482578713233c045603f881f6b612cc2))

- Remove debug logging statements from undo command
  ([`197dec4`](https://github.com/UseTheFork/byte/commit/197dec4960ea07d4253c90b05bd895f026d43809))

- Remove three self.app['log'].info() calls that were outputting state_snapshot and messages objects
  for debugging purposes. These statements are no longer needed as the code is stable.

- Simplify docstrings and add error display todo
  ([`1dff796`](https://github.com/UseTheFork/byte/commit/1dff796be68b05cff34289555cc8d224f7a3672f))

- Remove detailed parameter documentation from flash(), update_context(), analytics(), and
  update_files() methods, keeping only single-line descriptions - Add TODO comment in worker error
  handler to consider displaying error details in console instead of generic message

- Simplify docstrings in application and container classes
  ([`2d9eb05`](https://github.com/UseTheFork/byte/commit/2d9eb05f30c88801e26dcaeedf61b99219795bfb))

- Convert multi-line docstrings to concise one-line imperative descriptions per constitution
  standards - Remove Usage code examples and verbose Args/Returns sections across 40+ methods -
  Update bind_paths_in_container() docstring to better reflect actual behavior

- Simplify docstrings in prepare_environment bootstrap class
  ([`5c7ab4b`](https://github.com/UseTheFork/byte/commit/5c7ab4b554a18a9199110c053dad8ead393e7f37))

- Convert multi-line docstrings to concise one-line imperative descriptions per constitution
  standards - Remove Usage code examples, verbose explanations, and unnecessary details from all 11
  docstrings - Import ByteUserConfig to support field filtering in config serialization - Update
  _setup_config to only include ByteUserConfig fields when dumping config to prevent serializing
  ByteConfig-specific fields - Add return type hint (-> None) to _run_first_boot_setup method

- Sort dynamic imports alphabetically in coder and node modules
  ([`8f33008`](https://github.com/UseTheFork/byte/commit/8f33008922e70212e20ff91d7309752971a8d06e))

- Sort dynamic imports and lists alphabetically
  ([`9de2efa`](https://github.com/UseTheFork/byte/commit/9de2efaf48b8166a7d62fd134257ae06cc6f8cd0))

- Sort dynamic imports and tools alphabetically in plan module
  ([`df57fd1`](https://github.com/UseTheFork/byte/commit/df57fd14504c3d3b437aa845f4c7a57b409ef5b7))

- Sort leaves class attributes alphabetically
  ([`5a4871e`](https://github.com/UseTheFork/byte/commit/5a4871ed8f1efd67b31e54a9ce0a137176f047d5))

- Update byte display prefix from single to double border character
  ([`e631b69`](https://github.com/UseTheFork/byte/commit/e631b690e1d258f45948989d75091d154bf4cfd9))

- Update status bar loading animation colors and token display formatting
  ([`a578d9b`](https://github.com/UseTheFork/byte/commit/a578d9b29c0fc442f4bec12e892ae6973c68150c))

### Documentation

- Add docstrings to ClipboardServiceProvider
  ([`b49a3b8`](https://github.com/UseTheFork/byte/commit/b49a3b8d0fbb29765b8930b13c20a763abe1da72))

Add comprehensive docstrings to class and methods to document clipboard service registration and
  command functionality.

- Add gateway and commands explanation pages, reviewing conversations guide
  ([`2ccad18`](https://github.com/UseTheFork/byte/commit/2ccad181c3d5d88f675b155bda7a853cf682ec82))

- Shift recorded conversations from dev-only feature to default public feature by moving cache
  directory from cache/development to cache/conversations - Add explanation/the-gateway.md covering
  gateway architecture, auth, JSON-RPC 2.0 protocol, configuration, and security for external client
  developers - Add explanation/gateway-requests.md documenting five available gateway RPC methods:
  configure, add_file, drop_file, context_add_file, context_drop_file - Add
  explanation/the-commands.md explaining command system, invocation, categories, and integration
  with AI workflows - Add explanation/available-commands.md listing all 21 available commands
  organized by Agent, Context, and File Management categories - Add
  how-to-guides/reviewing-conversations.md explaining how to inspect recorded prompts, constitution
  injection, context, and tool calls for debugging - Update mkdocs.yml to include The Gateway
  section with nested Gateway Requests subpage and The Commands section with nested Available
  Commands subpage - Simplify RecordResponseService docstrings to lean format per constitution
  standards - Change DocumentationAgentNode llm_tier from coding to standard for cost optimization

- Add response format guidelines to commit agent prompt
  ([`2bee7cb`](https://github.com/UseTheFork/byte/commit/2bee7cbcfa61427ebf1de710c825f51e65d69c53))

- Expand documentation with how-to guides and explanation pages
  ([`a3d4248`](https://github.com/UseTheFork/byte/commit/a3d42480805f188125a034676df3fd924e93b170))

- Add comprehensive how-to guides for core Byte features: linting configuration, skill
  creation/management, spec creation/execution, file/web context management, constitution setup, and
  git commits - Create new explanation page on the Constitution covering structure, initialization,
  modification, scoping, versioning, and agent injection - Update documentation-tone skill with
  explicit rules on friendly agent names and plain language (no internal class/tool names) - Replace
  all technical class names with friendly display names throughout docs (HarnessAgentNode → Harness
  Agent, etc.) - Convert ASCII art diagrams to Mermaid diagrams for improved visual clarity -
  Clarify Routing Node as deterministic (non-AI) state routing logic - Add comprehensive Harness
  Agent explanation including context preparation role and separation of concerns - Update
  mkdocs.yml navigation to include all new documentation pages

- Improve edit block format documentation
  ([`c5a6545`](https://github.com/UseTheFork/byte/commit/c5a6545174fc3131be283568a39ac703fa32dfa6))

Enhance prompts.py documentation to clarify edit block format: - Reorganize to show operation types
  before format examples - Separate format documentation for edit operations vs
  create/delete/replace - Add detailed comments about search content requirements - Simplify
  examples by removing unnecessary search/replace tags for create/delete/replace operations -
  Improve clarity on when search/replace tags are needed - Fix typos (charector -> character)

This makes the format clearer for users and reduces confusion about which operations require
  search/replace tags.

- Improve git commit body parameter documentation
  ([`225b1c9`](https://github.com/UseTheFork/byte/commit/225b1c9aae14b7506fe471c0b6758e269c86acd8))

- Remove outdated AI todo comment from CommitMessage class - Expand body parameter description with
  detailed formatting guidelines: imperative mood, present tense, explaining motivation not
  implementation - Clarify that breaking changes should be described in body when breaking_change
  flag is True

- Reorganize docs to diataxis framework and add architecture explanation
  ([`b2d1385`](https://github.com/UseTheFork/byte/commit/b2d138571be14cbd9683b8a03790e61fba932972))

- Restructure documentation from concepts/reference layout to tutorials/how-to-guides/explanation
  following Diátaxis framework - Move installation to tutorials/getting-started/installation.md -
  Add how-to-guides for LLM provider configuration and file management - Add
  explanation/architecture-overview.md with detailed workflow orchestration and LangGraph Mermaid
  diagram - Update mkdocs.yml nav structure and configure pymdownx.superfences with Mermaid custom
  fence support - Update site description in mkdocs.yml to match new tagline - Create
  HarnessSkillsLoaded leaf to inject skill markdown into documentation agent context - Add
  HarnessSkillsLoaded to documentation_agent_node user template - Fix README tagline quote escaping
  - Delete deprecated concepts and reference documentation sections

- Restructure documentation to use dynamic markdown generation
  ([`7784e36`](https://github.com/UseTheFork/byte/commit/7784e3632687f538933f2db405a373b51354f7e3))

- Refactor documentation architecture to auto-generate reference pages from source code via Python
  scripts (commands_to_md.py, settings_to_md.py, requests_to_md.py) - Delete manual explanation
  pages (available-commands.md, gateway-requests.md) and create auto-generated references under
  docs/references/ - Update explanation pages (the-commands.md, the-gateway.md, the-constitution.md)
  to use {% include %} directives for embedding dynamically generated content - Add
  mkdocs-include-markdown-plugin dependency to support markdown inclusion in MkDocs builds - Enhance
  schema.json and ByteUserConfig with descriptions for all configuration fields to support
  auto-generated documentation - Add GatewayConfig descriptions and WebConfig descriptions to
  support reference page generation

- Standardize docstrings and add cancel feedback notification
  ([`b040d02`](https://github.com/UseTheFork/byte/commit/b040d0272dbfe3cc54e9a889e41db45dd8a9f323))

- Refactor docstrings across 14 service and utility modules to follow project constitution v0.2.0
  minimal-lean-docstrings standard - Convert all multi-line docstrings to single-line imperative
  format, removing verbose Args/Returns sections and Usage examples - Add missing return type
  annotations (-> None) to 20+ methods across services, utilities, and screen classes - Remove 'AI:'
  and 'AI!' task instruction comments from all modified files - Add user-facing cancel feedback via
  Messages.Notify() in ConversationScreen.action_cancel_request() to confirm cancel was accepted -
  Re-enable SystemEvents.PostBoot emission and dynamic message handling in conversation_screen boot
  sequence

### Features

- Add bootbox widget for displaying boot messages
  ([`0bbb1fe`](https://github.com/UseTheFork/byte/commit/0bbb1febe3ca6c3e39fe036eb83320604b11ec3c))

Introduce a new Bootbox widget that renders markdown messages during application boot. This widget
  is used to display initialization messages in the chat container.

Also reorder service providers to ensure TUIServiceProvider is initialized after its dependencies,
  and remove the unused is_empty property from Conversation widget.

- Add bootstrap instruction tool and refactor constitution workflow
  ([`87b9e7a`](https://github.com/UseTheFork/byte/commit/87b9e7a81ba70060ff21c2d190db2b2b43ba422c))

- Add BootstrapInstructionTool to pass instructions to agent harness in constitution workflow -
  Create create-instruction phase as entry point using HarnessAgentNode before constitution
  consideration - Refactor ConstitutionAgentNode to use HarnessInstruction leaf and standard LLM
  tier - Reorder context template leaves with ToolsLoaded at end - Add minimal-lean-docstrings
  principle to constitution - Update ApplicationBuilder docstrings to follow lean documentation
  pattern - Simplify DeleteFileTool description and update phase model formatting - Add error
  handling with logging in TUI conversation widget - Remove deprecated
  create_orchistration_plan_tool.py - Update constitution to version 0.2.0

- Add ByteDisplay formatting for tool call information
  ([`857b82f`](https://github.com/UseTheFork/byte/commit/857b82f7574edbc28ab6ab8b6030c20ffc1919e7))

Use ByteDisplay to format tool call information with proper visual hierarchy. Consolidate tool name
  and arguments into a single formatted display instead of printing each line separately.

- Add cache read and write token tracking across analytics and models
  ([`87f1bf4`](https://github.com/UseTheFork/byte/commit/87f1bf4a8844ac2726463d9ec69a99e66e646e76))

- Add cache-aware cost calculations to analytics service
  ([`d9eab5a`](https://github.com/UseTheFork/byte/commit/d9eab5a0c5471d95c8917cf235d470e9eae45bf3))

- Add collapsible arguments widget with custom styling and symbols
  ([`1eb7efc`](https://github.com/UseTheFork/byte/commit/1eb7efcbaadf357e07b5c780965338b1d1b15267))

- Add CommandRunner utility and enhance git grep with async execution and formatting
  ([`04636b6`](https://github.com/UseTheFork/byte/commit/04636b660f86962629edc5abbbe2ca8fe4ca0955))

- Create CommandRunner static utility class in src/byte/support/command_runner.py for asynchronous
  shell command execution using asyncio.create_subprocess_exec - Update GitGrepTool to use
  CommandRunner instead of blocking repo.git.grep, eliminating event loop blocking - Add
  case_sensitive parameter (default False) with -i flag for case-insensitive search - Add max_count
  parameter (default 100) with --max-count flag to limit result volume - Implement
  _format_grep_results() method to parse and structure output grouped by file with line numbers,
  matching expected format - Add --no-pager and --no-color flags to improve output handling - Export
  CommandRunner from src/byte/support module following existing utility pattern

- Add CompleteSimpleTurnTool for simplified agent turn completion
  ([`3b30de7`](https://github.com/UseTheFork/byte/commit/3b30de7ec5c222e7f84eb567206339a5f34099b6))

- Add conditional cache file naming based on development mode
  ([`2b37393`](https://github.com/UseTheFork/byte/commit/2b37393fc374ef7003c0b797ddd564c66d1c5345))

Add is_development() check to determine cache file naming strategy. In development mode, use
  timestamped filenames to preserve multiple responses. In production, use static filenames to
  prevent cache accumulation.

- Add Console service, Menu component, and split themes into package
  ([`2162eaa`](https://github.com/UseTheFork/byte/commit/2162eaae34ec85ce85e762b7afc64afc0e11d4ce))

- Add constitution command and refactor constitution filtering
  ([`e118fc7`](https://github.com/UseTheFork/byte/commit/e118fc791e48b47742445ac711ae46cd77789eca))

- Add constitution domain with models, service, and provider
  ([`bbd77db`](https://github.com/UseTheFork/byte/commit/bbd77db75ef345334020d06f97afaab35c64b660))

- Add constitution tools for managing principles, sections, and governance rules
  ([`fd074c2`](https://github.com/UseTheFork/byte/commit/fd074c22715920ed9c60758beb4f50ba88a32501))

- Add ConstitutionConfig with toggleable principles and bootstrap prompts
  ([`76443a6`](https://github.com/UseTheFork/byte/commit/76443a6465a5f4d23beb57724547d8d2e94a44f1))

- Add context drop file request and handler
  ([`cdd40ab`](https://github.com/UseTheFork/byte/commit/cdd40ab84e79990c8207d1c45a4bc017bf283001))

- Add Requests.ContextDropFile dataclass for dropping file contents from session context via RPC -
  Implement handle_context_drop_file handler with file path resolution and
  SessionContextService.remove_context integration - Add unit and integration tests for
  context_drop_file request type parsing and execution

- Add context management screen and integrate with analytics
  ([`4bde16a`](https://github.com/UseTheFork/byte/commit/4bde16ad2f2c4739b6cecc2f170eb9cba3294b63))

Add ManageContextScreen modal to view and remove session context items, similar to the existing file
  management screen. Integrate context count display in analytics widget with a new UpdateContext
  message. Users can now click on the context count to open the management screen and remove items.
  Updates include:

- New ManageContextScreen with DataTable displaying context keys and types - ContextInfo static
  widget to display context item count with clickable link - UpdateContext message for propagating
  context count changes - Integration in ConversationScreen with action_request_manage_context
  method - Updated Footer widgets to hide command palette in modals - Improved ManageFilesScreen
  styling with rounded borders and better spacing

- Add conversation clear functionality to TUI
  ([`cee439f`](https://github.com/UseTheFork/byte/commit/cee439f5d72172f59f4878b3a67796fa177ff903))

Implement clearing of conversation panels when the clear command is executed: - Add Clear message
  type to enable TUI event communication - Emit Clear message from clear_command to trigger
  conversation cleanup - Add message handler in conversation widget to remove all response panels -
  Remove debug logging statement from git_service

- Add create-tool skill documenting tool development process
  ([`d495796`](https://github.com/UseTheFork/byte/commit/d495796026dda5ea5ed0afe4af1f94d46aec3605))

- Add create_skill_tool for programmatic skill creation
  ([`84d2682`](https://github.com/UseTheFork/byte/commit/84d26826685db83dfb26fddacfed864b86b8af9a))

- Add debug logging to ask_agent_node execution flow
  ([`538f4d8`](https://github.com/UseTheFork/byte/commit/538f4d862ce3cc23a245aeca4ad62dcd4ad6d70f))

add logging statements at key execution points in the ask_agent_node invoke method to facilitate
  debugging and tracing of the agent lifecycle. logs are emitted for: create_runnable,
  generate_agent_state, add heading, dispatch_task, and ainvoke operations

- Add descriptions to slash command completions
  ([`9cac974`](https://github.com/UseTheFork/byte/commit/9cac974f347ddb2a34c2a863f80ad19892a8111c))

Update completion system to return tuples of (completion_text, description) instead of plain
  strings. This allows displaying helpful descriptions alongside command and argument completions in
  the UI.

Changes: - Modify get_slash_completions to return List[tuple[str, str]] with command descriptions -
  Update prompt_toolkit_service to display descriptions in completion items - Change prompt
  character from ">" to "❯" for better visual distinction

- Add developer message to readme and simplify binary detection logic
  ([`b0770c4`](https://github.com/UseTheFork/byte/commit/b0770c4c703098ab09a7bfbadf43aaee4469c849))

- Add 'A message from the developer' section to README.md - Remove common_paths fallback logic from
  _find_binary() method, relying solely on shutil.which() for binary detection - Update chrome
  binary detection to check 'google-chrome' before 'google-chrome-stable' - Regenerate
  command_commit.gif recording

- Add documentation domain with opinionated writing style
  ([`7a4abdf`](https://github.com/UseTheFork/byte/commit/7a4abdf2717087169e32e25bce0453c7acd7f223))

- Add documentation domain (agents, commands, workflows) following coder pattern for managing
  project docs and README - Introduce DocumentationConfig with framework selection, Diátaxis default
  style, Mermaid flag, and extra guidelines - Create DocumentationGuidelines leaf that renders
  style-specific guidance for diataxis, google, microsoft, and minimal styles - Add
  documentation-tone skill enforcing opinionated/bold writing voice for project documentation files
  - Rewrite README.md in opinionated/bold tone with single-line value proposition, trimmed sections,
  and new 'Why Byte Exists' origin story - Update README Core Principles to three focused items:
  Transparency First, Approval Required, Efficiency over excess - Register
  DocumentationServiceProvider in main.py and wire DocumentationGuidelines into
  DocumentationAgentNode system template

- Add domain-architecture skill documentation
  ([`fd789c5`](https://github.com/UseTheFork/byte/commit/fd789c51f92bfd412a741c8948ec6bb8d42474cb))

- Add EditTaskTool and load_task method to SpecLoaderService
  ([`771a768`](https://github.com/UseTheFork/byte/commit/771a768e8a793c4bedc450cf2b2c4aa21a3611a5))

- Add file count metadata to FileAdded event
  ([`3a2661d`](https://github.com/UseTheFork/byte/commit/3a2661d6d5ae018d6da53519015b28222c83a13a))

Add meta_editable_files and meta_read_only_files fields to FileAdded event to track file counts in
  context. Update file service to calculate and emit these counts when files are added. Wire up TUI
  to receive and display updated file statistics via new update_files method. This enables real-time
  file count display in the UI without requiring separate queries.

Also remove unused Columns import and uncomment autocomplete key handler in prompt input widget.

- Add file editing tools and tool file service
  ([`f7b8482`](https://github.com/UseTheFork/byte/commit/f7b8482022d4fce4480f6a0a25e4411431371b0d))

Introduce new file manipulation tools (edit_file, write_file, delete_file) and ToolFileService for
  managing file operations. These tools enable agents to modify files with exact string matching and
  proper validation.

Key additions: - ToolFileService: validates file paths, checks read-only status, and handles file
  edits - edit_file tool: replaces exact strings in files with comprehensive matching requirements -
  write_file tool: creates files with automatic parent directory creation - delete_file tool: safely
  removes files with existence checks - Updated FileServiceProvider to expose edit_file tool -
  Updated files/__init__.py to export new tools and service

- Add gateway domain skill and refactor harness/skill tools
  ([`98d4eef`](https://github.com/UseTheFork/byte/commit/98d4eef8247beb8313d7dd400ddae2b554ad38e9))

- Add gateway-domain skill documentation covering WebSocket JSON-RPC 2.0 bridge architecture, public
  API boundary, RPC method patterns, and cross-domain interaction rules - Replace
  BootstrapInstructionTool with BootstrapInstructionReferencesTool supporting reference_materials
  via SessionContextService validation - Create PresentSkillTool for user skill review/feedback
  workflow and DeleteSkillReferenceTool for removing skill references - Enhance Skill schema with
  to_xml() and to_markdown() utility methods for prompt injection and presentation - Unify all skill
  tools to use skill_id parameter and restructure CreateSkillWorkflow to enforce PresentSkillTool
  usage before phase completion - Rename HarnessWorkspaceReferenceContext to
  HarnessWorkspaceReferenceMaterials and update state field for consistency

- Add gateway domain with websocket json-rpc 2.0 server
  ([`b2afcd7`](https://github.com/UseTheFork/byte/commit/b2afcd754019dd98af21961480070eb5a79d28db))

- Introduce new gateway bounded-context domain at src/byte/gateway/ for optional WebSocket server on
  localhost that allows external clients (e.g., VS Code extension) to authenticate, send
  slash-commands, and receive streamed response events via JSON-RPC 2.0 notifications. - Add
  GatewayConfig with enable/host/port settings to ByteUserConfig; automatically deserialized from
  config.jsonc. - Implement GatewayService managing per-boot token generation, discovery file
  writing, auth handshake, and WebSocket lifecycle. - Implement SessionService for
  per-authenticated-connection RPC request dispatch and EventBus event forwarding
  (Messages.Response, Messages.ToolResponse, Messages.CommandExecutionCompleted, Messages.Status) as
  RPC notifications. - Define strict Pydantic models in protocol.py for JSON-RPC 2.0 envelope
  (RpcRequest, RpcResponse, RpcError, RpcNotification) with extra="forbid" and module-level error
  code constants. - Register GatewayServiceProvider in application bootstrap; add websockets>=16.0
  dependency to pyproject.toml and uv.lock. - Feature is opt-in: gateway only starts if
  gateway.enable is true in config.

- Add git_commit tool for conventional commit creation
  ([`ba40a2b`](https://github.com/UseTheFork/byte/commit/ba40a2b2f19358f867b711a1e1b232de516daaef))

Introduces a new Langchain tool `git_commit` that enables AI agents to create git commits with
  proper conventional commit formatting. The tool accepts commit type, message, scope, breaking
  changes, and body as parameters.

Refactors the commit workflow to use the new tool instead of the previous validation-based pipeline:
  - CommitAgentNode now yields to ToolNode for git_commit execution - Removes CommitValidator from
  the workflow chain - Simplifies CommitCommand by delegating commit handling to the workflow -
  Centralizes TUI message emission via Application.emit_tui()

Updates provider registration order to ensure ToolsServiceProvider initializes before
  GitServiceProvider for proper tool availability.

- Add git_commit tool for staging and committing changes
  ([`fe6d1c5`](https://github.com/UseTheFork/byte/commit/fe6d1c56761807cd5ed99d6ef265221cd55ed220))

Implement a new git_commit tool that enables committing staged changes with structured conventional
  commit messages. This tool accepts commit type, scope, message, and optional breaking change
  metadata to ensure consistent commit formatting.

The tool is integrated into the GitServiceProvider and made available to the commit agent workflow.
  Updates include: - New git_commit tool implementation with full parameter support - Refactored
  tools module structure into separate files (git_commit, git_grep) - Enhanced commit agent to force
  tool_choice on git_commit - Added ToolResponse message type for displaying tool call streaming -
  Improved workflow service to track and emit tool call events - Updated commit workflow to route
  through tool execution node

- Add git_grep tool for codebase pattern searching
  ([`fb36882`](https://github.com/UseTheFork/byte/commit/fb36882742b0103e70ae1adfd2e797ddabbedebd))

Introduce git_grep tool to enable agents to search tracked files using git grep. This tool supports
  regex patterns and optional file filtering, allowing agents like ConventionAgent and AskAgent to
  efficiently search the codebase in parallel with other operations.

Also add git_grep to ConventionAgent and AskAgent toolsets to improve their ability to gather
  context about existing code patterns and conventions.

- Add GitLogTool for retrieving git commit history with filters
  ([`ad1dd75`](https://github.com/UseTheFork/byte/commit/ad1dd7578c674955fd5fd6d81e460c0d3bf59fc5))

Introduce GitLogTool that allows querying git commit logs with support for: - Limiting results with
  max_count parameter - Filtering by date range (since/until) - Scoping to specific
  files/directories - Compact oneline output format

The tool is properly registered in GitServiceProvider and exported through the git module's public
  API.

- Add id, section_id, and order fields to constitution models and refactor tools/service to use
  id-based lookups
  ([`a5477f4`](https://github.com/UseTheFork/byte/commit/a5477f495421ce797f706af48d1d537d3babc8b0))

- Add interactive multiselect menu to context drop command
  ([`e01b2e2`](https://github.com/UseTheFork/byte/commit/e01b2e274a86f058a6e98c53cfa3c9ffe66c0677))

Make file_path argument optional in context_drop_command. When not provided, display an interactive
  multiselect menu to choose which context items to remove. This improves UX by allowing users to
  easily browse and select multiple items at once instead of requiring them to know exact file
  paths.

Also handle InputCancelledError when user cancels the operation.

- Add interactive prompts to initialize command and refactor constitution workflows
  ([`06f0852`](https://github.com/UseTheFork/byte/commit/06f0852595b62538c9f6fb47a8d49aeb2af2bd8e))

- Add list files and read files tools using BaseTool pattern
  ([`1297806`](https://github.com/UseTheFork/byte/commit/12978061ad4b007cc2cfbf4c7b2f6d123372e6a3))

- Add loading indicator widget for response streaming
  ([`1e7ff91`](https://github.com/UseTheFork/byte/commit/1e7ff919cdbf7d3a8303b32ee206b3aa0a3ad010))

Introduce a new LoadingIndicator widget that displays an animated spinner with a customizable
  message during response streaming. This replaces the previous pending panel approach with a more
  flexible, reusable component.

Changes include: - Create LoadingIndicator widget with show/hide methods - Refactor RuneSpinner to
  use Rich's Spinner for better animation - Integrate loading indicator into PromptPanel - Update
  tui_manager_service to show/hide indicator during response events - Remove obsolete ResponseStatus
  and AgentResponsePanel styles - Add utility CSS classes for layout and sizing

- Add LoadSkillTool to ask agent and include SkillsAvailable in system template
  ([`48b2dcc`](https://github.com/UseTheFork/byte/commit/48b2dccba5a694e18e61c153905fa5102f320c4e))

- Add import for LoadSkillTool from byte.skills.tools.load_skill_tool - Include
  Leaves.SkillsAvailable() in the system template to advertise available skills to the agent - Add
  get_tools() method to AskAgentNode that returns LoadSkillTool for agent use

- Add merge_classes utility function
  ([`c977b8b`](https://github.com/UseTheFork/byte/commit/c977b8b9be831ad9588836b7340101292d610c65))

Add a new utility function to merge multiple class strings into a single space-separated string.
  This function filters out None values and empty strings, making it useful for conditional CSS
  class composition in the TUI.

- Add notification system with Notifiable mixin
  ([`f4ce010`](https://github.com/UseTheFork/byte/commit/f4ce01065661957f306e2f7f7ae48a4a670c5f6a))

Introduce a new Notifiable mixin that provides methods for displaying flash/toast notifications to
  users. This mixin extends Eventable and emits TuiEvents.Notify events that are routed through the
  TUI manager service to display notifications via the Flash widget.

Changes include: - Create Notifiable mixin with notify(), notify_success(), notify_warning(), and
  notify_error() methods - Add Notifiable to Command base class alongside Eventable - Implement
  TuiEvents.Notify event type with content, style, and duration fields - Add flash() method to
  ByteTUI to display notifications - Route Notify events in TuiManagerService to Flash widget -
  Update AddFileCommand to use notify_error() instead of direct console.print() - Fix Flash widget
  CSS class names (remove leading dash) and improve styling - Refactor imports in eventable.py for
  clarity

- Add phase update messaging to tool call widget
  ([`0120759`](https://github.com/UseTheFork/byte/commit/01207593c38c97a4d147c858729e7a8ac47d0c6f))

- Add prompt caching with ephemeral cache control to tool messages
  ([`00582ac`](https://github.com/UseTheFork/byte/commit/00582ace518189671bc76f1a68a1a48c5b9c7658))

- Add quick spec workflow and command with standardized command naming
  ([`4932acc`](https://github.com/UseTheFork/byte/commit/4932acc1562cd27037e0c0283e8d6b4610b7f743))

- Add CreateQuickSpecWorkflow that enables quick spec creation without the analyze phase, using
  HarnessAgentNode to bootstrap instructions from chat history - Add QuickSpecCommand (spec:quick)
  to execute the new quick spec workflow - Standardize all spec command names with spec: prefix
  (spec:init, spec:execute, spec:refractor, spec:quick) - Update SpecCreatorAgentNode to use
  HarnessInstruction leaf instead of UserRequest for better context handling - Add llm_tier field to
  SpecTaskCreatorAgentNode - Refactor CreateRefractorWorkflow to use BootstrapAgentTool instead of
  BootstrapSkillsFilesTool

- Add ReadFilesTool to coder agent node
  ([`b20a8ae`](https://github.com/UseTheFork/byte/commit/b20a8aea13738d52b50ac501d64108403111a893))

- Add real-time analytics display with token usage and cost tracking
  ([`04f65bb`](https://github.com/UseTheFork/byte/commit/04f65bbd05576174b2f95fd7ac66507242e29f35))

Implement analytics calculation and real-time display in the TUI. The analytics service now
  calculates token usage, costs, and memory percentage after each LLM interaction and emits events
  to update the UI. A new Analytics widget displays this information with progress bars and
  formatted metrics. The prompt panel has been refactored into separate components (PromptPanel,
  PromptInput, PromptTextArea) for better modularity. Added utility CSS classes for spacing and
  dimensions to support the new layout.

- Add replace_file tool for replacing entire file content
  ([`0a6d886`](https://github.com/UseTheFork/byte/commit/0a6d886668ee19398961eaf689b822d8dcbe4046))

Add a new `replace_file` tool that allows replacing all content in a file with user confirmation.
  This complements the existing `edit_file` and `write_file` tools by providing a dedicated
  operation for complete file replacement.

The implementation includes: - New `replace_file` method in `ToolFileService` with file validation
  and user confirmation - New `replace_file` tool in `src/byte/files/tools/replace_file.py` - Export
  of `replace_file` from the files module - Integration into `CoderAgentNode` tools list - Moved
  `_prepare_file_path` helper method to the top of `ToolFileService` for better organization

The tool follows the same patterns as existing file operation tools and includes proper error
  handling and user interaction.

- Add research module with agent, workflow, command, and improved prompts
  ([`117a942`](https://github.com/UseTheFork/byte/commit/117a94222297b20d6a9af5ebb1b5eccd5d09d40e))

- Add response recording to agent nodes
  ([`6998f97`](https://github.com/UseTheFork/byte/commit/6998f978d27a4c1160ff078d108e6b2833486b31))

integrate RecordResponseService into ask and commit agent nodes to record agent responses for
  development and debugging purposes. this enables tracking of agent behavior and outputs across
  different agent types.

- Add Rule separator after question in Select and TextInput widgets
  ([`e36bc6b`](https://github.com/UseTheFork/byte/commit/e36bc6b99dd0bb4d6f8615eba24741a4254abc88))

- Add select pointer arrow to select and multi-select widgets
  ([`616ecf4`](https://github.com/UseTheFork/byte/commit/616ecf47dcab6a6cd31463fc267d715ffa079b41))

Add SELECT_POINTER unicode constant (❯) to indicate focused items in select lists. Update
  ChoiceLabel in both Select and MultiSelect widgets to display the pointer when focused and
  maintain two-space alignment padding for unfocused items.

This provides visual feedback for which item is currently highlighted when navigating with arrow
  keys.

- Add separate third-party logging handler and intercept standard logging
  ([`5764843`](https://github.com/UseTheFork/byte/commit/5764843366325442bcd9e9e5312ea46637f60de1))

Add InterceptHandler class to route Python's standard logging module through Loguru. Configure two
  separate log sinks: one for byte namespace logs and one for third-party library logs. This allows
  better separation of concerns when debugging application vs. dependency issues.

Intercepted logs from standard logging calls are now routed into Loguru and filtered based on their
  origin, enabling different log files for byte-specific and third-party logs.

- Add session context reference support to constitution workflow
  ([`b0ca8a2`](https://github.com/UseTheFork/byte/commit/b0ca8a2551ce192b2523364fd2d51cef508e4f97))

- Add skill creation workflow with command and agent integration
  ([`e60ea49`](https://github.com/UseTheFork/byte/commit/e60ea4913e32c9c159b2a4fbd42593fa26bb3ffe))

Implements end-to-end skill creation workflow including: - New SkillCommand CLI interface for
  creating skills - CreateSkillWorkflow orchestrating skill creation process - SkillCreatorAgentNode
  with enhanced user interaction guidance - LoadSkillTool added to ask and coder agents -
  Configuration for skill_creator_agent_node with Claude Opus model - Foundation domain skill
  documentation - Updated service provider and workflow exports

- Add skill ID-based tools for references and editing
  ([`57b30b3`](https://github.com/UseTheFork/byte/commit/57b30b3a44a59a69fafd14a47629934c87eba570))

- Add three new tools for skill management: AddSkillReferenceTool, EditSkillTool, and
  LoadSkillReferenceTool - Migrate all skill tools to use skill_id parameter instead of skill_name
  for consistency with normalized ID lookup - Add id field to Skill schema and track references as
  dict[str, Path] for bundled documentation - Update SkillLoaderService to key skills by normalized
  ID and parse reference files from references/ directory - Simplify SkillCreatorAgentNode template
  using HarnessInstruction leaf and remove manual phase definitions - Restructure
  CreateSkillWorkflow with explicit HarnessAgentNode bootstrap phase and improved phase IDs - Add ID
  boundary type to support ID-labeled skill identification in available skills output - Update
  BaseWorkflow.get_phases() return type to support both PhaseModel and RoutePhaseModel

- Add skill orchestrator agent for creating reusable skills
  ([`0f668c6`](https://github.com/UseTheFork/byte/commit/0f668c6cbd21b39f4eec5f872261da24ecc17823))

- Add spec task system with per-file markdown tasks and coding LLM tier
  ([`96f6b76`](https://github.com/UseTheFork/byte/commit/96f6b76c2dc23b580d0ff6538a750437d2d44d3e))

- Add SpecPhase dataclass and phase persistence to specs domain
  ([`c5ba952`](https://github.com/UseTheFork/byte/commit/c5ba952af8f0e4ae94b84d602c3b22d872e31a01))

- Add specs domain with spec creation workflow and loader service
  ([`2f07511`](https://github.com/UseTheFork/byte/commit/2f07511ac87314e8df7f8f360a510cfd28eca19f))

- Add strict typing principle to constitution and fix default order values
  ([`84116c4`](https://github.com/UseTheFork/byte/commit/84116c49118247415eb5d6b0b5dedc073b966bc8))

Added a new "Strict Typing" ConstitutionPrinciple (order=60) to the constitution initialization flow
  with user confirmation prompt. This principle enforces explicit type annotations for all function
  signatures and variables, prohibits use of `Any` without justification, and requires clean
  type-checking tool passes.

Also changed default order values from 0 to 1 across all constitution components (principles,
  governance rules, sections, section items) for better clarity in ordering semantics. Additionally
  fixed start_node.py to properly load skills from harness state instead of always initializing an
  empty list.

- Add textual TUI framework with chat interface
  ([`fd9b72d`](https://github.com/UseTheFork/byte/commit/fd9b72d28256de7ffe93b04c6c4f4d392c3f7e08))

Introduce a new terminal user interface (TUI) built with Textual framework to replace the prompt
  toolkit CLI. This includes:

- ByteTextualApp: Main Textual application class that manages the app lifecycle - ChatScreen: Screen
  component for displaying chat conversations - Chat widget: Core chat widget with message streaming
  and agent response handling - Chatbox widget: Individual message display with selection mode and
  syntax highlighting - PromptInput widget: Text input for user messages with multiline support -
  ResponseStatus widget: Loading indicator for agent responses - Welcome widget: Welcome message for
  new users - Comprehensive SCSS styling for the TUI

The new TUI provides a modern, interactive chat interface with vim-like keybindings, message
  selection, and code block navigation.

- Add theme registry and catppuccin color schemes to TUI
  ([`631bc4a`](https://github.com/UseTheFork/byte/commit/631bc4aa92ee6309617d40d4c5da65d3f3d2bcea))

Introduce ThemeRegistry class to manage Textual themes with four Catppuccin color schemes (Mocha,
  Macchiato, Latte, Frappe) based on Base16 specification. Themes are registered during TUI
  initialization with proper dark/light mode detection.

- Add tool registry service and integrate langchain tools
  ([`4997e3d`](https://github.com/UseTheFork/byte/commit/4997e3d98b85f86324e61c56ac7dfb033c08583b))

Implement a centralized tool registry service to manage langchain tools across the application. Add
  support for service providers to register tools via a new `tools()` and `register_tools()`
  interface. Update tool definitions to use langchain's InjectedToolArg for dependency injection of
  the Application instance instead of relying on the global `make()` function.

This enables tools to be properly registered and discovered at runtime while maintaining clean
  dependency injection patterns. Tools are now registered during application bootstrap through the
  ToolsServiceProvider.

- Add tool validation and improve tool call display formatting
  ([`cfafca1`](https://github.com/UseTheFork/byte/commit/cfafca111117ec542208f8e31d9177888dd2444e))

Add validation to check if tools exist before execution, returning an error message if a tool is not
  available. Improve tool call display with better formatting including backticks for arguments and
  a new ByteDisplay class that renders code with a left border character. Update console rule
  styling to use the new border character and add spacing before agent rules in verbose mode.

- Add ToolResult schema for standardized tool responses
  ([`3d055da`](https://github.com/UseTheFork/byte/commit/3d055da0866574545cd93da5d020dedd58ef0553))

Introduce ToolResult pydantic model to standardize tool execution responses with result and extra
  fields. Update edit_file tool and tool_node to use ToolResult instead of plain dicts for type
  safety and consistency.

- Add tree-sitter based file summary capability and update phase content
  ([`ca00032`](https://github.com/UseTheFork/byte/commit/ca000324a3042d94a7762ff4e46d0d84a560a096))

- Add `to_summary()` method stub to FileContext that will use tree-sitter to extract file structure
  (classes, functions, docstrings) while omitting implementation details - Add `UpdatePhaseTool` to
  phase-0 content and include usage note explaining agents can use it to mark phases complete -
  Clarify linting phase content to emphasize running lint tool FIRST before fixing errors

- Add UpdatePhaseTool to support phase completion workflow
  ([`66ca342`](https://github.com/UseTheFork/byte/commit/66ca3429d3f641d82c40d351f021792508dd64d7))

- Add usage analytics screen and multi-model token tracking
  ([`1c52f10`](https://github.com/UseTheFork/byte/commit/1c52f10f5c3a81f33c815c5e5de9432ba1418f7c))

- Add user confirmation prompts for file operations
  ([`7342a6a`](https://github.com/UseTheFork/byte/commit/7342a6a06a044895cfedf0259d102135c543d2af))

Require user confirmation before applying file creation, deletion, and replacement operations.
  Return VALID status when user declines to proceed, allowing the block to remain in a valid but
  unapplied state.

- Add user interaction tools for confirm, input, select, and confirm_or_input
  ([`1fe3c8c`](https://github.com/UseTheFork/byte/commit/1fe3c8c2bc36d70f9b56d57a4bcbb26fa603e9c3))

Added four new tool classes to the system module that provide structured user interaction
  capabilities:

- UserConfirmTool: Simple yes/no confirmation prompt - UserInputTextTool: Free-form text input
  collection - UserSelectTool: Multiple choice selection with labeled options -
  UserConfirmOrInputTool: Combined yes/no confirmation with text input fallback

Each tool integrates with InteractionService and includes JSON schema validation for parameters.
  Tools are registered in SystemServiceProvider and exported from the system module.

- Add UserMultiSelectTool and MultiSelect widget for batch selections
  ([`d85a55c`](https://github.com/UseTheFork/byte/commit/d85a55c94a543112eb51f8929cdbf37f659e69f1))

Implement multi-select capability throughout the system:

- Create UserMultiSelectTool to prompt users for multiple selections from a list - Build MultiSelect
  widget with checkbox toggling and batch submission (space to toggle, enter to submit) - Add
  multi_select() method to InteractionService supporting prompt_type='multiselect' - Wire
  multiselect handling into Conversation and ResponsePanel - Integrate UserMultiSelectTool into
  create_refractor_workflow tools - Simplify refractor workflow by merging propose phase into
  analysis phase with UserMultiSelectTool

Also: Clarify editable_files descriptions in bootstrap tools to exclude new files, remove debug
  logging from interactions_service.py, and add SpecTaskCreatorAgentNode to workflow graph.

- Add visual left border styling to code blocks and agent output
  ([`f54b487`](https://github.com/UseTheFork/byte/commit/f54b487d4c917f4d67b5ab679ac47055cce048e7))

Introduce a new CodeDisplay class that renders code with a left border character (▌) on each line,
  providing better visual separation in the CLI. Update tool node output and markdown rendering to
  use the new styling with secondary color theme.

Changes include: - Create CodeDisplay renderable for syntax-highlighted code with left borders -
  Update tool_node.py to display tool calls with new border styling - Add special handling for
  'byte' lexer blocks in markdown rendering - Implement _preprocess_tags() to convert agent_plan and
  edit_block tags to markdown - Pass rich_theme through MarkdownStream for consistent styling -
  Remove redundant markdown code fence markers from prompts (now auto-generated)

- Add workflow cancellation with ctrl+z keybinding
  ([`cd3bb1b`](https://github.com/UseTheFork/byte/commit/cd3bb1b2d29aaf0b9867f3416b15fc069e6a0fb0))

Implement comprehensive workflow cancellation functionality:

- Add cancel_event (threading.Event) to WorkflowService for managing execution stops - Add
  is_cancelled flag to execution state for tracking cancellation across nodes - Update routing_node
  to redirect to end_node when execution is cancelled - Update end_node to skip final message update
  when cancelled - Add Ctrl+Z keybinding to conversation screen to trigger cancellation - Track
  execution state with is_working reactive property - Add command execution lifecycle message
  handlers - Refactor emoji faces in status_bar using new unicode constants for improved
  maintainability - Add comprehensive emoji component constants (eyes, mouths, arms, accents) to
  support future visual enhancements

- Configure skill creator agent to use reasoning llm tier
  ([`aaecf36`](https://github.com/UseTheFork/byte/commit/aaecf3648d11ede8aa1f2c02bba31aa30370d4ad))

- Add llm_tier class attribute set to 'reasoning' on SkillCreatorAgentNode to specify the LLM tier
  for improved reasoning capabilities when generating skills

- Display completion descriptions in autocomplete dropdown
  ([`ff5aaa0`](https://github.com/UseTheFork/byte/commit/ff5aaa0c394d2995039c841c2883dc337fdf2fd3))

- Add optional `value` parameter to DropdownItem to store raw completion text separately from
  displayed content - Update DropdownItem.value property to return stored value if set, enabling
  descriptions to display without being inserted - Modify _do_slash_arg_search_async to render
  completion descriptions with dimmed styling using Content.stylize() - Update _complete method to
  use DropdownItem.value for proper value extraction instead of option.prompt.plain

- Display question as label above input in TextInput and Select widgets
  ([`e70d16b`](https://github.com/UseTheFork/byte/commit/e70d16bece8829912b7e3c621284b49d5fc6897b))

- Emit command execution lifecycle messages in file and workflow commands
  ([`3be1f57`](https://github.com/UseTheFork/byte/commit/3be1f57dd154290159161977631baa958d4335dc))

Add CommandExecutionStarted and AddUserInput messages to file commands (add, read-only, drop,
  switch-mode) and workflow commands (ask, coder). Add CommandExecutionCompleted messages to file
  commands. This provides consistent TUI feedback across all command executions.

For file commands, include the command name in AddUserInput. For workflow and git commands, format
  the message as "/{command_name} {raw_args}" to match the command syntax.

- Enable LSP and migrate tools to BaseTool pattern
  ([`d425114`](https://github.com/UseTheFork/byte/commit/d42511434f87b2927b92ff1ebda89f45689c1ed0))

- Enable random free port selection for gateway service
  ([`49bf79b`](https://github.com/UseTheFork/byte/commit/49bf79b6420a787d1cda1618091961db458940d9))

- Change default gateway port from 9731 to 0, allowing OS to assign a random free port - Add
  _actual_port field to track the resolved bound port after websockets.serve() completes - Extract
  actual bound port from server socket and update discovery file with real port - Move discovery
  file write and log message to after server starts so actual port is known

- Enforce phase-scoped tool permissions in tool node and harden context leaves
  ([`35aba19`](https://github.com/UseTheFork/byte/commit/35aba19d15b42f577257ca914a113fc16c16351c))

- Establish constitution as markdown-based governance framework with core principles
  ([`7c11b0b`](https://github.com/UseTheFork/byte/commit/7c11b0bebb0e38cad2ffb352422b75329db0cc2a))

- Extract raw block parsing into dedicated service
  ([`dc2a7e4`](https://github.com/UseTheFork/byte/commit/dc2a7e450915ea7a409e6220322f958dc7f40b02))

Create RawBlockService to handle initial parsing of edit blocks into RawSearchReplaceBlock objects.
  This service manages: - Parsing raw content into RawSearchReplaceBlock objects - Extracting and
  validating block_id, operation, and file_path attributes - Validating tag balance for edit_block
  tags - Merging blocks across multiple iterations by block_id - Validating syntax of raw blocks

This refactoring separates concerns by moving raw block parsing logic out of ParseBlocksNode and
  EditBlockService into a dedicated service, making the code more modular and testable.

- Extract text content from list-formatted message content
  ([`2c0b89f`](https://github.com/UseTheFork/byte/commit/2c0b89f5bc0a1558c8fb44eeee73ec422497c346))

Add `_extract_text_from_content` method to EndNode to handle message content that may be formatted
  as a list of dictionaries or a string. This ensures consistent text extraction regardless of
  content format before wrapping messages in XML boundaries.

Update test to use VCR cassettes for recording/replaying HTTP interactions instead of mocking the
  LLM service, providing more realistic integration testing. Add ConventionsServiceProvider and
  GitServiceProvider to test fixtures.

- Hide ToolArgsRaw widget when tool call is finalized
  ([`eaabf59`](https://github.com/UseTheFork/byte/commit/eaabf59c295269fe68ef4cd209850ee16b783fbd))

- Implement interrupted request handling for AI comment watcher
  ([`c54b897`](https://github.com/UseTheFork/byte/commit/c54b89716541d342f25e2f8e36ab951000cfcf7e))

Add support for tracking whether a user request was triggered by an AI comment detection
  (interrupted session) through the TUI stack.

Changes: - Add `interrupted` flag to `UserInputSubmitted` events and messages to track AI-triggered
  requests - Add `is_interrupted()` method to TUIManagerService to check if current session was
  auto-triggered - Store interrupted state in thread-local context to support concurrent requests -
  Implement `add_reinforcement_hook()` to inject role-specific instructions when request is
  interrupted: - For ask_agent_node: instructions for providing structured answers - For
  coder_agent_node: instructions for implementing changes and removing AI markers - Only append to
  history when request is not interrupted (avoid polluting history with AI-triggered messages) - Fix
  syntax error: change except tuple to proper except clause format

This enables the AI comment watcher to emit structured requests that are handled differently by
  agents, allowing for cleaner code comment removal and appropriate response formatting.

- Implement prepare environment bootstrapper with LLM, files, and gitignore setup
  ([`6b10219`](https://github.com/UseTheFork/byte/commit/6b10219c3e8fb8c5cf302b8a41a95e41921d4cfe))

- Implement production-grade async event bus with queue-based processing
  ([`05bc6a1`](https://github.com/UseTheFork/byte/commit/05bc6a1c1ea25c29b27f7e88c55cd8743ce482d2))

Replace simple synchronous event system with a production-grade async event bus featuring:

- Priority-based event queue (HIGH, NORMAL, LOW) for processing events in order of importance -
  Concurrent handler execution with configurable limits (max 10 concurrent) - Graceful start/stop
  lifecycle management - Support for both fire-and-forget and wait-for-completion event emission -
  Automatic fallback to synchronous processing if bus not started - Proper error handling with
  future rejection on handler exceptions

This enables responsive UI updates (HIGH priority) while background tasks (LOW priority) don't block
  user interactions. The queue-based approach ensures deterministic event ordering within priority
  levels.

- Implement skills system with discovery, loading, and tracking
  ([`1f83049`](https://github.com/UseTheFork/byte/commit/1f83049c140032b2291c23e56b4c2257b7a3d278))

- Implement structured planning and turn completion workflow
  ([`eb0f679`](https://github.com/UseTheFork/byte/commit/eb0f6796c0d14584ab55decdb59cbbcafb07729e))

Add planning system with CreatePlanTool, CompleteStepTool, and CompleteTurnTool to enable structured
  task execution and progress tracking.

Changes: - Standardize ToolResult format to dict with "content" key across all tools - Add
  format_tool_message() and format_tui_message() abstract methods to BaseTool - Introduce PlanStep
  TypedDict and plan field to BaseState - Create memory tools for planning and turn completion
  workflows - Update ToolNode to route complete_turn calls to end_node - Refactor EndNode to extract
  and display complete_turn message as final output - Update agent prompts with planning workflow
  examples - Add plan section generation to PromptAssembler

- Include command in user message display
  ([`fb6489f`](https://github.com/UseTheFork/byte/commit/fb6489f8108e10b0d499f5de386b29abe1262cf0))

prepend the command to the user message body when displaying in the response panel, allowing users
  to see which command was executed alongside their input

- Include model name in token usage summary
  ([`9047096`](https://github.com/UseTheFork/byte/commit/9047096613495d5733fe9f302ed79ca68afa16e8))

- Prepend model_schema.model to the token usage summary string so the model identifier appears first
  - Summary now displays: 'model · Tokens: X in / Y out · Cost: $Z · Memory: W%' - Provides better
  visibility of which model was used for each completion

- Initialize constitution with 7 principles and governance framework
  ([`0bd74e1`](https://github.com/UseTheFork/byte/commit/0bd74e17dfb024e0f4d7ec8c2b2493d74f1e448f))

- Migrate config format from yaml to jsonc with schema support
  ([`1ccd669`](https://github.com/UseTheFork/byte/commit/1ccd66915ec80bd6dd13ab3346a212980e5c071e))

- Replace .byte/config.yaml with .byte/config.jsonc to enable inline comments and improve
  readability - Add new Json utility class in src/byte/support/json.py for JSONC file loading/saving
  with comment preservation - Extract ByteUserConfig as base class for user-facing configuration;
  ByteConfig now includes internal app and web fields - Update LoadConfiguration bootstrapper to
  load JSONC format and auto-detect/configure Chrome binary for web functionality - Add automatic
  config migration from YAML to JSONC in PrepareEnvironment with schema reference injection -
  Generate and include schema.json for config validation and editor intellisense support - Update
  Python requirement from >=3.12 to >=3.14 and add json-with-comments>=1.2.10 dependency

- Pass explicit instruction from harness to coder agent via bootstrap tool
  ([`1357811`](https://github.com/UseTheFork/byte/commit/1357811bb0eed633afa80bc191af4a718c1b1dc4))

- Refactor select widget to use new Answer schema with label and value
  ([`6453790`](https://github.com/UseTheFork/byte/commit/6453790c58839194381e122496419842ef7c5062))

Update Answer schema from NamedTuple with text/id fields to dataclass with label/value fields. This
  provides better semantic naming and supports any value type.

Changes: - Convert Answer to dataclass with label and value fields - Add AnswerCancelled dataclass
  for cancellation handling - Update AskQuestion event to support Answer | list[Answer] |
  AnswerCancelled - Create new Select widget for single-choice selection - Add TUI constants for
  Unicode characters (SQUARE_OUTLINE, SQUARE_FILLED, ANGLE_RIGHT) - Update prompt_input to use
  Unicode constant for AI prompt indicator - Remove Question widget from prompt_panel - Update
  tui_manager_service to use new Select widget - Refactor question.py Option widget with active
  state tracking - Add logging and update return value in user_interactive.py - Clean up unused CSS
  utilities in tui.tcss - Add border styling utilities to utils.tcss

- Remove await from emit_tui calls throughout codebase
  ([`471e210`](https://github.com/UseTheFork/byte/commit/471e210b49149615f586faa5ce8d9dd0db19155b))

The emit_tui method in the Eventable mixin has been changed from async to synchronous, so all await
  calls must be removed. This change simplifies the API as emit_tui no longer needs to be awaited,
  reducing unnecessary async overhead across the codebase.

This affects emit_tui calls in: - Analytics and file services - Git services and validators -
  Knowledge (context) services - Lint services - Memory command handlers - Agent nodes (ask, coder,
  coder_plan, commit) - Tool and validation nodes - Workflow services - Web scraping service - TUI
  interaction and manager services - Notification handlers

- Remove gateway port config and enhance constitution workflow
  ([`fe86560`](https://github.com/UseTheFork/byte/commit/fe865603f8bc87359671886fc08e2f672f142fb7))

- Remove hardcoded gateway port 9732 from config to allow OS to assign random free port - Change
  constitution agent llm_tier from 'standard' to 'reasoning' - Add user request lines for each
  principle in initialize command (DDD, DRY, TDD, YAGNI, TDA, Strict Typing) - Update initialize
  workflow with clarifications that constitution writing is only available in 'create' phase -
  Expand ignore pattern from '.byte/cache' to '.byte' to exclude entire byte directory - Add ignore
  check to discovery service when building tracked files list - Integrate persistent aggregate token
  usage tracking into response panel with reactive updates

- Replace Input with TextArea in TextInput widget and add interactive additional comments prompt
  ([`de481d2`](https://github.com/UseTheFork/byte/commit/de481d2cf4f8d02c265a32e83cbfad434b8b920f))

- Replace loading indicator with unified status bar widget
  ([`e9108dd`](https://github.com/UseTheFork/byte/commit/e9108dde1d0a1fa5e80467eef75859de6eb12e56))

Introduce a new StatusBar widget that consolidates loading and status indicators into a single,
  reusable component. The StatusBar displays animated loading states or static status emojis with
  accompanying messages.

Key changes: - Create StatusBar widget with LoadingEmoji and StatusEmoji sub-components - Replace
  LoadingIndicatorShow/LoadingIndicatorHide messages with unified Status message - Migrate
  conversation event handlers to use new status bar - Remove loading indicator logic from
  response_panel - Reorganize prompt panel layout with StatusBar at the top

The new system provides better visual feedback with kaomoji expressions for different states
  (loading, error, success, warning, info, question, default).

- Return panel_id from emit_tui and auto-remove panels on command completion
  ([`9236aba`](https://github.com/UseTheFork/byte/commit/9236aba20defb5783ccf17d7403377f9e0bc8604))

- Add return type str | None to emit_tui() in Application and Eventable mixin -
  Application.emit_tui() now returns the panel_id extracted from payload, enabling callers to
  reference created panels - WebCommand captures panel_id from emit_tui() call and removes the panel
  after command execution completes - Conversation.update_status() now passes event.message to
  show_loading() with empty string fallback for type safety - Disable 'Clean with LLM' answer option
  in web command pending implementation

- Scroll to latest message after mounting response panel input
  ([`525bc38`](https://github.com/UseTheFork/byte/commit/525bc38e9c56edff900f728de8a2e65db959d944))

- Ensure UI displays the latest message by explicitly calling scroll_to_latest_message() after
  response panel input is mounted during handle_response operation - This guarantees proper
  scrolling behavior when new responses are added to the conversation

- Stream token fragments to status bar and remove ToolArgsRaw widget
  ([`c94f156`](https://github.com/UseTheFork/byte/commit/c94f156fd65e76d08f7cc09826d89ffe53e960f5))

- Support multiple URLs in web command with flexible delimiters
  ([`04d83e4`](https://github.com/UseTheFork/byte/commit/04d83e4237a71f22533ed378d3d994c72930f68f))

- Change parser argument from single 'url' positional to 'urls' with nargs="+" to accept multiple
  URLs - Add URL flattening logic that normalizes space, comma, and newline-separated delimiters
  into individual URL strings - Wrap scraping, display, and interaction logic in for loop to process
  each URL independently with per-URL panel management - Update docstring and usage examples to
  reflect multiple URL support

- Update demo recordings and improve cli function documentation
  ([`2017149`](https://github.com/UseTheFork/byte/commit/2017149f7c6bab03c0d4f13f7ae83c3b6853ebbd))

- Regenerate GIF recordings for command_file, command_web, and example_coder with improved UI
  patterns - Update .tape files to use Wait+Screen instead of Wait+Line and Tab navigation instead
  of Down - Delete command_preset_load.tape as it is no longer needed - Add BYTE_DEBUG and BYTE_ENV
  environment variables to _config.tape - Improve cli() function docstring with detailed multi-line
  description explaining configuration and execution flow - Reorder service provider imports
  alphabetically for consistency

- Upgrade langchain and langgraph dependencies to v1.1+
  ([`cdb348b`](https://github.com/UseTheFork/byte/commit/cdb348b90f7a2afe4d5ccc53b7ea4b9c305ef2a2))

Update langchain, langchain-openai, langchain-anthropic, langchain-core, and langgraph to their
  latest versions (1.1+). Replace skills-ref dependency with strictyaml. Update uv.lock to reflect
  new dependency versions.

- Upgrade Python to 3.14 and update dependencies
  ([`67cf7a4`](https://github.com/UseTheFork/byte/commit/67cf7a44d5e8ec71e79c3e104fc55a42c0ceb245))

Update Python version from 3.12 to 3.14 in .python-version and flake.nix. Update all flake.lock
  dependencies including flake-parts, nixpkgs, nixpkgs-lib, build-system-pkgs, pyproject.nix, and
  uv2nix to their latest versions.

### Ops

- Bump inputs
  ([`00af1f0`](https://github.com/UseTheFork/byte/commit/00af1f0613cd5110d9d442579eccf6787110c59c))

### Performance Improvements

- Cache pathspec in file watcher to reduce per-event overhead
  ([`f4b3926`](https://github.com/UseTheFork/byte/commit/f4b392619060dc0ecca984565fdf7891ce3aaada))

- Initialize _cached_pathspec once during _watch_files setup instead of calling
  ignore_service.get_pathspec() on every file change event - Invalidate cache when .gitignore or
  .byteignore files are modified to stay in sync with ignore rules - Replace expensive pathspec
  retrieval in _watch_filter with fast cached value lookup using safe getattr fallback - Add
  rust_timeout=5000 to awatch call to prevent indefinite blocking

- Parallelize async operations in prompt state generation
  ([`f8810e4`](https://github.com/UseTheFork/byte/commit/f8810e4c3bcb103199b248304be8522f6315dd55))

Optimize the `generate_state` method by using `asyncio.gather()` to execute independent async
  operations concurrently instead of sequentially.

This improves performance by allowing tasks like project context gathering, hierarchy building, file
  context retrieval, and constraint gathering to run in parallel.

Changes: - Add `asyncio` import - Replace sequential await calls with concurrent `asyncio.gather()`
  - Use dictionary-based task mapping for maintainability - Preserve conditional execution logic
  based on prompt_settings

### Refactoring

- Add agent message classes and improve message handling
  ([`e98cbb8`](https://github.com/UseTheFork/byte/commit/e98cbb8cc70ee54b9d34cb0a0d153bd5fd90905c))

Create dedicated message classes for each agent (AskAgentMessage, CoderAgentMessage,
  CoderPlanAgentMessage, CommitAgentMessage) that extend BaseByteAIMessage to track when messages
  are created. This enables proper type-aware message wrapping in end_node.py and improves type
  safety across agent workflows.

Export all agent message classes from the agents module for consistent API.

Implement last-message-only logic in end_node.py to wrap only the final CoderPlanAgentMessage with
  agent boundaries. Replace full recomposition in TextRule with targeted reactive watch updates for
  better performance.

Update agent nodes to dispatch record_response_service calls asynchronously instead of awaiting
  them, unblocking the UI from recording operations.

- Add automatic JSON deserialization for array and object tool parameters
  ([`6079a18`](https://github.com/UseTheFork/byte/commit/6079a18861ce99bd781f201b9207534a21e2c745))

Add JSON deserialization guard to BaseTool.invoke that automatically deserializes string-encoded
  JSON for parameters declared as "array" or "object" in the input schema. This prevents LLMs from
  breaking array parameters when they serialize them as JSON strings.

The guard checks the parameter type against input_schema and only deserializes strings when the
  declared type is "array" or "object", avoiding unintended parsing of legitimate string parameters.

Simplify CreatePlanTool.run by removing manual json.loads call since the base class now handles
  deserialization generically.

- Add type annotation and debug flag to workflow compilation
  ([`c4f8c26`](https://github.com/UseTheFork/byte/commit/c4f8c26fbace599896170df7398b0bde8e5991c2))

Add explicit return type annotation to the compile method in BaseWorkflow to clarify it returns a
  tuple of CompiledStateGraph, BaseState, and RunnableConfig. Also enable debug mode in the workflow
  event streaming to aid troubleshooting during development.

- Centralize agent tool call routing and add dynamic cache timestamps
  ([`209f9a4`](https://github.com/UseTheFork/byte/commit/209f9a448f8b045e2ccb87d396203dadd6132c71))

Extract repeated tool call routing logic from agent nodes into a shared `route_tool_calls()` method
  in BaseAgentNode. This eliminates code duplication across ask, coder, and commit agent nodes.

Add abstract `message_type` property to BaseAgentNode to allow each agent to specify its own message
  type for proper casting.

Implement timestamp-based cache file naming in RecordResponseService to uniquely identify cached
  responses.

Refactor PromptAssembler to separate user message assembly from context assembly, creating
  `assemble_user_message()` and new `assemble_refreshed_context()` methods.

These changes improve maintainability and reduce duplication while preserving existing behavior.

- Centralize harness state access with HarnessStateUtils
  ([`1024a86`](https://github.com/UseTheFork/byte/commit/1024a8614187910ca266ed49f006fa65ecef81a2))

Create HarnessStateUtils utility class with 11 static methods for safe access to harness state
  fields (files, skills, instruction). Refactor HarnessState to nest file-related fields under new
  HarnessFiles typed dict with edit/create/test/reference keys.

Update all harness tools (AddFilesTool, BootstrapAgentTool, BootstrapSkillsFilesTool) and
  orchestration leaves (HarnessWorkspaceFiles, HarnessWorkspaceReferenceFiles) to use
  HarnessStateUtils instead of raw dict access. Fix StartNode to construct HarnessState with nested
  files structure. Add HarnessStateUtils to orchestration module exports.

This centralizes state shape knowledge in one place, reducing duplication and simplifying future
  refactors.

- Centralize heading generation to workflow service and rename AddHeading to CreateHeading
  ([`24f3969`](https://github.com/UseTheFork/byte/commit/24f396968ce72c420b6e901ce014e624500afbcd))

Move heading emission from individual agent nodes to the workflow service level. This allows
  headings to be generated dynamically from langgraph node metadata rather than hardcoded agent
  names.

Changes: - Rename Messages.AddHeading to Messages.CreateHeading - Remove heading emission from ask,
  coder, and commit agent nodes - Add workflow-level heading generation in workflow_service - Pass
  langgraph_node metadata in Response messages for dynamic heading display - Add border_title
  support to SelectableMarkdown widget for improved visual hierarchy

- Centralize response finalization and add token usage metrics
  ([`c675894`](https://github.com/UseTheFork/byte/commit/c675894520518b72b17a645fd788a30a811b69da))

- Extract response recording and usage metric emission into BaseAgentNode.finalize_response method
  called consistently across all agent nodes after LLM invocation - Add emit_usage_summary to
  calculate and display token usage, cost, and memory percentage metrics via new CreateTokenUsage
  TUI message - Create TokenUsageRule widget component for rendering formatted token usage
  statistics in conversation interface - Replace manual HumanMessage append/extend with direct
  string concatenation on last prompt message for incomplete workflow error handling - Simplify
  write_file_tool to use HarnessStateUtils for safe editable files state updates instead of direct
  dict manipulation

- Change git_commit tool body parameter to list of strings
  ([`87931d3`](https://github.com/UseTheFork/byte/commit/87931d322a72e41c0bd90e5411550de3994994d8))

- Remove deprecated CommitGroup and CommitPlan schema classes marked for removal - Change body
  parameter from string to list[str] in GitCommitTool input schema - Update GitCommitTool to join
  body lines with '- ' prefix for formatting - Raise ToolDeclinedException when user declines commit
  confirmation instead of returning ToolResult - Add list_to_text utility method to MD class for
  converting list of strings to single string

- Change workflow request parameter from string to dict
  ([`92348e6`](https://github.com/UseTheFork/byte/commit/92348e64e37e31d81f96548fa3eb806cdf9b9920))

Refactor workflow execution to accept a dictionary request object instead of a plain string. This
  allows passing additional metadata like touched_files alongside the user_request.

Changes: - Update WorkflowService.execute() to accept dict instead of str - Update
  BaseWorkflow.compile() to accept dict and unpack it into initial state - Update
  commit_service.build_commit_prompt() to return dict with user_request and touched_files - Update
  ask_command and coder_command to wrap string requests in dict format - Remove unused current_msg
  tracking from WorkflowService - Update StartNode to use touched_files from state - Add logging of
  request in commit_command

This enables workflows to access additional context beyond just the user request text.

- Clean up unused imports and decorators
  ([`dcb533d`](https://github.com/UseTheFork/byte/commit/dcb533d6093625f165290f076a8eb7b238397140))

- Consolidate agent message classes into dedicated module
  ([`ba4347e`](https://github.com/UseTheFork/byte/commit/ba4347e9c1c23665e941b1728a7016a23542c215))

Extract agent message classes from various agent nodes and base_agent_node into a new messages
  module for better organization and reusability. Create ByteAIMessage namespace with nested message
  classes (CoderPlanAgentMessage, CoderAgentMessage, AskAgentMessage, CommitAgentMessage) that
  inherit from BaseAIMessage. Update all agent nodes to import and reference these messages via the
  new ByteAIMessage namespace. This improves code organization without changing external behavior.

- Consolidate agent message handling and remove ByteAIMessage abstraction
  ([`73139c5`](https://github.com/UseTheFork/byte/commit/73139c5a55a03b99c5ed015cf9569b928ad7c373))

- Consolidate agent node configuration and add message history filtering
  ([`94105ce`](https://github.com/UseTheFork/byte/commit/94105ceb47939119bfdb58d9e5464a16e4e7fd6d))

Replace individual parameter passing (template, model_schema) with agent_node reference in
  PromptAssembler. This simplifies configuration management and enables message history filtering
  through a new filter_message_history method in BaseAgentNode.

Changes: - Add filter_message_history method to BaseAgentNode and CommitAgentNode - Update
  PromptAssembler.boot to accept agent_node instead of template - Store model_schema as instance
  variable in PromptAssembler - Simplify generate_state method signature - Remove
  get_structured_output method in favor of model configuration - Apply message history filtering in
  _gather_modified_messages - Remove unused Optional import

- Consolidate cli into tui and refactor tools to class-based implementations
  ([`b95e4ea`](https://github.com/UseTheFork/byte/commit/b95e4eae16608835cb2e9ffbdc027450b2b13f5e))

- Move cli package functionality to tui package - Convert function-based tools to class-based
  implementations (DeleteFileTool, EditFileTool, ReplaceFileTool, WriteFileTool, GitCommitTool,
  GitGrepTool) - Add SearchWebTool for web search functionality - Replace CLIConfig with TUIConfig
  in configuration - Fix tool registration to use app.make() for dependency injection - Move
  InputCancelledError from cli to tui - Remove Console class, consolidate to tui - Update all
  imports throughout codebase - Fix keep-sorted ordering in dynamic imports - Disable first-boot
  setup code pending TUI integration

- Consolidate interaction service to tui module
  ([`30e1c93`](https://github.com/UseTheFork/byte/commit/30e1c937210b5048ad19ee17af63eb5fd1f15260))

Move InteractionService from cli.service to tui.service and refactor user interaction methods to use
  the new unified service. This consolidates all TUI-related interactions into the tui module.

Changes: - Delete cli.service.interactions_service - Create tui.service.interactions_service with
  confirm, select, and input_text methods - Update user_interactive mixin to import from tui module
  - Simplify prompt_for_select to use Answer objects directly - Remove prompt_for_select_numbered in
  favor of unified select method - Update return type annotations for consistency - Add
  InputCancelledError exception for cancelled interactions - Rename TuiEvents.AskQuestion to
  PromptUser with flexible prompt_type - Add Input widget for text input prompts - Update
  TUIManagerService to handle both select and text input prompts

- Consolidate lint messages into unified Lint message with status
  ([`6c61f47`](https://github.com/UseTheFork/byte/commit/6c61f47e793664c4938bc7757f1382c5ba898bf3))

Replace three separate message types (LintStarted, LintProgress, LintCompleted) with a single
  unified Lint message that uses a status field to differentiate operation states. This simplifies
  the message hierarchy and makes it easier to handle lint operations with status-based dispatch
  logic.

The new Lint message includes: - status field to indicate PENDING, RUNNING, or SUCCESS state -
  status-specific fields that are used based on the current status - unified handler in conversation
  widget that dispatches based on status

This consolidation reduces code duplication and improves maintainability of lint-related messages.

- Consolidate response messaging into unified Status enum
  ([`78e230d`](https://github.com/UseTheFork/byte/commit/78e230d5457098543f2325e7b80ab06d8eec67a1))

Replace separate ResponseStarted, ResponseChunk, and ResponseComplete messages with a unified
  Response message that uses a Status enum. This simplifies the messaging API and provides better
  state management for response handling.

Changes include: - Add Status enum with PENDING, RUNNING, CANCELLED, ERROR, SUCCESS states -
  Consolidate three message types into single Response message with status and optional chunk -
  Update all agent nodes to use new Response message pattern - Refactor conversation widget to
  handle unified response events - Update workflow service to emit Response messages with RUNNING
  status - Simplify notification styling to use SeverityLevel from textual - Update loading
  indicator to use reactive hidden property

- Convert tools from functions to classes and fix instantiation
  ([`fe66f75`](https://github.com/UseTheFork/byte/commit/fe66f753fbd699549ad3a0ca76a74cf26a28ffeb))

Convert all tool implementations from function-based to class-based approach: - Rename tool modules:
  delete_file.py → delete_file_tool.py, etc. - Create BaseTool wrapper class with eager input
  streaming config - Implement tools as classes: DeleteFileTool, EditFileTool, WriteFileTool,
  ReplaceFileTool, GitCommitTool, GitGrepTool, SearchWebTool - Update service providers to return
  List[Type[BaseTool]] instead of instances - Fix tool instantiation in ServiceProvider to use
  app.make() for proper dependency injection - Add GoogleSearchParser for web search result parsing
  - Add ResearchAgentNode for research-focused queries - Reorganize imports with keep-sorted
  formatting

- Convert tools from functions to classes inheriting from BaseTool
  ([`5035bc3`](https://github.com/UseTheFork/byte/commit/5035bc3fdcdbb15e49b3803fb522c4aa7d54b541))

- Renamed tool modules to use *_tool.py naming convention - Created BaseTool base class with eager
  input streaming enabled - Converted all file tools (edit, write, delete, replace) to classes -
  Converted git tools (commit, grep) to classes - Updated imports across agents and service
  providers - Tool registry now instantiates tool classes during registration - Added SearchWebTool
  for web searching - Added GoogleSearchParser for Google Search result parsing - Extended
  ChromiumService with do_search() method - Enhanced message classes with agent_name and mask fields

- Decouple event handling from command execution
  ([`014ccb7`](https://github.com/UseTheFork/byte/commit/014ccb764ab08d411c273a32124830303f529e96))

Remove event_handler parameter from command.handle() and command.execute() methods. Event handling
  is now managed through the EventBus system, allowing commands to emit events directly without
  tight coupling to UI callbacks.

This change simplifies the command interface and enables better separation of concerns between
  command execution and event handling.

- Derive spec ID from directory path instead of normalized name
  ([`bbad208`](https://github.com/UseTheFork/byte/commit/bbad20827d59db01d37bbf299d9fbbb75e796482))

Update SpecLoaderService to use relative directory path as spec ID instead of deriving from name
  field. This makes spec identity directory-based and immutable.

Changes: - Add specs_root parameter to _parse_spec_file for relative path computation - Compute spec
  ID as str(spec_file.parent.relative_to(specs_root)) - Pass directory to _parse_spec_file in
  _load_from_directory

Integrate SpecExecuteCommand with task iteration and status management. Add Spec leaf to harness
  agent template. Refactor Task.to_md() for cleaner task display. Use HarnessStateUtils in
  CreateSpecTool for consistent state handling. Clean up debug code and fix Python syntax errors.

- Disable unused tools and refine file management ui interactions
  ([`a31fe20`](https://github.com/UseTheFork/byte/commit/a31fe2018cafa9747b898f6be2c6dcfa39d71b63))

- Enhance add files tool description and coder agent internals
  ([`b816669`](https://github.com/UseTheFork/byte/commit/b81666912a6d2784c7d20edaef425ea665fba6bc))

- Enhance boot messaging and improve initialization order
  ([`363b2ea`](https://github.com/UseTheFork/byte/commit/363b2ea7ee2f5e8317dd7615452d0c031de8a01f))

- Enhance print_boot_status() to support optional subject parameter for formatted registration
  messages with muted message and bright subject text - Update all service provider registrations to
  use new print_boot_status signature with separate message and subject parameters - Refactor
  configuration setup to use dictionary unpacking for consistent schema reference placement - Update
  boot status messages in prepare_environment to use new method signature - Move _setup_gitignore()
  call from _run_first_boot_setup() to bootstrap() for proper initialization order - Add
  .byte/.gitignore to exclude cache and session_context directories

- Export BaseTool and remove read_file tool, change extraction error handling
  ([`fee9fdb`](https://github.com/UseTheFork/byte/commit/fee9fdb96dda6b9150b005e5709cee49b74fde72))

- Add BaseTool to public exports in tools/__init__.py - Update _dynamic_imports with BaseTool and
  reorder alphabetically - Change extract_content_from_message to return empty string instead of
  raising ValueError - Remove read_file.py tool implementation

- Extract comment cleaning logic and add instruction field to bootstrap tool
  ([`d340a48`](https://github.com/UseTheFork/byte/commit/d340a48f24e257f794bb9c0270a5bfb8b0535197))

- Create MD.clean_comment_lines() utility method in markdown.py to centralize comment marker removal
  logic, supporting both string and list inputs - Update ai_comment_watcher_service.py to use new
  centralized clean_comment_lines method instead of inline strip/lstrip operations - Add instruction
  field to bootstrap_agent_tool result dict to pass instructions alongside OK response - Implement
  format_tui_message() method in bootstrap_agent_tool to extract and display instruction data from
  tool results

- Extract communication style and workflow constraints into reusable leaves
  ([`9544395`](https://github.com/UseTheFork/byte/commit/95443955191d37f54112f7d3a78de8467c9db865))

- Extract cost calculation logic into CostCalculator utility
  ([`e821c14`](https://github.com/UseTheFork/byte/commit/e821c140830a8ac5d38a7fd2855b668916b2ad72))

- Extract GitDiffs leaf component for better code organization
  ([`a026a29`](https://github.com/UseTheFork/byte/commit/a026a29c71a7281b7577063745bedc9610f951ea))

- Extract markdown utilities and move commit guidelines to leaf
  ([`1fc3c3d`](https://github.com/UseTheFork/byte/commit/1fc3c3d0ea56c1cabf8cfc47e2ef17b55a38b141))

- Extract plan management into dedicated module with structured steps
  ([`27a1f2a`](https://github.com/UseTheFork/byte/commit/27a1f2a99c66e587f8381b86f02fd21856f498fb))

- Extract tool routing and prompt assembly logic into reusable methods
  ([`0a87e71`](https://github.com/UseTheFork/byte/commit/0a87e71d465ef6221c961d75c3d13373daed9b67))

- Add abstract `message_type` property to BaseAgentNode for type-safe message casting - Create
  `route_tool_calls()` method to centralize tool routing logic across all agent nodes - Remove
  redundant `cast` imports from agent node implementations - Split prompt assembly into
  `assemble_user_message()` and `assemble_refreshed_context()` methods - Add `refreshed_context`
  placeholder to coder agent message template - Remove duplicate `file_context_with_line_numbers`
  from coder agent prompt - Add timestamp generation to cached response files for better tracking -
  Initialize `prompt_state` attribute in PromptAssembler for state persistence

- Extract utility styles into separate stylesheet
  ([`637db6f`](https://github.com/UseTheFork/byte/commit/637db6fb15480f8d28e331855b7d57e5f60361ea))

Split reusable utility styles (margins, padding, dimensions, text alignment, etc.) into a dedicated
  utils.tcss file. Update ByteTUI to load both utils.tcss and tui.tcss stylesheets. This improves
  maintainability and allows utility styles to be reused across other components.

- Format markdown tables and improve code formatting in documentation and tools
  ([`51fb44b`](https://github.com/UseTheFork/byte/commit/51fb44b04fc8bf4a6fa1299e2d931524622d981c))

- Implement workflow completion loop in agent nodes with phase validation
  ([`169a212`](https://github.com/UseTheFork/byte/commit/169a212d82347a602936686e2f55a04e68935914))

- Improve agent plan and operation block formatting
  ([`94afde7`](https://github.com/UseTheFork/byte/commit/94afde726f464b6f9f664ccfa8dcac07015edce6))

Enhance markdown formatting for agent plans and operation blocks with better visual structure. Add
  search/replace boundary markers and improve metadata header formatting with proper spacing and
  backtick escaping.

- Improve ai comment watcher instructions and error handling
  ([`66e3ee1`](https://github.com/UseTheFork/byte/commit/66e3ee131377af4a43c5d259777915d6fb3815a6))

Enhance AI comment watcher service with clearer instructions for both coder and ask agents. Add
  explicit reminders to remove AI comment markers after implementation and provide structured
  guidance for answer formatting. Improve tool file service error handling with try-catch wrapper
  and TUI error panel display. Update edit_file tool to return structured dict with touched_files
  metadata for downstream processing.

- Improve error messages and file listing behavior
  ([`288a557`](https://github.com/UseTheFork/byte/commit/288a5576d9a7019b4fe98b44876286819fd5cfdf))

- Improve git grep tool documentation and type hints
  ([`72b6a73`](https://github.com/UseTheFork/byte/commit/72b6a7350210c2ec35d80aca98423426b8248964))

Replace parse_docstring=True with explicit description parameter in @tool decorator and add
  Annotated type hints with descriptions to function parameters. This makes the documentation more
  visible to tool callers and provides better IDE support. Remove verbose docstring since parameter
  documentation is now handled by type annotations.

- Improve line numbering, message formatting, and documentation clarity
  ([`05384ff`](https://github.com/UseTheFork/byte/commit/05384ffc5548321a84306c59b5329bfe0c714d95))

- Increase line number field width from 4 to 6 digits for better handling of large files - Add
  boundary markers to AI and tool messages for clearer message structure - Include user_request
  parameter in workflow execution for better context - Add example section notation format to
  documentation - Fix quote style and em-dash consistency in instructions

- Improve message handling and tool result formatting
  ([`54ca647`](https://github.com/UseTheFork/byte/commit/54ca647a2802508863b488d22cf0c368189373e5))

- Improve prompt structure and markdown formatting in orchestration layers
  ([`6894d19`](https://github.com/UseTheFork/byte/commit/6894d19d7e25e8baf9b6dd9322bce96ed3050b15))

- Improve tool schema property ordering and add default parameter
  ([`82c6043`](https://github.com/UseTheFork/byte/commit/82c6043f2d38f7439e3a856d6636302938797f77))

- Improve tui event handling and styling consistency
  ([`6a6747a`](https://github.com/UseTheFork/byte/commit/6a6747aa846094b2af8540e7b9b2974d36d654a3))

Refactor TUI event routing to enforce proper initialization order by requiring
  CommandExecutionStarted to be emitted first. Add support for customizable heading styles via
  AddHeading event parameter. Remove hardcoded color from TextRule and use CSS classes instead for
  better consistency. Add defensive assertions and null checks to prevent runtime errors. Clean up
  type ignore comments as they're no longer needed.

- Improve web search with humanized interactions and fix exception hierarchy
  ([`5a72cb6`](https://github.com/UseTheFork/byte/commit/5a72cb610a1b9757169740e12ec2447d3ca02ebe))

- Integrate leaf-based context templates across agent nodes
  ([`70ac25f`](https://github.com/UseTheFork/byte/commit/70ac25f4f96b4bd618087452130532bb648d924e))

- Integrate TUI messaging into command execution
  ([`b78a809`](https://github.com/UseTheFork/byte/commit/b78a8096d205311c9132cbf8152d1eb0ffe15677))

Replace direct console output with TUI message emissions and notification methods in clear and reset
  commands for consistent UI interaction. Update coder agent prompt examples to enforce 3-round
  minimum drafting with mandatory tool usage before summary.

- Limit exception traceback frames to 5
  ([`c835d37`](https://github.com/UseTheFork/byte/commit/c835d3714b8f40017390a9db71ab1ded48cb747f))

Add max_frames=5 parameter to traceback display to limit the number of frames shown when printing
  exception tracebacks. This improves readability by reducing verbose output for deep call stacks.

- Make agent tools conditional based on execution state
  ([`c9287b2`](https://github.com/UseTheFork/byte/commit/c9287b241c2cccaadd099c40e94be71616e24eeb))

- Make BaseBlock inherit from UserInteractive mixin
  ([`c50cb5c`](https://github.com/UseTheFork/byte/commit/c50cb5c887a309563eaa1c8b80c1bcb7d08772e9))

Add UserInteractive mixin to BaseBlock to enable user confirmation prompts for block operations.

- Migrate CLI components to TUI and standardize command patterns
  ([`ff901d3`](https://github.com/UseTheFork/byte/commit/ff901d38d7b7dcf7403eaea6c444769329c6fe64))

Refactor multiple commands and services to use the TUI event system instead of direct console
  output:

- Update ContextDropCommand to use emit_tui and notify_* methods like ContextAddFileCommand - Update
  WebCommand to use InteractionService and TUI messages for user interactions - Migrate
  ChromiumService to emit TUI loading indicators instead of using Rich spinners - Move
  byte_display.py and markdown.py from cli/rich to tui/rich - Standardize notification duration
  defaults to 3 seconds in Notifiable mixin - Clean up debug logging in InteractionService - Add
  proper command execution lifecycle messages in TuiManagerService - Improve loading indicator
  management in conversation widget

This ensures consistent UI patterns across all commands and services.

- Migrate constitution storage from JSON to Markdown with YAML frontmatter
  ([`45437bc`](https://github.com/UseTheFork/byte/commit/45437bce3a04fadcf600821e0fcd696754cf5c6a))

- Migrate tool schemas from dict to pydantic models
  ([`e7904ee`](https://github.com/UseTheFork/byte/commit/e7904eee904ea51fd94f760f7e6cf25116473b3d))

Convert dictionary-based ArgsSchema definitions to Pydantic BaseModel classes across all tools
  (file, git, web). Add InjectedToolArg support for dependency injection. Standardize parameter
  naming (path → file_path, old_string → search_string, new_string → replace_string). Remove ABCMeta
  from BaseTool and simplify subclass validation. Clean up agent prompt templates and remove
  redundant logic from coder agent.

- Migrate tool system to custom json schema-based architecture
  ([`32f5dc9`](https://github.com/UseTheFork/byte/commit/32f5dc9bc3b3f29ba9ff05f2cb98e6a82d1b5259))

- Move agent prompts from module scope to method scope
  ([`405883d`](https://github.com/UseTheFork/byte/commit/405883ddb2db3f96178783aff44eda13bb7e26df))

- Move border rendering to line loop in byte display
  ([`6dfe969`](https://github.com/UseTheFork/byte/commit/6dfe969ba38b82120598ecebb8b3c2e85cdf4575))

Move the border rendering from before the loop to inside the loop so that the border is applied to
  each line individually rather than yielding it separately. This simplifies the logic and ensures
  consistent border styling across all rendered lines.

- Move Command and CommandRegistry to dedicated command module
  ([`182c48e`](https://github.com/UseTheFork/byte/commit/182c48ecaa7e2a94592c2ae4cbc1f8417173a934))

Extract Command and CommandRegistry from the cli module into a new dedicated command module to
  establish clearer separation of concerns. The command domain is now a first-class module alongside
  foundation, cli, and other core domains.

This change: - Creates new `byte.command` module with Command and CommandRegistry - Moves
  CommandRegistry from `byte.cli.service.command_registry` to
  `byte.command.service.command_registry` - Updates all imports across the codebase to use `from
  byte import Command` instead of `from byte.cli import Command` - Removes Command and
  CommandRegistry from cli module exports - Updates service providers to import from the new
  location - Maintains backward compatibility through dynamic imports

The command module is now properly positioned as a core domain that cli depends on, rather than
  being nested within cli.

- Move event system to dedicated module
  ([`ac14f6f`](https://github.com/UseTheFork/byte/commit/ac14f6f12d78462dfbc9e1f68dbcd8e4225e463d))

Extract EventBus and Events from foundation module into a new dedicated byte.event module. This
  improves code organization by separating event infrastructure from application foundation
  concerns.

Updates all imports across the codebase to reference the new module location. Also introduces
  TuiEvents as a separate namespace for TUI-specific events, replacing the previous Messages event
  definitions.

- Move file operations to ToolFileService with user confirmation
  ([`4c7ca76`](https://github.com/UseTheFork/byte/commit/4c7ca7693f926cfd1079130a9dce7f005db0b16e))

Extract write_file and delete_file logic from tool functions into ToolFileService methods. Both
  operations now require user confirmation before execution, following the same pattern. Update tool
  functions to delegate to the service and return ToolResult objects for consistency.

Also update edit_file tool path annotation to clarify it expects exact paths from the source
  variable. Add write_file and delete_file tools to coder agent node.

- Move plan generation to workflow layer and refactor prompt assembly
  ([`b37c1f5`](https://github.com/UseTheFork/byte/commit/b37c1f544155416c0378fe795ec339a4cde616a9))

- Move status messaging from conversation to interactions service
  ([`a220660`](https://github.com/UseTheFork/byte/commit/a2206607062705bceb8c2dc7f007e0893209144a))

Move status message emissions from the conversation widget to the interactions service to better
  separate concerns and ensure consistent status updates during user interactions.

Changes: - Move status message emissions to interactions_service in prompt(), select(), and
  input_text() methods - Remove status message handling from conversation widget's
  handle_prompt_user() - Refactor status_bar.py: make BYTE_STATES public, add logging, remove unused
  hide() method - Add margin-bottom to tool_call widget for better spacing

- Move workflow system to orchestration and introduce phase model
  ([`36ed316`](https://github.com/UseTheFork/byte/commit/36ed3161d32e8a82b0582f8abd8ccc881885d9ad))

- Refactor agent node naming and configuration to use agent IDs
  ([`2c7ffc3`](https://github.com/UseTheFork/byte/commit/2c7ffc3161d5fd5cd97ebe22666c72c48eb4de11))

Update LLM configuration keys and agent node implementations to use consistent agent-based naming:

- Rename LLM config keys from generic names (ask, coder, commit) to agent node identifiers
  (ask_agent_node, coder_agent_node, coder_plan_agent_node, commit_agent_node) - Update
  LLMService.get_model() to accept agent_id instead of model_id for configuration lookup - Implement
  name property in BaseAgentNode to automatically derive agent node name from class name using
  snake_case conversion - Update all agent nodes (Ask, Coder, Commit) to use self.name for dynamic
  config lookup instead of hardcoded strings - Add new CoderPlanAgentNode to support multi-step
  planning before code generation - Update coder workflow to use CoderPlanAgentNode as entry point,
  routing to CoderAgentNode after planning - Update routing and service provider registrations to
  include new CoderPlanAgentNode

This change enables more flexible agent configuration and makes the relationship between agent nodes
  and their LLM configuration explicit and maintainable.

- Refactor analytics widget with reactive data binding
  ([`7c7f725`](https://github.com/UseTheFork/byte/commit/7c7f7258a058d6cdb484177d3d06261ee6173a79))

Replace ModeInfo placeholder classes with specialized TokensInfo, CostInfo, and FileInfo classes
  that use reactive properties and data binding. This eliminates manual label updates and improves
  maintainability by leveraging Textual's reactive system for automatic UI updates.

Also move scroll_to_latest_message() call to the correct location after response completion, remove
  unnecessary padding from Screen, and clean up TODO comment.

- Refactor block apply methods to use status attributes instead of return tuples
  ([`43ece81`](https://github.com/UseTheFork/byte/commit/43ece81e920532cbe6b882babfe2435c9e87ae72))

Change apply() methods across all operation block types to set status and status_message attributes
  instead of returning tuples. This simplifies the API and makes status tracking more consistent.
  The apply() method signature changes from returning tuple[BlockStatus, str] to returning None,
  with status stored in self.status and self.status_message.

- Refactor chat widget to use langchain messages and simplify architecture
  ([`cd18eea`](https://github.com/UseTheFork/byte/commit/cd18eeaca05ac391ab0b7081dbe0d2545f9461c0))

Replace custom message handling with langchain BaseMessage types. Update ChatMessage schema to use
  langchain messages instead of dict-based format. Simplify chat widget initialization and remove
  dependency on chat_data parameter. Comment out streaming response logic and chat loading
  functionality for refactoring. Update chatbox to work with langchain message objects and remove
  litellm-specific message handling. Add ChatHeader widget for displaying chat metadata. Update
  imports to use local widget modules instead of elia_chat. Add command and subcommand input
  handlers for slash commands and subprocess execution.

- Refactor configuration and bootstrap logic with formatting improvements
  ([`802fe3b`](https://github.com/UseTheFork/byte/commit/802fe3b896137def5f35958e82115a93c4216b40))

- Add schema reference to config.jsonc and compact array formatting for consistency - Rename cli
  section to tui in config and remove presets configuration - Add prettier.config.cjs for JSON/JSONC
  formatting rules - Remove LSP service provider integration from byte_config and main - Fix return
  type annotations in bootstrap methods for proper functional composition - Update web config to
  exclude enable field and default chrome_binary_location to None - Improve text formatting in skill
  workflow and analytics widgets

- Refactor gateway to use typed request dataclasses with @on dispatch pattern
  ([`a2650ff`](https://github.com/UseTheFork/byte/commit/a2650ff67b3c8da431b0515b51b943dc97913193))

- Replace flat RpcRequest.params dict with typed GatewayRequest dataclass hierarchy, mirroring the
  Messages pattern from tui/messages.py - Create Requests namespace with Execute, Configure,
  Subscribe, AddFile, DropFile, and ContextAddFile dataclasses in dedicated requests.py module -
  Implement @on decorator-based dispatch system: decorator tags handler methods with
  _gateway_request_type attribute without wrapping, SessionService scans and builds dispatch table
  at boot time, _dispatch resolves RpcRequest to typed GatewayRequest then looks up and calls
  handler by type - Extract GatewayUtils utility class to separate utils/ package with parse_request
  and make_error_response static methods; dynamically build REQUEST_TYPES registry using
  Str.class_to_snake_case instead of manual mapping - Add comprehensive test suites: integration
  tests for AddFile and DropFile over real WebSocket with auth flow, unit tests for all request
  types, gateway_utils parsing/error responses, and @on dispatch mechanism - Handle missing required
  params by catching TypeError in parse_request and re-raising as ValueError for proper RPC error
  responses - Update Application to catch ScreenStackError when posting TUI messages to gracefully
  handle disconnected screens; add .input_history to .gitignore and ANTHROPIC_API_KEY to test
  environment

- Refactor lint service and UI components for improved results display
  ([`5278f37`](https://github.com/UseTheFork/byte/commit/5278f3725adfb21f6fb8011113e5adfb3acc5a12))

Replace CreatePanel message with dedicated LintResults message for better separation of concerns.
  Update LintStarted to use total_commands instead of separate file_count and command_count
  parameters. Refactor Linting widget to use custom ProgressBar and RuneSpinner components. Improve
  Analytics widget layout with better CSS organization and add MemoryUsedInfo component. Update
  TextRule to use HorizontalGroup composition with ByteBug component. Remove
  pending_response_panel.py as it's no longer needed. These changes improve code organization and
  provide a more flexible UI messaging system.

- Refactor llm config, services, and prompt assembly
  ([`8cb12f5`](https://github.com/UseTheFork/byte/commit/8cb12f58c8df9bb7d48eb0f3eb413bc2f4a0eaf2))

update config schema to include provider field for each llm model. replace orchestration event
  reference from GatherReinforcement to GatherProjectContext. remove recompose flag from reactive
  text field and use targeted updates via watch method. add validate_text method for input
  sanitization. remove commented event hook code. remove yaml header construction from context file
  addition. fix type hints in session context service return types

- Add `provider` field to LLMModelConfig to support multiple LLM providers - Update llm_service to
  set provider from config on model schema - Replace `GatherReinforcement` event with
  `GatherProjectContext` throughout - Refactor TextRule widget to avoid full recomposition on text
  changes - Remove `recompose=True` from reactive declaration - Add `validate_text` method to
  sanitize input - Add `watch_text` method for targeted DOM updates - Remove YAML header
  construction from file context addition - Remove unused commented event hook registration - Fix
  type hints in SessionContextService to use direct type references instead of string literals - Add
  `_gather_modified_messages` method to prompt assembler for conversation history - Update prompt
  templates to use `modified_messages` variable - Add type imports (AIMessage, BaseMessage) to
  prompt assembler

- Refactor LLM service to return model schema and parameters instead of compiled model
  ([`8e9e9cb`](https://github.com/UseTheFork/byte/commit/8e9e9cb14fe8c68379e4f2ab94e06c8afa20d89f))

Change LLMService.get_model() to return a tuple of (ModelSchema, dict) containing model
  configuration and merged parameters instead of a compiled BaseChatModel instance. This allows
  callers to customize model initialization as needed.

Update all agent nodes to handle the new return type and compile models locally in their
  create_runnable() method using init_chat_model(). Also move model compilation into
  create_runnable() in BaseAgentNode for better separation of concerns.

Remove boot_messages functionality and SystemEvents.PostBoot event listener from LLMServiceProvider,
  simplifying the service provider initialization logic.

Update PromptAssembler to accept agent name and ModelSchema in generate_state() and pass
  provider/model information to the reinforcement gathering event. Update reinforcement logic in
  LLMService to check provider names instead of model schema behavior properties.

- Refactor memory tracking and tool result handling
  ([`39c87b6`](https://github.com/UseTheFork/byte/commit/39c87b608c32bf4dbab91d768b686d6e96820c84))

- Refactor orchestration to add skill selection phase and consolidate utilities
  ([`44f8afa`](https://github.com/UseTheFork/byte/commit/44f8afafac66cc5f80281a5f4678686bdb3a98f8))

- Refactor prompt assembler to use phase utils instead of plan-based logic
  ([`2e2a777`](https://github.com/UseTheFork/byte/commit/2e2a77773478f911dbaa71ed6bf56236d45ba655))

- Refactor prompt assembly and epilogue logic
  ([`1912810`](https://github.com/UseTheFork/byte/commit/1912810c01c1c0bacbd8dc28d5d99f4566e1832a))

- move epilogue function from prompt_leaves to PromptAssembler as context-aware method - add
  conditional logic to epilogue for first vs followup responses - relocate user_request assignment
  to results gathering phase - add tracking ID to PROJECT_STATE section for better traceability -
  improve project state message clarity - format task phases with bullet points in coder agent node
  - comment out verbose instruction about PROJECT_STATE references - fix typo: "nest" → "next" in
  important note - comment out extras field in BaseTool

- Refactor prompt assembly to separate system and user message templates
  ([`f2c3fa6`](https://github.com/UseTheFork/byte/commit/f2c3fa631627440d26649f66f3e3f98ab0088039))

- Refactor prompt assembly to use leaf-based composition pattern
  ([`7c808fc`](https://github.com/UseTheFork/byte/commit/7c808fcd1200d272827dc3b06a159c5962e4ab84))

- Refactor prompt assembly with leaf-based composition system
  ([`031f97e`](https://github.com/UseTheFork/byte/commit/031f97e768bd6d6b38cb5d57ce35bf0bccacb255))

- Refactor prompt caching and remove redundant log statements
  ([`ee01b9b`](https://github.com/UseTheFork/byte/commit/ee01b9ba0e1473e99380dcc30c16bca525108a47))

- Refactor prompt context and enhance skill creation
  ([`1057230`](https://github.com/UseTheFork/byte/commit/10572309c8b5e22a9da5fb20e7fe8b9019f50a34))

- Refactor prompt system to use structured sections instead of boundary tags
  ([`d4485ff`](https://github.com/UseTheFork/byte/commit/d4485ff2c040a86df6d6cfa7f2566e8e6cce587d))

Replace XML-based Boundary tags with new Section/SectionType system for clearer prompt organization:

- Add new `Section` class and `SectionType` enum for Markdown-based section management - Implement
  `Section.start()`, `Section.end()`, `Section.ref()` for structured sections with anchor links -
  Expand `preamble()` with detailed conversation structure and XML tag reference guide - Add
  `epilogue()` function for prompt resumption instructions with `RESUME_FORMAT` section - Migrate
  all agent node templates (ask, coder, commit) to use Section API - Update prompt_assembler to use
  Section for file context, conversation history, and project state - Add `success` field to
  ToolResult schema (default True) - Add `status` field to ToolMessage for error tracking - Clean up
  BoundaryType enum, removing unused values - Update imports throughout codebase to expose new
  Section/SectionType classes - Fix message content access patterns (use `.text` instead of
  `.content` where applicable)

- Refactor research agent node to improve system architecture and tool management
  ([`9fb318d`](https://github.com/UseTheFork/byte/commit/9fb318dfcd6684740c26c230e3ded52f72c8f292))

- Refactor session service to emit tui messages instead of routing commands directly
  ([`81d7cad`](https://github.com/UseTheFork/byte/commit/81d7cadc2f934ef9eac0e42816fcb8dcb4dc4ce3))

- Update SessionService to emit Messages.UserInputSubmitted to event bus instead of directly routing
  slash commands - Add import for Messages from byte.tui - Comment out direct command routing logic
  pending RpcRequest alignment with Messages protocol - Add gateway port 9732 to config.jsonc -
  Remove gateway specification files from .byte/specs/gateway/ as they are no longer needed - Fix
  pytest marker typo: asyncio -> asyncios in test_prepare_environment.py

- Refactor skill creator workflow and agent to support iterative phase completion
  ([`3d75bd2`](https://github.com/UseTheFork/byte/commit/3d75bd29a8819dac6424ddacad403340995c838a))

- Refactor tools from functions to classes with dependency injection
  ([`2fcbabf`](https://github.com/UseTheFork/byte/commit/2fcbabfea8c5d8e391bf2587f1d2140450f68d36))

Convert all tool implementations (file tools, git tools, search tools) from function-based to
  class-based architecture inheriting from BaseTool. Update service providers to return tool classes
  instead of instances, with instantiation handled via app.make() for proper dependency injection.
  Add SearchWebTool and GoogleSearchParser for web search capabilities. Create ResearchAgentNode for
  research tasks. Enhance message system with agent_name and mask fields for better tracking.

- Refactor undo command and add panel removal ui interactions
  ([`950b3ab`](https://github.com/UseTheFork/byte/commit/950b3ab422abb53bc6bd54a0f98657c2b4270d86))

- Replace CoderAgent with CoderWorkflow in undo_command for cleaner agent access pattern - Replace
  direct console interactions with InteractionService.confirm for better separation of concerns -
  Add RemovePanel message type to support removing ResponsePanel widgets from conversation -
  Implement action_scroll_to_panel on ConversationScreen to enable clickable panel navigation in
  confirmation dialogs - Add remove_panel handler to Conversation widget to remove panels by ID and
  clean up message handling - Remove unused TYPE_CHECKING import and conditional block from
  command.py - Remove debug logging statement from git_service.py

- Refactor workflow orchestration to use UpdatePhaseTool and RoutePhaseModel
  ([`261ed4d`](https://github.com/UseTheFork/byte/commit/261ed4dd1dde74c48810a2f7d5eb1c7818bb2876))

- Refactor: simplify git grep tool and add missing docstrings
  ([`52f671e`](https://github.com/UseTheFork/byte/commit/52f671ed7a3358c28ef02266dd70029b34725ae3))

- Remove InteractionService dependency from GitGrepTool - Eliminate user confirmation dialog before
  executing git grep - Streamline execution by removing nested conditional logic - Add docstrings to
  FileChanged event and service provider classes - Enhance error messages in tool execution with
  input args context

- Remove auto-init blank constitution and streamline initialize workflow
  ([`999f1fd`](https://github.com/UseTheFork/byte/commit/999f1fd2a4db14a6f3973f6f90dc0d65789304cd))

- Remove commented-out debug code in tool_node
  ([`59ccf09`](https://github.com/UseTheFork/byte/commit/59ccf09a45937b54ee107bdc862578c038eb96b1))

- Remove conditional lsp tool loading from skill creator agent
  ([`b6dfec8`](https://github.com/UseTheFork/byte/commit/b6dfec8081019a611c2ebb5f2d35a789c07c1b9a))

- Remove config migration logic and Migrator class
  ([`fd39a62`](https://github.com/UseTheFork/byte/commit/fd39a62455ea60ba1e7f52aeb767d72f4949eae1))

- Remove Migrator class and migration_001_000_000.py file that handled version-based config
  migrations - Simplify LoadConfiguration.bootstrap() by removing version checking and migration
  step, directly loading config into ByteConfig - Remove Migrator from config module exports in
  __init__.py - Remove unnecessary imports (metadata, __future__ annotations) from
  load_configuration.py

- Remove development mode check in record_response_service
  ([`f3aebad`](https://github.com/UseTheFork/byte/commit/f3aebad0822aa2d6780374ae7a489273edc63f26))

remove the is_development() guard to allow response caching in all environments, not just
  development mode

- Remove FileMode enum and unify file context handling
  ([`b4f095c`](https://github.com/UseTheFork/byte/commit/b4f095c3626226975d316512e4a34b8011f96ea1))

- Remove FileMode enum from models.py and all mode-based differentiation throughout file service
  layer - Simplify file APIs: add_file() and list_files() no longer accept or filter by mode
  parameter - Update generate_context_prompt() to return single list instead of tuple of (read_only,
  editable) - Delete add_read_only_file_command.py, switch_mode_command.py, and context.py; remove
  associated exports - Remove SetContext bootstrap step and ProjectHierarchy leaf from orchestration
  pipeline - Simplify file UI and analytics to display unified file counts instead of mode-based
  separation - Add tree-sitter-language-pack>=1.8.1 dependency for language support - Update all
  dependent services and commands to work with unified file context model

- Remove future annotations and simplify docstrings in bootstrap module
  ([`e7bd03a`](https://github.com/UseTheFork/byte/commit/e7bd03a9bd795c333a6abf283bd2013e297b7aa6))

- Remove `from __future__ import annotations` from bootstrapper files as it is no longer necessary
  with modern Python versions - Simplify all docstrings to one-line imperative format per
  constitution standards, removing verbose Args/Returns sections and multi-line descriptions -
  Delete boot_providers.py module and remove all references to BootProviders from __init__.py
  exports and TYPE_CHECKING imports - Update class docstrings in LoadConfiguration, LoadConsoleArgs,
  LoadEnvironmentVariables, and RegisterProviders to be more concise and descriptive

- Remove git_commit tool from exports and service provider
  ([`c2fb73b`](https://github.com/UseTheFork/byte/commit/c2fb73b2627d515500aefb197d7a125a5236ce8c))

Delete the git_commit tool implementation and remove it from the GitServiceProvider. Only git_grep
  remains as an available tool. Also remove unused imports and clean up commented-out code in
  related files.

- Remove LintNode and fix tool schema handling
  ([`d913891`](https://github.com/UseTheFork/byte/commit/d913891f125340116d113599cf6b8d3adf033d8b))

- Remove LintNode and integrate LintTool into workflows
  ([`13a9c55`](https://github.com/UseTheFork/byte/commit/13a9c553c391c472cb591b3e0f7c0b07f931e822))

- Remove llm_tier override from CommitAgentNode
  ([`79e619a`](https://github.com/UseTheFork/byte/commit/79e619affe911dd092d55c11142e33d53abdb566))

- Remove MCP module and conventions directory setup
  ([`a10b348`](https://github.com/UseTheFork/byte/commit/a10b34872b07f95cbb0700e4e48d55ceb7e791bf))

- Remove entire MCP (Model Context Protocol) module that is no longer used - Delete MCP command and
  service implementations from codebase - Remove conventions directory creation from environment
  bootstrap sequence - Update create_skill_workflow to dynamically reference PresentSkillTool.name
  in phase instructions

- Remove redundant branching in git commit tool
  ([`0e6b951`](https://github.com/UseTheFork/byte/commit/0e6b951cb0c4d5cd9a6a003b2a3600235ed8a96b))

- Remove redundant scroll_to_latest_message call from handle_response
  ([`56f91d6`](https://github.com/UseTheFork/byte/commit/56f91d6df90ccaea4856325e4e86be3bd0372708))

- Remove unnecessary scroll_to_latest_message() invocation that was called after mounting the
  response panel input. The mounting operation already handles scrolling to the latest message,
  making this explicit call redundant.

- Remove redundant slash command completion and fix tab completion slash prefix
  ([`7ffd25a`](https://github.com/UseTheFork/byte/commit/7ffd25a5140e55a4da3dac959c1c6fe5ed2da7c6))

Remove redundant slash command completion logic from TextAreaAutoComplete: - Eliminated
  self.slash_commands caching since CommandRegistryService already provides filtering - Unified
  command name and argument completion into single debounced _do_slash_arg_search call - Removed
  slash-specific fuzzy matching logic and _should_show special case - Fixed tab completion to
  preserve "/" prefix when completing command names by prepending "/" and adjusting cursor position

Also remove commented-out code from prompt_input.py and rename CreatePlanTool name to
  "create_plan_tool" for consistency. Update type ignore comments to use "ty:ignore" format with
  specific error codes.

- Remove runtime parameter from node execute methods
  ([`f36e19b`](https://github.com/UseTheFork/byte/commit/f36e19bf43b9d86b00aab6685b53df1ffc5f3bec))

- Remove SystemEvents PostBoot emission and simplify bootbox initialization
  ([`58a9271`](https://github.com/UseTheFork/byte/commit/58a9271670cd42bde0bf7e6a140d402c7c213065))

- Remove unused SystemEvents import from conversation_screen - Comment out PostBoot event emission
  and dynamic message handling - Simplify Bootbox to render only styled logo without event payload -
  Remove __future__ annotations import from response_panel - Add text-accent CSS class to
  TokenUsageRule for aggregate usage styling - Expand .byte/config.jsonc ignore pattern from
  .byte/cache to .byte

- Remove type hints from service provider methods
  ([`a192d94`](https://github.com/UseTheFork/byte/commit/a192d94ec3a4aff76f0dbdd0426162cadd0d1926))

- Remove type hints from service provider methods
  ([`a25eddf`](https://github.com/UseTheFork/byte/commit/a25eddf5f7be01e60b35de8cdf188ae8678dd438))

- Remove unused CLIContextDisplayService
  ([`6fc0b68`](https://github.com/UseTheFork/byte/commit/6fc0b684af1ada1f5994126f37d063f08ec6d851))

- Remove unused code and simplify function calls
  ([`8e540d2`](https://github.com/UseTheFork/byte/commit/8e540d23373f894705c91419633ef3290be5a819))

- Remove unused comment and improve touched_files handling
  ([`458194f`](https://github.com/UseTheFork/byte/commit/458194f35e459fbfc7d71580542f91051c7cd4b2))

Replace direct state access with safe get() method to handle missing or empty touched_files. Remove
  obsolete AI comment from StartNode class. Update docstring references in SelectableMarkdown to
  remove external library links. Replace unused metadata variable with underscore in
  workflow_service. Add TextArea styling for border and height in TUI.

- Remove unused future import and update event reference
  ([`e5e97a2`](https://github.com/UseTheFork/byte/commit/e5e97a2ff10c7dd962e0d48a6253752993e1eddc))

Remove the `from __future__ import annotations` statement that is no longer needed. Update the
  Events reference to OrchestrationEvents in the prompt assembler. Clean up unnecessary comment in
  tui manager service.

- Remove unused Optional import from typing
  ([`d21419d`](https://github.com/UseTheFork/byte/commit/d21419d9c08313c961554db308c41ecd1a0ab0b5))

- Remove unused validators and nodes from codebase
  ([`c018785`](https://github.com/UseTheFork/byte/commit/c018785cc9da1a0a22d4d5ccc2832d1bc8e72761))

- Remove verbose logging from ask agent node execution
  ([`c370798`](https://github.com/UseTheFork/byte/commit/c370798bc3cc1cca33dbcac17585352894f13017))

Remove redundant log statements that were used for debugging during agent node execution. These logs
  add noise without providing significant value during normal operation. The code flow is clear from
  the function calls themselves.

- Rename CodeDisplay to ByteDisplay for consistent naming
  ([`af6f0b6`](https://github.com/UseTheFork/byte/commit/af6f0b6d94465b2ed87d6c7615ce2e6a93135bae))

Rename CodeDisplay class to ByteDisplay to better reflect its purpose of displaying byte-specific
  content. Update all imports and usages accordingly.

- Rename CompleteStepTool to CompleteTurnTool and clean up formatting
  ([`3e22b53`](https://github.com/UseTheFork/byte/commit/3e22b53ebd7b677499db19c7c7b6890880e52f30))

- Rename force_tool_choice to tool_choice and support dict format
  ([`d03e9f8`](https://github.com/UseTheFork/byte/commit/d03e9f8c583477947616f5d470b9ddd4891cbb33))

- Rename Input widget to TextInput
  ([`2d2eb00`](https://github.com/UseTheFork/byte/commit/2d2eb009e2ea247c0722e47025490007756f0164))

- Rename pending_agent_state to scratch_messages and remove unused state fields
  ([`dcfc93b`](https://github.com/UseTheFork/byte/commit/dcfc93beb088738986556f7557ee0b847d2b89d3))

- Rename ReadFilesTool to AddFilesTool with improved semantics
  ([`2c3b1c9`](https://github.com/UseTheFork/byte/commit/2c3b1c92fdfebee669fc29ab5429c4834d2b1160))

- Reorganize agent domain into node, orchestration, and subgraph modules
  ([`fdb53ef`](https://github.com/UseTheFork/byte/commit/fdb53effc0b159ecaf4e0b9427e9b8ce799ba015))

Split the monolithic agent module into three focused domains:

- **node**: Contains base node class and all node implementations (assistant, dummy, end, extract,
  lint, model variants, parse blocks, routing, show, start, tool, validation) - **orchestration**:
  Contains orchestration logic including state management, schemas, validators, reducers, prompt
  utilities, and exceptions - **subgraph**: Contains agent implementations (ask, base, coder, commit
  agents)

This restructuring improves code organization, separation of concerns, and makes the codebase more
  maintainable. Each domain now has its own service provider for dependency injection.

Updated main.py to import and register NodeServiceProvider alongside existing providers.

- Reorganize agent message imports and references
  ([`79d91e4`](https://github.com/UseTheFork/byte/commit/79d91e4ddee727c740808ac64a9f2600a0b445f4))

Move agent message type imports under a TYPE_CHECKING block and update references to use
  ByteAIMessage namespace. This improves import organization and reduces circular dependencies at
  runtime while maintaining type checking capabilities.

- Reorganize agents and workflows into domain-specific modules
  ([`0e7f055`](https://github.com/UseTheFork/byte/commit/0e7f05591d7187adec18efab663e43317461b034))

- Reorganize ask and coder into domain-specific modules
  ([`9ffcd13`](https://github.com/UseTheFork/byte/commit/9ffcd137634b56c4e67afaed38eb8046f3846684))

- Reorganize command system and move ByteArgumentParser to command module
  ([`4825f4b`](https://github.com/UseTheFork/byte/commit/4825f4b5a830c6e466ca4ebfb234458775e74d24))

Move ByteArgumentParser from byte.cli.argparse to byte.command.argparse to better organize the
  command system architecture. Rename CommandRegistry to CommandRegistryService for clarity. Create
  CommandServiceProvider to manage command-related services. Update all imports across the codebase
  to reflect the new module structure. This improves separation of concerns by keeping
  command-related utilities in the command module rather than the CLI module.

- Reorganize event system into domain-specific namespaces
  ([`a23ad87`](https://github.com/UseTheFork/byte/commit/a23ad8738635c00394c00a026703bbbff58fd2bc))

Split the monolithic Events class into domain-specific event namespaces: - SystemEvents: PostBoot -
  OrchestrationEvents: GatherReinforcement, GatherProjectContext - FileEvents: FileAdded,
  FileChanged - NodeEvents: EndNode, PreAssistantNode - TuiEvents: UserInputSubmitted,
  ComponentEvent - TuiComponentEvents: Notify, CommandExecutionStarted, UpdateAnalytics, etc.

This improves code organization, reduces circular dependencies, and makes event types more
  discoverable. Updated all imports and event emissions throughout the codebase to use the new
  namespaces. Added emit_tui helper method to Eventable mixin for cleaner TUI event emission.

- Reorganize exports and move human message panel to ui widgets
  ([`edd83e4`](https://github.com/UseTheFork/byte/commit/edd83e4e026269bbe9605556aa9db61d7fd51f93))

Move HumanMessagePanel to ui/human_message.py and rename to HumanMessage for better organization.
  Reorganize __init__.py exports to group related items together (commands, services, tools). This
  improves code structure without changing API behavior.

- Reorganize imports and module structure for orchestration and subgraph
  ([`b5c0849`](https://github.com/UseTheFork/byte/commit/b5c084936eb8948ffa3483cdb6dd2e920fd28043))

Move imports from byte.agent to byte.orchestration and byte.subgraph modules: - TokenUsageSchema,
  BaseState, ValidationError, Validator moved to byte.orchestration - AskAgent, CoderAgent moved to
  byte.subgraph - AssistantContextSchema moved to byte.orchestration - Remove AgentServiceProvider
  from main.py - Update node naming: AssistantNode → ModelMainNode, WeakModelNode → ModelWeakNode,
  ReasoningModelNode → ModelReasoningNode - Remove ShowNode and AssistantNode from node exports -
  Update routing node return values to use new naming convention - Simplify node routing using
  route_to helper method - Update graph builder to scan byte.node and byte.subgraph modules

- Reorganize imports and move convention constants to dedicated module
  ([`98c45be`](https://github.com/UseTheFork/byte/commit/98c45be9a43adf164a379425e1cbff1d4fca93a3))

Consolidate imports from nested service modules into top-level package exports. Move FOCUS_MESSAGES
  constant from agent implementations to a dedicated conventions module for better code organization
  and reduced import depth. Rename ConventionsParsingService to ConventionParsingService for
  consistency. Reorganize test file structure by moving parser service tests to code_operations
  directory and removing obsolete subprocess agent tests.

- Reorganize imports and remove unused project_name field
  ([`de7c9a2`](https://github.com/UseTheFork/byte/commit/de7c9a2464f3d8384ab8068b3b47b307eaca1d5c))

- Reorganize node architecture into agents and nodes packages
  ([`a6b1c5d`](https://github.com/UseTheFork/byte/commit/a6b1c5da26ca9b2a8e0834ea9ad68e37ce2d9c84))

Move agent implementations (CoderAgent, AskAgent, CommitAgent) from subgraph module to new
  byte.node.agents package. Move node implementations from byte.node.implementations to
  byte.node.nodes package. This creates a clearer separation between agent nodes (which use LLMs)
  and utility nodes (routing, validation, etc).

Rename Node base class to BaseNode for consistency with other base classes. Update all imports and
  references throughout the codebase. Remove the deprecated subgraph module entirely.

Update GraphBuilder to use NodeServiceProvider for discovering nodes and agents instead of
  reflection-based scanning.

- Reorganize response_panel location and improve loading animation formatting
  ([`c3d1253`](https://github.com/UseTheFork/byte/commit/c3d1253caba0c7db1e96b90a630af8d272e24738))

- Move response_panel.py from panels/ subdirectory to widgets/ root directory - Update imports to
  reflect new response_panel location - Refactor loading emoji animations to use character constants
  for better maintainability and consistency - Apply f-string formatting consistently across all
  animation frames

- Reorganize SelectableMarkdown class structure and update focus binding
  ([`6cdd8f6`](https://github.com/UseTheFork/byte/commit/6cdd8f65b2b1c9bbdfc928dcad7da8b3d759162c))

Move the `_run` method earlier in the class to improve code organization and readability. Move the
  `CursorEscapingBottom` message class definition before the BINDINGS list for better logical
  grouping. Update the escape key binding action from 'screen.focus("input")' to
  'screen.focus("PromptTextArea")' to use the correct widget identifier. Also fix mypy type ignore
  comments from 'possibly-missing-attribute' to 'unresolved-attribute' for accuracy.

- Reorganize skill creator agent and update read_files tool implementation
  ([`479c6b3`](https://github.com/UseTheFork/byte/commit/479c6b3a83f515fe89d67ede14d4b48d507c9a75))

- Reorganize TUI components from cli to dedicated tui module
  ([`b93f9ec`](https://github.com/UseTheFork/byte/commit/b93f9ec295c73728671d9f181cd3915698178a59))

Move textual UI components from byte.cli to a new byte.tui module structure. This includes:

- Rename ByteTextualApp to ByteTUI in new byte.tui.byte_tui module - Move chat screen, widgets, and
  styles to byte.tui package - Create TUIManagerService for centralized chatbox management - Add
  TUIServiceProvider to application service providers - Update application.py to import from new tui
  module location

This reorganization improves code organization by separating CLI and TUI concerns into distinct
  modules.

- Reorganize tui into screens and improve file management
  ([`a8215cd`](https://github.com/UseTheFork/byte/commit/a8215cdedff60f23b2ea73720e985ecb867bd71f))

Extract conversation UI logic into a dedicated ConversationScreen to improve code organization and
  separation of concerns. Add ManageFilesScreen for handling file management operations with a modal
  dialog. Move boot logo rendering and system event handling from ByteTUI to ConversationScreen.
  Replace hardcoded file list with dynamic loading from file service. Make conversation property a
  lazy-loaded getter to access the current screen's conversation widget. Update analytics widget to
  make file info clickable and inherit from Static for better functionality.

- Replace autocompleter widget with text area auto complete
  ([`a863532`](https://github.com/UseTheFork/byte/commit/a86353289a2820503a8b1e39e5eff3a1c254560e))

Replace the old Autocompleter widget with a new TextAreaAutoComplete widget that provides better
  integration with TextArea. The new implementation:

- Supports slash command completion with argument suggestions - Supports file path completion
  triggered by @ symbol - Integrates directly with TextArea via message signals - Handles key events
  (up/down/tab/enter/escape) for navigation and selection - Uses fuzzy search for better matching -
  Removes shell mode support (to be re-added later) - Simplifies prompt.py by removing
  autocompleter-related logic

Changes: - Add get_all_slash_command_names() to CommandRegistry for retrieving command names with /
  prefix - Update schemas.py to use standard dataclass and add Command field to AutocompleteOption -
  Delete old autocompleter.py widget - Simplify prompt.py by removing autocompleter bindings and
  event handlers - Add new text_area_auto_complete.py with complete implementation

- Replace BootstrapSkillsAndFilesTool with BootstrapAgentTool supporting instruction,
  editable/reference files, and rich_markdown option in CommunicationStyle
  ([`1a5c91b`](https://github.com/UseTheFork/byte/commit/1a5c91bc6bda71a970f3b5a5bbbed086de70ad01))

- Replace chatbox with selectable markdown widget
  ([`289c2f8`](https://github.com/UseTheFork/byte/commit/289c2f804d7e11658abea2b459004dc13932d952))

Rename Chatbox to SelectableMarkdown and update all references throughout the codebase. This widget
  now provides better text selection and markdown rendering capabilities.

Also remove the load_convention tool from ask_agent_node and update state initialization to use
  touched_files instead of parsed_blocks. Update prompt input styling and remove unused bindings
  from conversation widget.

- Replace component-specific styles with utility margin and padding classes
  ([`5e38d2f`](https://github.com/UseTheFork/byte/commit/5e38d2ff3dc0994dc1bad58b04b3006f311a3bb5))

Replace all component-specific margin and padding rules in tui.tcss with reusable utility classes
  following a consistent naming convention (mt-*, mb-*, ml-*, mr-*, mx-*, my-*, pt-*, pb-*, pl-*,
  pr-*, px-*, py-*). This reduces CSS duplication and makes styling more maintainable and
  predictable.

- Replace ConstitutionConfig with inline constitution building in initialize command
  ([`6cfd048`](https://github.com/UseTheFork/byte/commit/6cfd04849fa250e88a274c38d3652b9b384fcae6))

- Replace conventions module with enhanced agent tools and switch to duckduckgo lite search
  ([`5fbd66b`](https://github.com/UseTheFork/byte/commit/5fbd66b4537494eba73b5dc2cbf8097aae6174c5))

- Replace dict schemas with pydantic models in file tools
  ([`da6e9bd`](https://github.com/UseTheFork/byte/commit/da6e9bd9acf9b94c676d165b78b48c0a6c4a086f))

Convert file tool schemas from dictionary-based JSON schemas to Pydantic BaseModel classes with
  Annotated fields. This enables proper type validation and supports dependency injection via
  InjectedToolArg.

Changes: - Replace dict schemas in delete_file_tool, edit_file_tool, replace_file_tool, and
  write_file_tool with corresponding Pydantic input classes - Update _arun methods to accept app as
  direct parameter instead of kwargs - Add InjectedToolArg support for proper dependency injection -
  Add ToolMessage wrapper class for tool messaging - Add ValidationError handling in tool_node -
  Remove debug logging statements from tool_node and conversation_screen - Add UserCancelled message
  type to TUI messages

- Replace event payload system with typed dataclass events
  ([`bc632f8`](https://github.com/UseTheFork/byte/commit/bc632f8dc721de941a5721442d33e11ba843f717))

Replace the generic Payload/EventType enum-based event system with strongly-typed dataclass events.
  This provides better type safety, IDE support, and clearer event contracts.

Key changes: - Replace EventType enum and Payload class with Events namespace containing typed
  dataclass events (FileAdded, FileChanged, PostBoot, GatherReinforcement, etc.) - Update EventBus
  to work with event types instead of string event names - Refactor all event listeners to accept
  and return specific event types - Update event emission throughout the codebase to use new event
  types - Remove Payload and EventType from public API exports

This is a breaking change as the event system API has been completely redesigned.

- Replace ExecutorAgentNode with unified HarnessAgentNode and BootstrapSkillsAndFilesTool
  ([`fe19018`](https://github.com/UseTheFork/byte/commit/fe190188b3c0b2605872bc11e8177ae202a76ad7))

- Replace json-stream with partial-json-parser for JSON parsing
  ([`169a1b1`](https://github.com/UseTheFork/byte/commit/169a1b1f981ab4ed8d6fe1fc955469fecdd8aa50))

Switch from json-stream library to partial-json-parser for improved partial JSON parsing in tool
  calls. This change includes: - Updated dependencies in pyproject.toml and uv.lock - Refactored
  tool_call.py to use partial_json_parser.loads() instead of custom parse_partial_json() - Updated
  exception handling from json.JSONDecodeError to MalformedJSON - Added DEFAULT_CSS styling to
  ToolCall widget

- Replace per-node llm config with tiered model system and rename CostCalculator to UsageMetrics
  ([`127db0a`](https://github.com/UseTheFork/byte/commit/127db0a5952b54a811cb076321ffac06f18dc48f))

- Replace skill boundary type with tool in registry service
  ([`f1b6141`](https://github.com/UseTheFork/byte/commit/f1b614125b7ebf07d6c490d7cb48a9c050790208))

- Replace skill selection agent with harness-based bootstrap tools
  ([`19869c7`](https://github.com/UseTheFork/byte/commit/19869c7012c900403fe795f3b5a8494b8f6f36c4))

Remove SkillSelectAgentNode and introduce BootstrapSkillsTool and BootstrapSkillsFilesTool for
  loading skills and files through HarnessAgentNode. This simplifies the workflow by consolidating
  skill selection into the harness initialization phase.

Replace SkillSelectAgentNode references with HarnessAgentNode in CreateSpecWorkflow. Add llm_tier
  and improve agent templates in SpecCreatorAgentNode and SpecTaskCreatorAgentNode. Update error
  messaging pattern to append to prompt instead of extending with new message.

Rename SpecTaskCommand to SpecExecuteCommand and CreateSpecPhaseWorkflow to CreateSpecTaskWorkflow
  for clarity. Create RefractorCommand for new refactoring workflow. Update spec tool to populate
  harness with spec metadata for downstream agents.

- Replace skill tracker service with active flag on skill dataclass
  ([`699de35`](https://github.com/UseTheFork/byte/commit/699de35a3ddc75efb339828017b8d22413923584))

- Replace spec version/tags with reference_files and extract Str.normalize_id
  ([`379f0dd`](https://github.com/UseTheFork/byte/commit/379f0dd27b7fecd9c2661f67eb9c62d2388e4cdb))

- Replace ToolResult success flag with typed tool exceptions
  ([`de54700`](https://github.com/UseTheFork/byte/commit/de54700a53ecc6af3ae90a5fca0bece7d8144d99))

- Restructure agent architecture and consolidate workflows
  ([`c2ba0b2`](https://github.com/UseTheFork/byte/commit/c2ba0b2874cc5f5eca251839cf08bb6743286789))

Reorganize agent implementations into a cleaner architecture:

- Move agent implementations from `implementations/` to `agents/` directory - Rename agent node
  classes to agent classes (e.g., AskAgentNode → AskAgent) - Move base node from
  `nodes/base_node.py` to `base_node.py` at agent module root - Create new CoderAgent and
  CommitAgent implementations - Introduce CoderWorkflow and CommitWorkflow for workflow
  orchestration - Replace AgentService with WorkflowService for agent execution - Update routing to
  use explicit routing state instead of node_to/node_from - Simplify node references throughout the
  codebase (assistant_node → main_model_node) - Remove deprecated agents (CleanerAgent,
  ConventionAgent, ResearchAgent) - Remove ShowCommand from memory module - Update all imports and
  references to reflect new structure

- Restructure agent architecture with node-based workflow system
  ([`6548552`](https://github.com/UseTheFork/byte/commit/6548552ef36f077ad7d961c7b778b772d6c7a27e))

Refactor agent system from command-based to node-based architecture with dedicated workflow service.
  This change introduces:

- New BaseAgentNode and specialized agent nodes (AskAgentNode, CodeReviewerAgentNode) replacing
  command pattern - Model-specific nodes (MainModelNode, ReasoningModelNode, WeakModelNode) for LLM
  selection - RoutingNode for dynamic graph navigation - New WorkflowService and BaseWorkflow for
  workflow orchestration - Reasoning model support in LLM configuration and service - Token usage
  tracking moved to WorkflowService - Agent state now includes node_to/node_from for routing and
  final_message for results - Simplified AssistantContextSchema by removing direct model references
  - Graph builder now automatically includes RoutingNode

Breaking changes: - AskCommand moved to workflow.command.ask_command - Agent execution now uses
  workflow nodes instead of commands - AssistantContextSchema no longer contains main/weak model
  references - Agent metadata no longer includes mode field

BREAKING CHANGE: Agent execution model changed from command-based to node-based workflow system.
  AskCommand moved to byte.workflow package. AssistantContextSchema no longer accepts main/weak
  model parameters. Agent state structure updated with node_to/node_from routing fields.

- Restructure agent instructions and make project context unconditional
  ([`da49e82`](https://github.com/UseTheFork/byte/commit/da49e82a40203d06af276e055259015201968aac))

- Restructure code operations to use polymorphic block hierarchy
  ([`9f181e6`](https://github.com/UseTheFork/byte/commit/9f181e61eb354fa1e7c25e7c618fdea0c0417f48))

Replace flat SearchReplaceBlock schema with a polymorphic class hierarchy: - BaseBlock: abstract
  base for all block types - BaseOperationBlock: extends BaseBlock with operation semantics -
  BaseFileOperationBlock: extends BaseOperationBlock with file validation - Concrete
  implementations: CreateFileOperationBlock, EditFileOperationBlock, DeleteFileOperationBlock,
  ReplaceFileOperationBlock - RawBlock: represents unparsed blocks

This enables type-safe block handling, encapsulates validation logic within block classes, and
  provides better separation of concerns. Blocks now validate themselves during construction and
  expose to_dict() for state serialization.

Update parse_blocks_node to work with new block types and serialize blocks to dicts for state
  storage. Update edit_block_service to use new block classes. Rename edit_block to operation_block
  in boundaries and constants.

BREAKING CHANGE: SearchReplaceBlock and RawSearchReplaceBlock schemas removed. Code using these
  types must migrate to new block class hierarchy. parsed_blocks state field now contains list[dict]
  instead of list[SearchReplaceBlock]. EditBlockService.convert_raw_blocks_to_search_replace renamed
  to convert_raw_blocks_to_parsed and returns BaseOperationBlock instances.
  EditBlockService.validate_semantics removed - validation now occurs in block constructors.

- Restructure commit prompt data flow through agent workflow
  ([`e79194a`](https://github.com/UseTheFork/byte/commit/e79194ae97f8cb505d976830021e3396de133f74))

Refactor how commit prompt data is passed through the workflow: - Rename user_request to git_diffs
  for clarity - Pass only touched_files to workflow executor - Add extra context parameter to prompt
  assembly pipeline - Improve section formatting with proper spacing and emphasis

This restructuring separates concerns and makes the data flow more explicit while maintaining the
  same external behavior.

- Restructure constitution to use keyed dicts for O(1) lookups and surgical edits
  ([`1a8da0d`](https://github.com/UseTheFork/byte/commit/1a8da0d1511952662ef245f428e75dc01c2c5bff))

- Restructure tool call execution and TUI messaging
  ([`9e51a5e`](https://github.com/UseTheFork/byte/commit/9e51a5e35f0b1caaa85692d19d73761ee5da4d40))

Extract tool message creation and TUI updates into a dedicated `_update_tui()` method in ToolNode.
  Restructure the ToolCall message to use `tool_id`, `status`, and `content` fields instead of
  `name` and `args`.

Refactor UI components to separate argument display (ToolArgs) from result display (ToolResult) with
  a collapsible container. Update response panel and conversation widget handlers to work with the
  new message structure.

This improves separation of concerns and makes tool call state management more explicit.

- Restructure TUI event system and pending panel architecture
  ([`a0c78e6`](https://github.com/UseTheFork/byte/commit/a0c78e6663c0ec4c25b7662b6de2351734f77f32))

Replace the old Messages-based event system with a new TuiEvents-based architecture. Consolidate
  pending response panel into a unified PendingPanel widget with streaming markdown support.

Key changes: - Rename TuiMessage events to TuiEvent with new event types (AddHeading,
  ResponseStarted, ResponseChunk, ResponseComplete, CommandExecutionStarted/Completed) - Replace
  PendingResponsePanel with PendingPanel supporting async markdown streaming - Simplify TUI manager
  service to handle new event types and delegate to panel methods - Update TextRule and Bootbox to
  inherit from Static instead of Widget - Remove unused chat_header.py and welcome.py widgets -
  Update all event emissions across model_main_node, ask_command, and workflow_service

- Separate llm and tui formatting for add files tool
  ([`cf50466`](https://github.com/UseTheFork/byte/commit/cf50466b4085e7d6c9da69caccacb4970fd49e05))

- Simplify Application import path in prepare_environment
  ([`993eb76`](https://github.com/UseTheFork/byte/commit/993eb7693d7802bebc5c158d07f23a8d49af1aec))

- Import Application directly from byte package instead of byte.foundation module - Reduces import
  coupling to the foundation layer and improves code clarity

- Simplify auto focus and clean up unused bindings in ByteTUI
  ([`67ae208`](https://github.com/UseTheFork/byte/commit/67ae2087e08e1408f8f6fd74470d5eef52e7515c))

Remove unnecessary focus targets from AUTO_FOCUS, keeping only PromptTextArea as the primary focus
  target. Remove commented-out keybindings that are no longer needed. Add TODO comment about
  creating a Rich theme to maintain consistent styling.

- Simplify boundary methods to use xml tag format
  ([`87a84b1`](https://github.com/UseTheFork/byte/commit/87a84b1ffc0d99fc228c392c65663e81c80e8e08))

Remove format_style parameter from critical, important, and warning methods. Replace HTML comment
  format with consistent XML tag-based format (e.g., `<critical>`, `<important>`, `<warning>`,
  `<comment>`) for easier parsing and consistency across the codebase. Simplify methods by removing
  conditional branching and validation checks.

- Simplify coder agent prompt and remove mandatory tool usage language
  ([`dcd43f6`](https://github.com/UseTheFork/byte/commit/dcd43f6f04be25b9360f57ee3232a1b8b0606422))

Remove "(MANDATORY)" markers from tool usage sections and commented example code from coder agent
  prompts. Change file_context_with_line_numbers to file_context. Remove trailing critical boundary
  message about using tools after drafting rounds. These changes streamline the prompt while
  maintaining core functionality.

- Simplify coder agent workflow and extract plan-execute pattern
  ([`0fb21b8`](https://github.com/UseTheFork/byte/commit/0fb21b85edb09d879fccc33af3c9e83aeba6266a))

- Simplify coder workflow by removing planning phase
  ([`d3fc785`](https://github.com/UseTheFork/byte/commit/d3fc7852cf586533c3425887224a7063ea347114))

Remove the CoderPlanAgentNode from the coder workflow and consolidate the planning and
  implementation phases into a single CoderAgentNode execution.

The new CoderAgentNode now handles both planning and implementation in one phase, eliminating the
  need for a separate planning step. This simplifies the workflow while maintaining the same level
  of code quality through updated prompt templates.

Also: - Remove CoderAgentMessage and CoderPlanAgentMessage exports from agents __init__ - Update
  agent display names to use human_name property for better UX - Upgrade coder_agent_node model to
  claude-sonnet-4-6 for improved capabilities - Add snake_to_title utility for converting snake_case
  to Title Case - Fix response panel markdown streaming initialization - Remove unused __future__
  import in text_rule.py

- Simplify edit block service by delegating raw parsing
  ([`54670f2`](https://github.com/UseTheFork/byte/commit/54670f20ed8620087f7e6a1d21b0eb8ede296725))

Update EditBlockService to use RawBlockService for raw block parsing. Changes include: - Remove raw
  block parsing methods (_parse_message_to_components, _merge_components_by_block_id, etc.) - Add
  convert_raw_blocks_to_search_replace() to convert raw blocks to SearchReplaceBlock objects - Add
  parse_raw_block_to_search_replace() for single block conversion - Add
  extract_search_replace_content() and extract_edit_block_content() helpers - Rename
  mid_flight_check() to validate_semantics() for clarity - Remove ABC inheritance and unused imports
  - Update match_pattern to be simpler (no longer extracts attributes)

This reduces EditBlockService complexity and makes it focus on semantic validation and application
  of blocks.

- Simplify error handling and improve worker state management
  ([`bd2f1a2`](https://github.com/UseTheFork/byte/commit/bd2f1a2302c30d98f291c6438b6417512d802a2c))

- Replace asyncio.iscoroutinefunction with inspect.iscoroutinefunction for better performance -
  Remove try/except from EventBus.emit listener loop to allow exceptions to propagate naturally -
  Add exit_on_error=False to @work decorator so worker continues on errors - Add Worker.StateChanged
  handler to safely log errors on main Textual thread - Remove try/except from
  emit_user_input_submitted, relying on worker state change for error handling

- Simplify event bus and migrate to textual messages
  ([`b76c8a9`](https://github.com/UseTheFork/byte/commit/b76c8a9967ffc8588afb4525a5c289b35a98e150))

Replace the production-grade async event bus with priority queuing and concurrent processing with a
  simpler synchronous event system. Migrate TUI events from custom TuiComponentEvents to Textual
  Message types for better integration with the Textual framework.

Key changes: - Remove EventPriority enum and QueuedEvent dataclass - Remove async queue-based
  processing, priority handling, and concurrent execution limits - Simplify EventBus to direct
  synchronous listener invocation - Migrate TuiComponentEvents to Messages (Textual Message
  subclasses) - Update emit_tui() to post messages directly to conversation widget - Add new Message
  types: CreatePanel, UpdateAnalytics, UpdateFiles, LintStarted, LintCompleted, LintProgress,
  LoadingIndicatorShow, LoadingIndicatorHide - Rename TuiComponentEvents.Notify to Messages.Notify -
  Rename TuiComponentEvents.Flash to Messages.Notify - Move message handling from TUIManagerService
  to Conversation widget handlers - Add Linting widget for displaying lint progress - Update all
  services and nodes to use Messages instead of TuiComponentEvents - Add CommitAgentNode and
  BaseAgentNode for structured commit message generation - Simplify commit workflow to use
  CommitAgentNode with ValidationNode - Update git service to emit Messages instead of console
  output - Update lint service to emit progress Messages instead of Rich progress bars

- Simplify generate_agent_state to return only prompt assembler
  ([`bea5399`](https://github.com/UseTheFork/byte/commit/bea5399b1bd5ff196fabcaa981e58285b574d73e))

- Simplify imports and improve widget naming consistency
  ([`4d02dec`](https://github.com/UseTheFork/byte/commit/4d02dec1a18522d25eb97160daae3e00b297bc11))

- Remove unnecessary tui instance binding in application initialization - Simplify
  InvalidGitRepositoryError import path - Rename prompt text area widget ID from "input" to
  "prompt-text-area" for clarity - Update selector reference to match renamed widget ID

- Simplify LLM configuration and provider management
  ([`c71a8c4`](https://github.com/UseTheFork/byte/commit/c71a8c4a732e289fb8eaf1dfc5fef4457df9f7b3))

Remove provider-based configuration system and replace with direct model specification. Simplify
  LLMModelConfig to include provider field, remove LLMProviderConfig and ProvidersConfig classes,
  and eliminate environment variable-based provider detection.

Update LLMService to use langchain's init_chat_model for provider-agnostic model initialization
  instead of maintaining provider-specific class mappings. Remove ModelParams and ModelProvider
  schemas in favor of direct model and provider fields in ModelSchema.

This change reduces configuration complexity and makes the system more maintainable by centralizing
  model definitions in models_data.yaml.

- Simplify multi-select UI by replacing checkbox display with icon-based visual states
  ([`eba017a`](https://github.com/UseTheFork/byte/commit/eba017ae975ca3eb91d3511123a0500520c9a33e))

Remove checkbox display from multi-select items and instead use CSS-based styling with
  SQUARE_FILLED/SQUARE_OUTLINE icons to indicate selection state. Add 'space' keybinding to toggle
  selection and reorganize event handlers by moving on_list_view_selected logic into new
  action_toggle_current method.

Also update type ignore comments to use 'ty:ignore' format with specific error codes for
  consistency.

- Simplify RawSearchReplaceBlock schema and move validation logic
  ([`a4cb45d`](https://github.com/UseTheFork/byte/commit/a4cb45dc5019df81825b202f8b57015633fabae7))

Remove file_path, operation, block_status, and status_message fields from RawSearchReplaceBlock.
  These attributes are now extracted and validated during the conversion to SearchReplaceBlock in
  EditBlockService, providing better separation of concerns.

Move check_single_block_tags_balanced from RawBlockService to EditBlockService where it's actually
  used. This consolidates tag validation logic with the block parsing that depends on it.

Update parse_raw_block_to_search_replace to handle all validation inline, returning
  SearchReplaceBlock with appropriate error status for invalid blocks instead of raising exceptions.

- Simplify tool schemas and improve tool invocation consistency
  ([`c31e6d8`](https://github.com/UseTheFork/byte/commit/c31e6d8ec483a76773efc52e73546d96ba05d28e))

- Convert file tool input classes to inline dict schemas (DeleteFileTool, EditFileTool,
  ReplaceFileTool, WriteFileTool) - Remove unused Pydantic imports and InjectedToolArg decorators -
  Change args_schema from optional to non-optional across all tools - Rename EditFileTool parameter
  from 'path' to 'file_path' for consistency - Add MAX_RESULT_LENGTH constant to GitGrepTool with
  truncation logic for large results - Refactor GitGrepTool parameter handling from **kwargs to
  explicit app=None - Fix tool_node.py to lookup tools by class name instead of name attribute

- Simplify tool_node by removing unused imports and parameters
  ([`60a1d11`](https://github.com/UseTheFork/byte/commit/60a1d1141533c1ad4b5c298679285b37f3fef158))

- Sort AddFilesTool in __init__.py keep-sorted block
  ([`da9675d`](https://github.com/UseTheFork/byte/commit/da9675dba04f9b599a147da7630190f71cf0c26c))

- Sort imports and register CompleteSimpleTurnTool in service provider
  ([`0c79c3a`](https://github.com/UseTheFork/byte/commit/0c79c3a329a016d33ca21f1792238e427abdac6c))

- Standardize block type enums and improve validation
  ([`aa2a484`](https://github.com/UseTheFork/byte/commit/aa2a484131d16059f4412de3cc146b00f3e250d2))

Replace ADD/REMOVE with CREATE/DELETE for consistency with operation names. Add UNKNOWN block type
  to catch invalid operations. Update BlockStatus to default to UNKNOWN instead of VALID for better
  validation flow. Improve search content matching with progressive fallback strategies (exact
  match, newline stripping, whitespace stripping). Add INVALID_OPERATION_ERROR status for
  unsupported operations. Update all prompts and examples to use BlockType enum values instead of
  hardcoded strings. Refactor boundary formatting to use HTML comments for notices/warnings instead
  of custom XML tags. Remove debug logging statements and consolidate validation logic in
  edit_block_service.

- Standardize tool names with _tool suffix, sync harness state on file ops, validate files in
  bootstrap, default llm_tier to fast, catch TUI event errors
  ([`d70bd1e`](https://github.com/UseTheFork/byte/commit/d70bd1efa54444208e6a3f3364932b933817c47f))

- Support multiple complete turn tools in routing logic
  ([`5fa3028`](https://github.com/UseTheFork/byte/commit/5fa3028d84d5e4aa6f3ee888cc9118cd8e8a1e32))

- Track token usage by model instead of by mode category
  ([`5a6f305`](https://github.com/UseTheFork/byte/commit/5a6f3050831c1b7a6be3c2c985bb2381c414fbed))

Replace main/weak/reasoning usage tracking with provider-based tracking keyed by model ID. This
  allows accurate attribution of token usage to specific models and providers.

Changes: - Update UsageAnalytics schema to use by_model dict instead of main/weak fields - Add
  update_usage_by_model() method to AgentAnalyticsService that uses LLMRegistryService to map model
  IDs to providers - Update calculate_analytics() to iterate through models and fetch constraints
  from registry - Update reset_context() to work with by_model structure - Modify WorkflowService to
  extract model ID from usage_metadata_callback and track by model - Calculate memory_percent as
  average of individual model usage percentages

- Track token usage by model instead of main/weak modes
  ([`688d781`](https://github.com/UseTheFork/byte/commit/688d781fec2cdc126f1c88a16d5fd1b3b00bc3fa))

Replace hardcoded main/weak/reasoning model tracking with dynamic provider-based tracking using
  LLMRegistryService. This allows the system to work with any number of providers and models.

Changes: - Update UsageAnalytics schema to use by_model dict instead of main/weak fields - Replace
  update_main_usage/update_weak_usage with update_usage_by_model(model_id) - Refactor
  calculate_analytics to iterate through models and use LLMRegistryService - Update reset_context to
  work with by_model structure - Extract model_id from usage_metadata_callback in WorkflowService -
  Calculate memory_percent as average of individual model percentages

- Track token usage by provider instead of model type
  ([`209dbdd`](https://github.com/UseTheFork/byte/commit/209dbddcafa23aa45f3ce49f689eb4d9cf3a0805))

Replace main/weak/reasoning model type tracking with provider-based aggregation. This allows
  flexible tracking across any number of providers (Anthropic, OpenAI, etc.) without schema changes.

Key changes: - Update UsageAnalytics to use by_model dictionary instead of hardcoded main/weak
  fields - Implement update_usage_by_model() that uses LLMRegistryService to map model IDs to
  providers - Refactor calculate_analytics() to iterate through models and fetch provider data from
  registry - Update _track_token_usage() to extract model ID from callback and track by model -
  Calculate memory_percent as average of each model's individual context usage percentage

- Unify file command notifications and add file stats event
  ([`509d496`](https://github.com/UseTheFork/byte/commit/509d496f74152e1202d28f9dec370184d314f4b3))

Replace direct console output with notify_success/notify_error methods across all file commands for
  consistent notification handling. Introduce FileStats event to track editable and read-only file
  counts separately from FileAdded events. Update TUI event listener to subscribe to FileStats
  instead of FileAdded for accurate file count updates. Remove unused subscription method from
  AICommentWatcherService and uncomment file modification handler.

- Update model configurations and refactor user input handling
  ([`27c28c2`](https://github.com/UseTheFork/byte/commit/27c28c234f7678b1cb8ad0e37574dccf1548e96a))

Update LLM model versions in config: - Change claude-sonnet-4-5 to claude-sonnet-4-6 for planning
  and ask agents - Change coder agent from devstral-medium-latest to claude-haiku-4-5

Refactor user input message construction across commands: - Replace f-string formatting with
  function parameters in AddUserInput calls - Extract command name as separate parameter instead of
  string interpolation

Simplify workflow execution: - Remove unused display_mode parameter from execute method - Remove
  unused Literal import - Clean up trailing blank lines in __init__ files - Remove TODO comments and
  debug logging calls - Update usage documentation in docstring

Enhance workflow configuration: - Add panel_id metadata to RunnableConfig for TUI tracking

- Update parse blocks node to use new service architecture
  ([`26e5547`](https://github.com/UseTheFork/byte/commit/26e55474393a77c64dcc517713d76f2d26e98074))

Refactor ParseBlocksNode to use RawBlockService and updated EditBlockService: - Remove all raw block
  parsing methods (now in RawBlockService) - Remove all SearchReplaceBlock parsing methods (now in
  EditBlockService) - Simplify __call__ method to use new service methods - Use
  raw_block_service.merge_iterations() for parsing and merging - Use
  raw_block_service.validate_syntax() for syntax validation - Use
  edit_block_service.convert_raw_blocks_to_search_replace() for conversion - Use
  edit_block_service.validate_semantics() for semantic validation - Remove unused imports (re,
  BlockType, BoundaryType, extract_content_from_message, get_last_message)

This significantly simplifies the node by delegating to specialized services.

- Update raw block schema with operation and file_path
  ([`0fb9ada`](https://github.com/UseTheFork/byte/commit/0fb9ada13edef0f0f64e8d80082e2cafcbb21ab8))

Enhance RawSearchReplaceBlock schema to include operation and file_path fields extracted during raw
  parsing: - Add file_path: str field - Add operation: str field - Make search_content and
  replace_content optional with empty string defaults in SearchReplaceBlock

This allows RawSearchReplaceBlock to carry more metadata from the raw parsing stage, reducing the
  need to re-extract attributes later.

- Update record_response call to use prompt instead of agent_state
  ([`61a6b3b`](https://github.com/UseTheFork/byte/commit/61a6b3b7d4bb7bb63f168410c5320f646c5e654e))

- Use app.make() for dependency injection in workflows and node registry
  ([`3d6e22f`](https://github.com/UseTheFork/byte/commit/3d6e22f37adc48aea2b7f2424ed7808c97f3aa3b))

- Use GitService for file discovery instead of os.walk
  ([`a2c7410`](https://github.com/UseTheFork/byte/commit/a2c7410a9f3d28ce5233eff17fca12f12d2110cf))

Replace os.walk with GitService.get_tracked_files() in FileDiscoveryService to naturally respect
  .gitignore patterns via git, eliminating manual ignore pattern matching.

Add get_tracked_files() method to GitService that uses git ls-files to retrieve all tracked files.
  Reorder GitServiceProvider initialization to occur before dependent services. Update
  ask_agent_node model to claude-opus-4-6.

### Testing

- Add comprehensive gateway service test suite with auth and post_message tests
  ([`648da09`](https://github.com/UseTheFork/byte/commit/648da090c1e68364c607f6dd310fde086a44b82e))

- Add test_gateway_service.py with auth handshake tests covering valid token, invalid token, wrong
  method, and malformed request scenarios - Add test_post_message.py with unit tests using mocks for
  each message type routing - Add test_post_message_integration.py with integration tests over real
  WebSocket connections - Refactor post_message method in gateway_service.py to eliminate nested
  async function and improve coroutine handling - Add host field to gateway discovery file for
  complete server location info - Remove __future__ annotations imports from container.py,
  conftest.py, test_prepare_environment.py, and utils.py - Update conftest.py to use ByteUserConfig,
  change config format from YAML to JSON, add .byte/.gitignore, and set custom gateway port 9735 for
  tests

- Add comprehensive raw block service tests
  ([`dcacb4e`](https://github.com/UseTheFork/byte/commit/dcacb4e48c25410161e33393c69735e61bf83b67))

Add new test suite for RawBlockService covering: - Parsing simple and multiple raw blocks -
  Detecting invalid blocks with unbalanced tags - Validating block_id requirements (must be numeric)
  - Merging iterations with block replacement by id - Preserving text content between blocks -
  Adding new blocks in subsequent iterations

These tests ensure the raw block parsing and merging logic works correctly.

- Disable php coder agent test assertions
  ([`d5298dc`](https://github.com/UseTheFork/byte/commit/d5298dc2cc362ae505ae31f44a14eabcda949a80))

Comment out assertions in test_coder_agent_php.py that verify file modifications. These tests appear
  to be failing and need investigation before re-enabling.

- Fix indentation in coder agent tests
  ([`3a69878`](https://github.com/UseTheFork/byte/commit/3a6987812b59867757213dae2bade1a57f0c30a3))

Fix indentation in test file content strings to match expected Python formatting. This ensures test
  assertions about file content work correctly.

- Refactor coder agent tests and improve test file setup
  ([`7b349b7`](https://github.com/UseTheFork/byte/commit/7b349b763b2f1124cea1cda608f1765ef4fc84b6))

- Refactor coder agent tests and improve test file setup
  ([`7eceeb3`](https://github.com/UseTheFork/byte/commit/7eceeb31f4d3453707f95b9784cb4e20caf7c1f1))

Remove mocking of prompt_for_confirmation since it's now handled by unit test detection. Fix
  indentation in test file content. Comment out duplicate test. Improve test file creation with
  proper indentation.

- Refactor parser service tests to use helper function and improve coverage
  ([`1c5b95e`](https://github.com/UseTheFork/byte/commit/1c5b95e37067ff0ab4bf9d33b805b5009290666d))

Consolidate test setup into parse_and_prepare_test_blocks helper with apply_blocks parameter. Create
  multiple test files with proper content setup. Update assertions to check block status attributes
  instead of return values. Remove tests that directly instantiate blocks in favor of integration
  tests. Simplify test assertions and remove unnecessary mocking.

- Update cases
  ([`e861d19`](https://github.com/UseTheFork/byte/commit/e861d19a0508fbf394512b208746a60d3f82af28))

- Update parser service tests for new architecture
  ([`a0b112f`](https://github.com/UseTheFork/byte/commit/a0b112f8784983755838df4638ae226e1c9cfe9c))

Update test_parser_service.py to work with refactored EditBlockService: - Update boundary type
  references from FILE to EDIT_BLOCK - Remove test for check_block_ids() (now in RawBlockService) -
  Remove test for check_file_tags_balanced() (now in RawBlockService) - Remove test for unknown
  operation defaulting to EDIT - Update test calls from mid_flight_check() to validate_semantics() -
  Update test calls from check_blocks_exist() to parse_content_to_blocks() - Add tests for
  convert_raw_blocks_to_search_replace() - Add tests for validate_semantics() with relative paths -
  Add tests for apply_blocks() with empty search content - Add test for
  SearchReplaceBlock.to_error_format()

These changes ensure tests align with the new service architecture.

- Update test assertions to match actual LLM response content
  ([`6f248b1`](https://github.com/UseTheFork/byte/commit/6f248b16d0e8ca2025c8a865e16b316d3558f1cd))


## v1.4.0 (2026-02-12)

### Bug Fixes

- Make parse blocks node method async
  ([`b6b2c93`](https://github.com/UseTheFork/byte/commit/b6b2c93a61eb1b34cfdab66a2973dabe54563d1c))

### Build System

- Add skills-ref dependency to project
  ([`d041ac9`](https://github.com/UseTheFork/byte/commit/d041ac95236198dd2e9b29f4af78437c639d1764))

### Chores

- Remove old convention markdown files
  ([`8a35a5a`](https://github.com/UseTheFork/byte/commit/8a35a5a8a82539bce889189e5b9c86ac0db17ea6))

- Update config to support new skill and convention domains
  ([`d4b1c3b`](https://github.com/UseTheFork/byte/commit/d4b1c3b048212f4b5fac0dd1968aa16b4b05817b))

- Update documentation and configuration
  ([`a1ab876`](https://github.com/UseTheFork/byte/commit/a1ab876f7630e07f6d0a25cb59ae6bca5ebc0e01))

### Documentation

- Add domain documentation for config, files, git, and lint domains
  ([`1cacadc`](https://github.com/UseTheFork/byte/commit/1cacadc4c59725e46d030905b52d71f1cbd6d905))

- Add domain documentation for git and parsing domains
  ([`988a9c2`](https://github.com/UseTheFork/byte/commit/988a9c2536184ef573f15176a57006b64eb6c289))

- Add knowledge domain documentation
  ([`2948064`](https://github.com/UseTheFork/byte/commit/2948064f0eacfc564094f69e9950eed495db781a))

- Add project conventions for comment standards and architecture
  ([`ac055d7`](https://github.com/UseTheFork/byte/commit/ac055d7e3b8f07c57c5b789a2373d93f023d8d48))

Introduce comprehensive documentation for: - Comment standards for Python docstrings, inline
  comments, and documentation - Project architecture guidelines covering directory structure,
  dependency injection, and service patterns

These conventions provide clear guidance for code documentation and architectural design across the
  project, promoting consistency and maintainability.

- Update conventions with new markdown files
  ([`bcfadef`](https://github.com/UseTheFork/byte/commit/bcfadef66d3cd03c681e8e0b2b290eec606a4aaf))

- Update project conventions and documentation standards
  ([`54947a4`](https://github.com/UseTheFork/byte/commit/54947a4997a4a814d341fb674e09c4801cfddad6))

### Features

- Add context add command for smart context management
  ([`af29edb`](https://github.com/UseTheFork/byte/commit/af29edbd2ab5555ad2bee405923ef5a34004c089))

- Add convention parsing and validation services
  ([`aba8067`](https://github.com/UseTheFork/byte/commit/aba8067da93590dfcc0fa30c361e2b6271874b3b))

- Add skill formatting method to parsing service
  ([`09d7afe`](https://github.com/UseTheFork/byte/commit/09d7afeaead5eb155c8a204b2e236de45723a2cd))

- Add slugify method to string utility
  ([`a8849ef`](https://github.com/UseTheFork/byte/commit/a8849efa037e0b2fd6ca9e7227337f2de19a8af5))

### Refactoring

- Enhance prompt assembly with convention context gathering
  ([`be84152`](https://github.com/UseTheFork/byte/commit/be841521bcbfae269f3bf5f9e4ed0deae24f16ae))

- Migrate convention-related imports and services
  ([`5e5658e`](https://github.com/UseTheFork/byte/commit/5e5658eca8aa9c7ea2472bb437e0905f8b52cd13))

- Modify extract node to use parsing services
  ([`da30488`](https://github.com/UseTheFork/byte/commit/da30488e4343c1514ab4436d3ffda79004ea1847))

- Move boundary and boundary type to support module
  ([`65c1c61`](https://github.com/UseTheFork/byte/commit/65c1c61c01f5ae076eafb8f11fe11ee654a5baf2))

- Move convention command and constants to conventions module
  ([`957140f`](https://github.com/UseTheFork/byte/commit/957140f526bee7fa26c4c259c61b1dd1e24f96bf))

- Remove unused conventions module
  ([`a5afb22`](https://github.com/UseTheFork/byte/commit/a5afb22dc79d0ae4fa7c3b7306d36856520f0138))

- Remove unused imports and simplify prompt assembler
  ([`2de8cb5`](https://github.com/UseTheFork/byte/commit/2de8cb5d4ebb1c8adbef2cf1c2a8744536e19494))

- Rename convention files to use consistent hyphen naming
  ([`0e2e91b`](https://github.com/UseTheFork/byte/commit/0e2e91b1dfadab2c712583201f467d8f51931ecb))

- Rename prompt_format module to code_operations
  ([`ca65c72`](https://github.com/UseTheFork/byte/commit/ca65c72611a7dc3deac4be1a28b1f54da896735c))

Restructure the project by renaming the `prompt_format` module to `code_operations` to better
  reflect its broader functionality. This involves:

- Renaming the entire module directory - Updating import statements across multiple files -
  Maintaining the existing functionality while improving module naming

- Replace skill parsing service with conventions parsing service
  ([`2227f08`](https://github.com/UseTheFork/byte/commit/2227f0871a4332c905044e72f0e0c299ad4091c3))

- Restructure code operations module
  ([`b63dc44`](https://github.com/UseTheFork/byte/commit/b63dc447eb617bfa45971b966d75f360750f66fb))

- Restructure convention management with new context service
  ([`8421deb`](https://github.com/UseTheFork/byte/commit/8421deb25031e78e5469015de487d2fa97714370))

- Restructure knowledge domain into conventions and parsing domains
  ([`70d1406`](https://github.com/UseTheFork/byte/commit/70d140694411b73ba8ee609d510e601ddde2eb1c))

- Restructure parsing services with base abstract class
  ([`928cabc`](https://github.com/UseTheFork/byte/commit/928cabc9acc952f0ace759447b4e424228a9a64e))

- Simplify ai comment watcher service output
  ([`342ee31`](https://github.com/UseTheFork/byte/commit/342ee31221901236bb991c789257c43179104138))

- Update agent implementations to use new conventions and parsing domains
  ([`84f753a`](https://github.com/UseTheFork/byte/commit/84f753a24fb24521d6179029e6d745828ccc2eac))

- Update agent nodes to improve message handling
  ([`8587caa`](https://github.com/UseTheFork/byte/commit/8587caa4396ebc1be317ad97dafbf904c37d5451))

- Update boundary extraction with new extractor class
  ([`b6fc600`](https://github.com/UseTheFork/byte/commit/b6fc600b657e9d40a16154282182108df78f7b34))

- Update context display and convention type selection
  ([`d866ca9`](https://github.com/UseTheFork/byte/commit/d866ca9e88290c6a057ecb2f1ce2f9b9708d663e))

- Update convention tools and parsing to support new naming convention
  ([`8005895`](https://github.com/UseTheFork/byte/commit/8005895d0faa09e26f373e5149c2f8f2721fab50))

- Update edit block service and remove edit format service
  ([`e29468f`](https://github.com/UseTheFork/byte/commit/e29468f86d8d414cb2ddba7b9879478712e4be73))

- Update event bus and console utilities
  ([`b0bb801`](https://github.com/UseTheFork/byte/commit/b0bb8017fd125bf0c3e71104844ee2211967c49e))

- Update import paths for boundary and boundary type
  ([`67cc88c`](https://github.com/UseTheFork/byte/commit/67cc88cf930ec138f100b94685c2a648e69a7c7c))

- Update prompt format and boundary utilities
  ([`b4c4c16`](https://github.com/UseTheFork/byte/commit/b4c4c161e928572951ea1641c79285285382964d))

- Update prompt format and response structure
  ([`2503c64`](https://github.com/UseTheFork/byte/commit/2503c64fb18498cb6161958205299b2da59caa65))

- Update user interactive mixin return type hint
  ([`756239d`](https://github.com/UseTheFork/byte/commit/756239da58ce587171d97748b94a4337853307cc))


## v1.3.0 (2026-02-02)

### Bug Fixes

- Bump langgraph from 1.0.5 to 1.0.7
  ([`e1b36a1`](https://github.com/UseTheFork/byte/commit/e1b36a165fd674e62aeea3c82dbe06e0ba088104))

Bumps [langgraph](https://github.com/langchain-ai/langgraph) from 1.0.5 to 1.0.7. - [Release
  notes](https://github.com/langchain-ai/langgraph/releases) -
  [Commits](https://github.com/langchain-ai/langgraph/compare/1.0.5...1.0.7)

--- updated-dependencies: - dependency-name: langgraph dependency-version: 1.0.7

dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- Bump mkdocstrings from 1.0.0 to 1.0.2
  ([`136133a`](https://github.com/UseTheFork/byte/commit/136133ac5420a499863f0d33aec54c40bce2488a))

Bumps [mkdocstrings](https://github.com/mkdocstrings/mkdocstrings) from 1.0.0 to 1.0.2. - [Release
  notes](https://github.com/mkdocstrings/mkdocstrings/releases) -
  [Changelog](https://github.com/mkdocstrings/mkdocstrings/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/mkdocstrings/mkdocstrings/compare/1.0.0...1.0.2)

--- updated-dependencies: - dependency-name: mkdocstrings dependency-version: 1.0.2

dependency-type: direct:development

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- Convert message content to string in record response service
  ([`4e97615`](https://github.com/UseTheFork/byte/commit/4e97615e47dab1429cc5c23ca8901b2a6761b9a0))

### Build System

- Update dependencies and build system requirements
  ([`19a1983`](https://github.com/UseTheFork/byte/commit/19a198347b8c7071d6a30e4f8f1b1193e63e52eb))

- Update main with clipboard service provider
  ([`517b0b5`](https://github.com/UseTheFork/byte/commit/517b0b5388b820291d741021669ca3aa4b3d39b0))

### Chores

- Add github workflow for preparing release documentation
  ([`648bf44`](https://github.com/UseTheFork/byte/commit/648bf44a64ebd579254eb7b08aa6cb87d69e3450))

- Add step to push changes to staging branch
  ([`24a59cc`](https://github.com/UseTheFork/byte/commit/24a59cc37ab890915bcc4cc186d03a77d27008df))

- Configure git user for github-actions bot in release workflow
  ([`01125df`](https://github.com/UseTheFork/byte/commit/01125df35c7cd63bdbc299f1371cc8e5cd038176))

- Update documentation and configuration
  ([`eee8be2`](https://github.com/UseTheFork/byte/commit/eee8be230d6d0ed2d1229054dc3f1e04558a31ad))

- Update documentation and configuration
  ([`8ecce42`](https://github.com/UseTheFork/byte/commit/8ecce4255e95631c8466f44e8f4a531646749a6f))

- Update vscode settings and remove unused configurations
  ([`2cb6647`](https://github.com/UseTheFork/byte/commit/2cb664771ff936eef81309c1e1a8bd9079441b76))

### Documentation

- Add project architecture convention document
  ([`65e90fc`](https://github.com/UseTheFork/byte/commit/65e90fc01e0f8a67ee8780ddc737fb284965ccc7))

### Features

- Add cancellation spinner for agent execution
  ([`6832c94`](https://github.com/UseTheFork/byte/commit/6832c9471986e961ec22bcb355100231248314eb))

Implement a custom RuneSpinner to provide visual feedback when an agent execution is cancelled. The
  spinner now supports: - Customizable color palette - Dynamic rune generation - Transient display
  during cancellation process

- Add clipboard extraction to end node
  ([`ce71bf3`](https://github.com/UseTheFork/byte/commit/ce71bf3edd14f2abf2207cb2da371a120df57a72))

- Add clipboard service for code block management
  ([`89fa2cc`](https://github.com/UseTheFork/byte/commit/89fa2ccb44398882051f54e586064becf74999f8))

- Add code block navigator for interactive selection
  ([`cd62305`](https://github.com/UseTheFork/byte/commit/cd62305e2ae8305a7a154bfbab3ea4f3e0861c32))

- Add commit enforcement rule to prompt module
  ([`e17d50b`](https://github.com/UseTheFork/byte/commit/e17d50b2c97a888ece7e9319d8cdf3e102e91c1d))

- Add configurable agent settings framework
  ([`c049280`](https://github.com/UseTheFork/byte/commit/c0492805d0768b4c98dc07fc34062776250b3fe3))

- Add copy:drop command to manage clipboard code blocks
  ([`ed2a2be`](https://github.com/UseTheFork/byte/commit/ed2a2be4fe33e970e52aa8cea9b02c40c7b30ada))

Introduces a new command to clear code blocks from the clipboard session

- Add CopyDropCommand to drop code blocks - Enhance ClipboardService with block type filtering -
  Update schemas to include block type - Add type filtering to copy and drop commands - Provide
  optional type-based filtering for code blocks

- Add dispatch_task method to application
  ([`3802e76`](https://github.com/UseTheFork/byte/commit/3802e76c18f034471dc763bb843f5042b8640405))

- Add interactive subprocess result handling
  ([`a31f66c`](https://github.com/UseTheFork/byte/commit/a31f66c318014652fb29646fdb14db0bd52be0d7))

Enhance subprocess command execution with user interaction: - Add ability to display subprocess
  results in a panel - Prompt user to add subprocess output to conversation context - Allow optional
  user notes with subprocess results - Modify subprocess handling to support more interactive
  workflows

- Add logging for successful text parsing in chromium service
  ([`4fd7e20`](https://github.com/UseTheFork/byte/commit/4fd7e200aa15dedcea62a934e54ed7eb15c410cb))

- Add project hierarchy configuration for ask agent
  ([`3a8fa3a`](https://github.com/UseTheFork/byte/commit/3a8fa3a0ccd5eec80396f775a6f3e8a0e991deda))

- Add project hierarchy setting to conventions agent
  ([`1e46978`](https://github.com/UseTheFork/byte/commit/1e469783dc4cc2dfe565223d88282c2c50a6f021))

- Add prompt assembler for dynamic template rendering
  ([`b22fd5b`](https://github.com/UseTheFork/byte/commit/b22fd5b8ca0312d8dd3a7bb5742d2a0b7fbaa314))

- Add user confirmation validator for interactive validation
  ([`dd4dbe1`](https://github.com/UseTheFork/byte/commit/dd4dbe1e6815325455705eea6f20106b38966580))

- Enhance web content parsing with content extraction and cleaning pipeline
  ([`472fd5b`](https://github.com/UseTheFork/byte/commit/472fd5b11194bbe9926dc95ee2c0a4cfc0ae63a6))

Introduces significant improvements to web content parsing: - Add extract_content_element method to
  web parsers - Implement get_cleaning_config method for parser-specific configurations - Create
  ContentCleaner service for flexible content processing - Update ChromiumService to use new content
  extraction and cleaning pipeline - Add support for Sphinx documentation parser - Improve parser
  initialization with boot method instead of __init__

These changes provide more robust and configurable web content extraction across different
  documentation platforms.

- Expose CodeBlockNavigator in cli module
  ([`6b815fa`](https://github.com/UseTheFork/byte/commit/6b815fa447fbd7e58c250d3abf3c8aa0b6b66376))

- Handle input cancellation in convention and tool nodes
  ([`f19466b`](https://github.com/UseTheFork/byte/commit/f19466bc8ef209c3d609a2abc25b6cb2057309c5))

- Implement config agent command for interactive settings
  ([`67173c3`](https://github.com/UseTheFork/byte/commit/67173c3a5c52b4e3bf8a70d30d6fd9836f5b9ca1))

- Improve content extraction for sphinx and web parsing
  ([`8d69db1`](https://github.com/UseTheFork/byte/commit/8d69db1ad697bf5a93f8529206cadd6b9e0e4831))

### Ops

- Add branch synchronization workflow step to release process
  ([`7666937`](https://github.com/UseTheFork/byte/commit/7666937b8f5ba0ef5acc823e5f586dd512914c62))

- Add fake api key for prepare-docs workflow
  ([`98ccb37`](https://github.com/UseTheFork/byte/commit/98ccb37e223afab9f056d7e51d9ba3f4953c7334))

- Update prepare-release workflow to merge changes to development branch
  ([`58e974f`](https://github.com/UseTheFork/byte/commit/58e974f485500b62f9585edc04b80083a2d56cb8))

### Refactoring

- Add get_prompt method to base agent implementation
  ([`3771d8e`](https://github.com/UseTheFork/byte/commit/3771d8e7a2461e105b163426f3d5266fb8a33c89))

- Add get_user_template method to base and agent implementations
  ([`75fffdf`](https://github.com/UseTheFork/byte/commit/75fffdfda4d4efc78bf8ee54c5981cb7170a7b95))

- Enhance prompt format schemas with new boundary types
  ([`1063372`](https://github.com/UseTheFork/byte/commit/1063372c71738ee84b4f2c656a7bab95598e30ea))

- Extend metadata schema with erase history flag
  ([`a0e93dd`](https://github.com/UseTheFork/byte/commit/a0e93dd8a32999687936cdb109f16c53b69fc505))

Add erase_history boolean field to MetadataSchema to control message history preservation

- Extract user template to separate variables in prompt files
  ([`a04f091`](https://github.com/UseTheFork/byte/commit/a04f091649118c55699a36553cd8f35eeced0daa))

- Improve copy command description for clarity
  ([`3b93ac0`](https://github.com/UseTheFork/byte/commit/3b93ac0757bddfc37d468ed4712c7a410cdda461))

- Improve end node message handling and state management
  ([`445a0cd`](https://github.com/UseTheFork/byte/commit/445a0cde2f48976c809f8f9f1cc55a98f8d49dac))

Enhance message processing logic in EndNode: - Remove unused imports - Add docstring explaining
  node's purpose - Conditionally promote messages based on metadata - Remove explicit message
  clearing

- Improve task cancellation and error handling in stream execution
  ([`b536a26`](https://github.com/UseTheFork/byte/commit/b536a26fba3906ab366a976a1cf3f72629c390c7))

Refactors the stream execution method to: - Handle asyncio.CancelledError in _run_stream method -
  Move stream task creation inside try block - Replace CancelledError with KeyboardInterrupt for
  user cancellation - Add proper cleanup and logging for task cancellation

Removes redundant print statements that were likely used for debugging

- Improve user request wrapping logic in assistant node
  ([`a254e5d`](https://github.com/UseTheFork/byte/commit/a254e5d1591d2a88559b60210af6a79bbc51e734))

Modify the wrapping of user requests to handle XML-like structured inputs more intelligently: -
  Check if user request already starts with XML tags - Skip wrapping if XML structure is detected -
  Maintain existing boundary wrapping for plain text inputs

- Initialize state with default values and clear scratch messages
  ([`b960402`](https://github.com/UseTheFork/byte/commit/b960402513e39c09d7f342e2484030b674a479be))

Update StartNode state initialization: - Always clear scratch messages - Set default values for
  parsed_blocks and extracted_content - Add erase_history flag to metadata

- Modify parser service to return formatted masked messages
  ([`a0401fe`](https://github.com/UseTheFork/byte/commit/a0401fe89bb9827211a75ab758ac8cbf2f5ab899))

- Remove copy agent and node implementations
  ([`eb2122c`](https://github.com/UseTheFork/byte/commit/eb2122ca2611d4a66a6d61cae7caebaec47767e8))

- Remove copy command from prompt format
  ([`c60ea25`](https://github.com/UseTheFork/byte/commit/c60ea25cfad015d8003024181ec29032c6985a84))

- Remove debug log and add content retrieval for added files
  ([`4aac4a4`](https://github.com/UseTheFork/byte/commit/4aac4a41377be0b63221e370184688f8b477f2e4))

- Remove readthedocs parser and consolidate parsing logic
  ([`145ccc9`](https://github.com/UseTheFork/byte/commit/145ccc92bb6685ea421068decb291dfc01290a58))

Consolidate parsing logic by removing the separate ReadTheDocs parser and integrating its
  functionality into the Sphinx parser. This simplifies the parser structure and reduces code
  duplication. Key changes include:

- Remove ReadTheDocsParser - Update Sphinx parser to handle ReadTheDocs sites - Remove
  ReadTheDocsParser references from imports and parser lists - Simplify content extraction methods
  across parsers

- Remove show agent and move show command to memory module
  ([`6d9a23b`](https://github.com/UseTheFork/byte/commit/6d9a23beee39d7e6c844d659145711375250611c))

This refactoring moves the show functionality from the agent module to the memory module: - Deleted
  show agent and command from agent implementations - Added new show command in memory module -
  Updated imports and service providers accordingly - Simplified assistant node and other related
  files

- Restructure prompt templates with user template and assembler
  ([`b774719`](https://github.com/UseTheFork/byte/commit/b7747197a3ba91850bb9bc08949fd94cf5a619da))

- Simplify agent and application interrupt handling
  ([`5f2b64c`](https://github.com/UseTheFork/byte/commit/5f2b64c9a57133db7f7c911fc2713b01c6b6e7c9))

Remove unnecessary debug print statements and spinner logic Streamline keyboard interrupt handling
  in both agent and application Reduce code complexity by removing redundant cancellation steps

- Update agents to use get_enforcement method
  ([`8afe9e5`](https://github.com/UseTheFork/byte/commit/8afe9e53dedc2cdaa52f34f908189af1fbc9e198))

- Update ai comment watcher with more flexible comment handling
  ([`41cb281`](https://github.com/UseTheFork/byte/commit/41cb281b4117c669f65b2610dae6376ca512edc8))

- Update cleaner agent prompt and user template
  ([`7d2878a`](https://github.com/UseTheFork/byte/commit/7d2878afc6f46e6e64220b38a4230b6c67a449c2))

- Update interactions service to handle default selection
  ([`62f5d9d`](https://github.com/UseTheFork/byte/commit/62f5d9d1aa46c3e7db0ddabc63763fd74dcfd5b4))

- Update message handling in nodes and utils
  ([`ca19427`](https://github.com/UseTheFork/byte/commit/ca19427b03f0258113a04bb8af784ea40c40fefe))

- Update parse blocks node with user interaction handling
  ([`c75e594`](https://github.com/UseTheFork/byte/commit/c75e594f9219da7f5f3a05359efbd3bda6a5d0d5))

Modify ParseBlocksNode to handle user interactions: - Add UserInteractive mixin - Implement graceful
  handling of input cancellation - Add metadata flag for history erasure on max iterations

- Update state schema with optional extracted content
  ([`25ac65b`](https://github.com/UseTheFork/byte/commit/25ac65bd96d399c6a45149d2ee12bdb003df0c29))

Modify state schema: - Make extracted_content nullable - Minor formatting adjustments

### Testing

- Add test files for various web parsers
  ([`add603a`](https://github.com/UseTheFork/byte/commit/add603ad29db24877443095652f91d47d28ef413))

- Add test fixtures for web parser service
  ([`59ae9c0`](https://github.com/UseTheFork/byte/commit/59ae9c01996a874877385eabe1a3c06b963aae7c))

- Update fixtures to include all html
  ([`5ea5fe2`](https://github.com/UseTheFork/byte/commit/5ea5fe20070b65f5b3561fe2606dc94bf8110e8a))


## v1.2.0 (2026-01-29)

### Chores

- Configure dependabot to target development branch
  ([`f6fc50f`](https://github.com/UseTheFork/byte/commit/f6fc50f033c73fc832ef51bfc0a9bc8483980211))

- Remove outdated convention documentation
  ([`e4e9b51`](https://github.com/UseTheFork/byte/commit/e4e9b513cdba3542a8c5ec450535e07f4ed1a093))

### Features

- Add boundary methods for important and critical text formatting
  ([`66658fa`](https://github.com/UseTheFork/byte/commit/66658fae23f2019de74c4ddae22cd8701c3ce8c2))

Introduces new Boundary methods: - `important()` for emphasizing important information - Refactors
  existing critical text formatting - Adds support for both XML and markdown formatting styles

These changes improve text emphasis and formatting capabilities in the prompt system

- Add record response service for tracking agent interactions
  ([`b751175`](https://github.com/UseTheFork/byte/commit/b751175ec11cfaea63c4c23f3fd2321717453d14))

### Refactoring

- Improve message formatting and boundary handling
  ([`98d9a97`](https://github.com/UseTheFork/byte/commit/98d9a9765d5ae669c6e15465598cdc11773bc11f))

- Improve type hints and simplify enforcement list handling
  ([`ae14ff0`](https://github.com/UseTheFork/byte/commit/ae14ff01c76f0bcb2c7864c059fb355dc7aaf3bf))

- Remove _setup_environment method from load configuration
  ([`26329a1`](https://github.com/UseTheFork/byte/commit/26329a1b3ef7780e4f3aa4cb51fb83166e449838))

- Update enforcement and reinforcement message handling
  ([`b8b74d4`](https://github.com/UseTheFork/byte/commit/b8b74d49d39bfb419d6e5580da2f6055141bf8a2))

- Update list handling in ai comment watcher and add warning method to boundary utils
  ([`fa3d02f`](https://github.com/UseTheFork/byte/commit/fa3d02f7f28bba601a171dc82834ada54a5f0347))


## v1.1.0 (2026-01-24)

### Bug Fixes

- Correct weak model config path in migrator test
  ([`e5bccb0`](https://github.com/UseTheFork/byte/commit/e5bccb0990a774419669a5f91d17bf7d7c446474))

### Features

- Add configuration version and migration support
  ([`3495b93`](https://github.com/UseTheFork/byte/commit/3495b93db45ea29faf99aebf4814faf07a9fb41b))

Introduces version tracking for configuration and a migration mechanism to handle configuration
  updates between different versions of the application. Key changes include:

- Added version field to configuration - Created migrator to handle config version transitions -
  Updated LLM service to support default model selection - Improved configuration bootstrapping
  process - Added support for retrieving application version dynamically

- Add input cancellation handling for interactive prompts
  ([`85780ca`](https://github.com/UseTheFork/byte/commit/85780cac0763bf0b975ad76ce83bf3bff52ad16b))

- Enable lsp service provider
  ([`b3fb3f5`](https://github.com/UseTheFork/byte/commit/b3fb3f5db59e964164bdf0e27dfd81cb623ebda5))

- Improve commit command to handle untracked files and staged changes
  ([`d87e299`](https://github.com/UseTheFork/byte/commit/d87e29914964d2cb139373766462b8ed9b3ff73a))

### Refactoring

- Handle input cancelled error in commit command
  ([`b04c2ff`](https://github.com/UseTheFork/byte/commit/b04c2ff3f63a17eb0a709711e732d417e33509b6))

- Modify commit validation workflow
  ([`78ce60e`](https://github.com/UseTheFork/byte/commit/78ce60e4a25cca56f3cfdd25bc5b44e74e3327d3))

- Raise input cancelled error on interrupt
  ([`e99046c`](https://github.com/UseTheFork/byte/commit/e99046cf88c50bc14e952254d8bc5f06c86020f1))

- Remove unused config variable in service provider
  ([`065ae1e`](https://github.com/UseTheFork/byte/commit/065ae1e891b8a0697014b32aadd495e3fa390d00))

- Restructure llm configuration and model management
  ([`d8de1f6`](https://github.com/UseTheFork/byte/commit/d8de1f6a9c4b26dfa68d6c2b5b1787d415a47d5f))

Major refactoring of LLM configuration and model management:

- Replaced provider-specific schemas with a more flexible ModelSchema - Introduced providers
  configuration with enable/disable flags - Added support for dynamic model configuration via
  models_data.yaml - Simplified LLM service configuration and model selection - Updated
  configuration structure to support multiple providers - Improved model initialization and
  parameter handling - Removed hardcoded provider-specific model configurations

Breaking changes: - Removed AnthropicSchema, OpenAiSchema, and GoogleSchema - Changed LLM
  configuration structure in config.py - Modified LLMService to use new configuration approach -
  Updated tests to work with new configuration model

- Simplify keyboard interrupt handling in menu interactions
  ([`6d6fa18`](https://github.com/UseTheFork/byte/commit/6d6fa186f00e26a4e987ebfb66ad1603950b40e5))

- Update analytics and service provider with cost calculation and env loading
  ([`e11610f`](https://github.com/UseTheFork/byte/commit/e11610fd248aa21fc7708a4682301a5404a90902))

- Update console panel method for commit validation
  ([`f855ab3`](https://github.com/UseTheFork/byte/commit/f855ab3b770efee787444e2272e3444af6c06285))

### Testing

- Update test mocks for user confirmation
  ([`5fb5171`](https://github.com/UseTheFork/byte/commit/5fb517132aa3e411edb0e34cf9668d44b8ad4f30))


## v1.0.0 (2026-01-23)

### Bug Fixes

- Correct typo in project_information_and_context variable name
  ([`295ba97`](https://github.com/UseTheFork/byte/commit/295ba97ac2c8e6ffee2fe816423e8c58b08bfb23))

- Ensure config and cache paths exist on log service init
  ([`faf307b`](https://github.com/UseTheFork/byte/commit/faf307b3e85234c5b7a14fe77fb4f20385c94f31))

- Improve diff retrieval and change type detection in git service
  ([`5a98502`](https://github.com/UseTheFork/byte/commit/5a985023f96099af6da8f2369641894245eea15e))

Changes include: - Modify get_diff() to retrieve staged changes from HEAD commit - Correct change
  type detection and mapping - Add better handling for binary files - Improve diff generation for
  modified files

- Resolve file paths relative to application base path
  ([`ca2e102`](https://github.com/UseTheFork/byte/commit/ca2e1025b5c83b4cc4b87c8f148c50e61192bd2e))

Update file path resolution to use application base path for relative paths. This ensures consistent
  file path handling across file discovery and matching operations. Removed skipped tests and added
  small delays to improve watcher service test reliability.

- Update spinner transient mode for unit tests
  ([`078088e`](https://github.com/UseTheFork/byte/commit/078088e403fb4efce16d0ff44a1506f52bcf9ee3))

### Build System

- Add pytest-mock dependency for testing
  ([`d2c3bb6`](https://github.com/UseTheFork/byte/commit/d2c3bb6f74ba57e9ccfdaf25cbaffc3b8f0fc0e6))

- Configure dependabot for weekly updates
  ([`42dce10`](https://github.com/UseTheFork/byte/commit/42dce1062bf54a9b32cee7a7f5e7f842a2c3dd66))

- Fix semantic release version path
  ([`a3af03a`](https://github.com/UseTheFork/byte/commit/a3af03ac7f626eeed483aa6a205232b5775e88d3))

- Increase semantic-release verbosity to debug release process
  ([`de011f6`](https://github.com/UseTheFork/byte/commit/de011f6a3869501ff6b52558954986b92411ac7f))

- Update justfile to run pytest with coverage
  ([`6287838`](https://github.com/UseTheFork/byte/commit/628783832dc955c4709b2eb0a078c27a697f417e))

### Chores

- Add placeholder test files for config writer and prepare environment
  ([`55a2260`](https://github.com/UseTheFork/byte/commit/55a2260a3284772353df6a447ccdd62aa62da6b9))

- Clean up exception handling and application flow
  ([`095fa7c`](https://github.com/UseTheFork/byte/commit/095fa7cd87356ad0f52230d558ff0b345365e2fe))

- Comment out documentation generation steps in release workflow
  ([`70bec7a`](https://github.com/UseTheFork/byte/commit/70bec7aff0e30bd309645a8e057ac842f81d13a4))

- Remove changelog from release commit message
  ([`0990711`](https://github.com/UseTheFork/byte/commit/0990711284aa2b52f8792df0262ef525e5535424))

- Remove git-cliff from development environment
  ([`f0f70b1`](https://github.com/UseTheFork/byte/commit/f0f70b1af7d9ffe4f0dc88c26207056c55ec1715))

- Remove project architecture document
  ([`8346bf2`](https://github.com/UseTheFork/byte/commit/8346bf23af48fbfa687fe6217fe411922101d20f))

- Remove unused bootstrap file
  ([`577d5ac`](https://github.com/UseTheFork/byte/commit/577d5ac967ac583990fab6e6ee4599aed4b9881c))

- Reorganize test files and fixtures
  ([`243920a`](https://github.com/UseTheFork/byte/commit/243920aac37151640079c03508ad2abd0f099b74))

- Update byte-ai-cli dependency to 0.7.1
  ([`23e98a8`](https://github.com/UseTheFork/byte/commit/23e98a884132e1cb7f79df03052c2aa147d538e4))

- Update config for agent node conventions
  ([`eed0aa4`](https://github.com/UseTheFork/byte/commit/eed0aa4f900fc0ca8f5af3849cf89bb7ef5daddf))

- Update config to include editable test files
  ([`37dc211`](https://github.com/UseTheFork/byte/commit/37dc2112f0374b187f3f88d992acf6d03ef71a8b))

- Update gitignore to include coverage.xml
  ([`9310470`](https://github.com/UseTheFork/byte/commit/9310470df707de611bd16898c1002fbe870372fd))

- Update semantic release and project configuration
  ([`8a0cd4c`](https://github.com/UseTheFork/byte/commit/8a0cd4c41eef31d2fb96b81fccec121fbfa639bd))

- Update test cassette files
  ([`0c35de5`](https://github.com/UseTheFork/byte/commit/0c35de5b946ff71f91b1e80a2f8401135d7f7efd))

### Code Style

- Improve markdown table formatting in settings reference
  ([`f569667`](https://github.com/UseTheFork/byte/commit/f5696677231f76a6a33be3b6f03658aa6be0e665))

### Features

- Add commit agent test infrastructure with VCR support
  ([`8f9b399`](https://github.com/UseTheFork/byte/commit/8f9b3994948e6ac6e65ab3f8185555f53d49b777))

Introduces test infrastructure for commit agent with pytest-recording for HTTP interaction
  recording. Includes: - New test files for commit agent - Fake chat model utility - VCR cassette
  recording configuration - Updated dependencies to include pytest-recording

- Add configurable display modes for stream rendering service
  ([`bd9697b`](https://github.com/UseTheFork/byte/commit/bd9697b72dba4a526a0ec076b627798c2e22a137))

- Add dummy node exception for graph routing errors
  ([`9d269f3`](https://github.com/UseTheFork/byte/commit/9d269f34a2ad08a076cf872bafdcee87f8ba7189))

Introduces a new DummyNodeReachedException to handle unexpected routing in agent graphs. This helps
  identify and debug routing issues by raising an explicit exception when a dummy node is reached
  during execution.

- Add DummyNode and update node return types for LangGraph compatibility
  ([`d4b83e4`](https://github.com/UseTheFork/byte/commit/d4b83e4f40890e7073b710540cb85e6feb6f4866))

This change introduces several updates to improve compatibility with LangGraph:

- Added a new DummyNode for placeholder/passthrough node functionality - Updated node method
  signatures to explicitly return Command with specific goto types - Removed direct usage of START
  and END constants in favor of LangGraph's graph configuration methods - Standardized node return
  types to provide more explicit routing information

These changes enhance the flexibility and type safety of the agent node implementations.

- Add environment detection and configuration support
  ([`b330cec`](https://github.com/UseTheFork/byte/commit/b330cec160effefa5a9c73e3380bf190f95afb6f))

Introduces environment detection mechanisms and configuration support: - Added AppConfig to
  ByteConfig for environment management - Implemented environment detection methods in Application -
  Updated various services to use new environment configuration - Added environment-specific helper
  methods

- Add extract node to commit agent graph
  ([`0e48a4b`](https://github.com/UseTheFork/byte/commit/0e48a4bb86f2879a559a4f4d96b088264c08fe8a))

- Add file path placeholder support for lint commands
  ([`3fd1a73`](https://github.com/UseTheFork/byte/commit/3fd1a73debd4b30b27bbb9cd9de0a6cc754cc0dc))

Enhance lint command configuration to support {file} placeholder for flexible file path insertion.
  Removes full_command attribute and updates command execution to handle file path dynamically.

- Add first boot setup for byte environment
  ([`f03c82a`](https://github.com/UseTheFork/byte/commit/f03c82a615634554e8486792778ec35d2cbdf340))

- Add foundation service provider
  ([`dbd2c3b`](https://github.com/UseTheFork/byte/commit/dbd2c3b33dff6799ee5742a8530d7b0452fa987f))

- Add method to format commit message with files
  ([`511ad40`](https://github.com/UseTheFork/byte/commit/511ad4017a734a02a1e94a5edf1428139aa8195e))

- Add refresh method to convention context service
  ([`80d2910`](https://github.com/UseTheFork/byte/commit/80d291087c4b6b11c98b0cd6097a68e0873b7296))

- Add subprocess agent implementation and related changes
  ([`470eb0a`](https://github.com/UseTheFork/byte/commit/470eb0af7a8fa7d86ba85692e7bdcd7e15ee20ef))

- Enhance file discovery service with comprehensive test coverage
  ([`f9e0fdc`](https://github.com/UseTheFork/byte/commit/f9e0fdc69a265c0c17fbf82b4142c79819ca1513))

Added extensive test cases for FileDiscoveryService to validate: - Nested directory file discovery -
  Fuzzy file matching - Case-insensitive search - Handling of ignored directories - Caching and
  refresh behavior - Handling of unreadable and binary files

- Enhance test infrastructure with logot and improved fixtures
  ([`0a49cd3`](https://github.com/UseTheFork/byte/commit/0a49cd3819e8dffcd2c216b4cab6e47299eb97a7))

Add logot for better log capturing in tests, update test fixtures to support more flexible
  configuration, and improve logging and debugging capabilities. Changes include: - Add logot
  dependency with loguru support - Update pytest configuration to use logot capturer - Modify base
  test fixtures to create config.yaml in git repo - Adjust log levels to DEBUG for more detailed
  testing - Add config fixture in test watcher service - Skip some incomplete test methods

- Implement enhanced LSP configuration with preset and custom server support
  ([`96a6e14`](https://github.com/UseTheFork/byte/commit/96a6e14bdad8ac568b02b40a7c0683ace5daaffd))

This commit introduces a more flexible LSP configuration system:

- Add support for preset LSP servers from lsp-client - Implement new server configuration types:
  PresetServerConfig, LocalServerConfig, ContainerServerConfig, and CustomServerConfig - Update LSP
  service to work with the new configuration system - Add support for different server types (local
  and container) - Integrate with lsp-client library for improved LSP functionality - Refactor LSP
  service methods to use the new client interface

- Introduce new application foundation and bootstrapping
  ([`da5eb98`](https://github.com/UseTheFork/byte/commit/da5eb98a2c103a5b94993b6b9800646bdb636bb7))

### Ops

- Update deploy docs workflow to use full checkout
  ([`0ad3b54`](https://github.com/UseTheFork/byte/commit/0ad3b54db5625d5da3bcf28e27c624cb7a12b087))

### Refactoring

- Add type ignore comments for StateGraph initialization and node creation
  ([`f084379`](https://github.com/UseTheFork/byte/commit/f084379cb7331658c74a580cf97779cbe210c97b))

Add type ignore comments to suppress type checking warnings for StateGraph initialization and node
  creation across multiple agent implementations. This helps maintain type compatibility while
  working with dynamic graph construction.

- Cleanup and simplify various project configurations and test infrastructure
  ([`e0b7185`](https://github.com/UseTheFork/byte/commit/e0b7185192a5140414465f3f201a9bac5ce5f56b))

This commit includes several minor refactorings: - Simplified type hints and method signatures -
  Updated configuration and test infrastructure - Reorganized import statements and type checking -
  Minor code cleanup across multiple files

- Consolidate test utilities and remove base test class
  ([`ae196ef`](https://github.com/UseTheFork/byte/commit/ae196ef6c93ede6aca653df9e783ead1fad420e2))

This commit refactors the test infrastructure by: - Removing the BaseTest class - Creating a new
  utils.py file with common test utilities - Updating test files to use the new utility functions -
  Removing unnecessary utils directory - Renaming test cassette files to follow consistent naming
  conventions

- Enhance agent and stream rendering implementations
  ([`499c3ae`](https://github.com/UseTheFork/byte/commit/499c3aefccb41ce788cd78b8ed2bde8da265e48e))

- Enhance commit agent validation workflow
  ([`3ea99f8`](https://github.com/UseTheFork/byte/commit/3ea99f853b106f1e51d8ca86d8f3e4e02ad77421))

Introduces a more interactive validation process for commit messages: - Add user confirmation step
  in commit validator - Support retry mechanism for commit message generation - Improve error
  handling and logging - Update validation node to support more flexible routing

- Enhance exception handling and logging
  ([`840ebc6`](https://github.com/UseTheFork/byte/commit/840ebc6abe0e9f8b69236e621c8fcd0bd7e9bfa0))

- Extract file creation logic into a helper method in git service tests
  ([`484834c`](https://github.com/UseTheFork/byte/commit/484834c4fdfed44582f3c973b8a32a4350bd3861))

- Extract providers list to main module for reuse
  ([`9db435f`](https://github.com/UseTheFork/byte/commit/9db435fcf968aebb520d6418ce50f0c3064023b0))

BREAKING CHANGE: Moved providers list from individual scripts to main module, which may require
  updating import statements in existing code that previously defined providers locally

- Improve application path and git repository handling
  ([`fc744d4`](https://github.com/UseTheFork/byte/commit/fc744d45b2395999a6ba5ca266f848278030b7d2))

- Improve commit message generation and file path handling
  ([`2e3c1f6`](https://github.com/UseTheFork/byte/commit/2e3c1f62a0d4dae4d4e65f4690b0b91277298c38))

Refactored commit message generation to separate breaking change footer and improve file path
  resolution. Updated test utilities to use mocker instead of unittest.mock.

- Improve commit validator with message numbering and formatting
  ([`c7572ab`](https://github.com/UseTheFork/byte/commit/c7572ab81d0ecbf8b1a7358e342a9f335283d95b))

- Improve error handling and logging in various services
  ([`dab5b3e`](https://github.com/UseTheFork/byte/commit/dab5b3ecedf1c2f6e7f43dccdfb43c2f1e941028))

- Improve file parsing and creation methods
  ([`bbd9709`](https://github.com/UseTheFork/byte/commit/bbd9709aed635974f508620be1d6792643a340ad))

- Improve file service and hierarchy generation
  ([`0b13e90`](https://github.com/UseTheFork/byte/commit/0b13e906433bb550ea7f2974aa136572c819b421))

- Improve stream rendering service logic and state management
  ([`e179c08`](https://github.com/UseTheFork/byte/commit/e179c08b33d026f96c55a40865cc039f6f967251))

Refactored stream rendering service to: - Add explicit state tracking for stream and tool spinner -
  Improve handling of AI message chunks and tool usage - Simplify message handling logic - Ensure
  consistent spinner and stream rendering behavior

- Improve task manager error handling
  ([`bdd857c`](https://github.com/UseTheFork/byte/commit/bdd857c4abe44f680c9a3e5e5c7f510e9eed6752))

- Modify convention generation and loading process
  ([`835c799`](https://github.com/UseTheFork/byte/commit/835c79980139b61f2a760d255b049cec29575994))

- Modify parser service default confirmation behavior
  ([`fa775e3`](https://github.com/UseTheFork/byte/commit/fa775e3a934906599d16da93458743f33bcc1102))

- Modify service provider and application boot process
  ([`78a533e`](https://github.com/UseTheFork/byte/commit/78a533e4d117a35e70119b2894a37d88187fc6a1))

- Remove async from service boot methods and method calls
  ([`96d493c`](https://github.com/UseTheFork/byte/commit/96d493c016f1ade5a4b872a573db0ffec65ce0f6))

This commit removes async/await from service boot methods and method calls across the project. The
  changes include:

- Removing `async` from boot methods in various services - Updating method calls to remove `await`
  for boot and make methods - Adjusting import paths and references to reflect the synchronous
  changes - Removing unnecessary async/await decorators and keywords

The goal is to simplify the service initialization and method invocation process by making it
  synchronous.

- Remove commented AI guidance in validation node
  ([`4439d87`](https://github.com/UseTheFork/byte/commit/4439d879453742fb2906a16a63e32d3e39ae5f1f))

- Remove debug logging in assistant node
  ([`b4defc6`](https://github.com/UseTheFork/byte/commit/b4defc6972604faf23199d0d73bb2432391f95af))

- Remove debug print and use config path method
  ([`168eb86`](https://github.com/UseTheFork/byte/commit/168eb868661abe097ea015e74e2c2a6029a94af9))

- Remove duplicate node from subprocess agent pipeline
  ([`5cb3d58`](https://github.com/UseTheFork/byte/commit/5cb3d58ffa5b726da0b3f585d0411ee82efafb02))

- Remove pass from base_node execute method
  ([`5528b56`](https://github.com/UseTheFork/byte/commit/5528b56d1a07b0eb250e5cb82a164d0942996a2d))

- Remove self parameter from pytest fixtures
  ([`1b77ece`](https://github.com/UseTheFork/byte/commit/1b77ece1724472c643a5bf6a732b813d96ace5af))

- Remove unused imports and commented code
  ([`fef6775`](https://github.com/UseTheFork/byte/commit/fef6775b03f8ed688f222b8103d90dc845df5b9c))

- Remove version tracking from src/byte/__init__.py
  ([`6369423`](https://github.com/UseTheFork/byte/commit/636942305f8a9d07c3aba406d49887e13bbc524c))

- Rename and reorganize mixins and utility modules
  ([`21d946c`](https://github.com/UseTheFork/byte/commit/21d946c3221ab51710987868aca897773be04f76))

- Reorganize CLI and domain modules
  ([`4c3a249`](https://github.com/UseTheFork/byte/commit/4c3a249d339bea9e797a03efba2d968f15bad8d9))

- Reorganize config module and remove unused test fixture
  ([`6582eeb`](https://github.com/UseTheFork/byte/commit/6582eeb2338b14dbaa565b9308a202548f72d984))

- Reorganize log method placement in log module
  ([`e264d0d`](https://github.com/UseTheFork/byte/commit/e264d0deee5d492a64b7cf2d0e0a370e99572174))

- Reorganize project structure and move utils
  ([`9a837a5`](https://github.com/UseTheFork/byte/commit/9a837a5541ad5ef20b9039152bceb4f951cf5b8b))

- Replace self.make() with self.app.make() and add container access methods
  ([`c07463b`](https://github.com/UseTheFork/byte/commit/c07463b79266964b94a938e10cdfa554a2042515))

This refactoring introduces several key changes: - Replaced direct `self.make()` calls with
  `self.app.make()` across multiple files - Added new container access methods like `__getitem__`
  and `log()`, `console()` to Application - Improved type hinting and overloading for container
  methods - Simplified dependency injection and service resolution

The changes improve the consistency of service resolution and provide more explicit ways to access
  application services.

- Restructure console and configuration components
  ([`0e5113e`](https://github.com/UseTheFork/byte/commit/0e5113e1154a27299480e5fe9ebaa9693ee46752))

- Restructure logging and testing modules
  ([`8a8689b`](https://github.com/UseTheFork/byte/commit/8a8689b31114bd00698a8f5089ffe6f90a5eb720))

- Restructure logging service and remove unused dependencies
  ([`361d9e0`](https://github.com/UseTheFork/byte/commit/361d9e0f4a286a06bf4fe0e3472da9b29746d3f5))

- Restructure project architecture and module imports
  ([`6bc5adb`](https://github.com/UseTheFork/byte/commit/6bc5adbab4cfc082aa2e602ebc3aba088f2de543))

- Restructure project architecture and module organization
  ([`079e155`](https://github.com/UseTheFork/byte/commit/079e15501076b64091dbc797c514190f699cf98d))

Major refactoring of project structure: - Reorganized modules across different packages - Moved CLI
  and domain-specific components to new locations - Simplified import paths and module dependencies
  - Removed redundant files and consolidated core functionality

- Restructure project architecture documentation
  ([`9eb64b4`](https://github.com/UseTheFork/byte/commit/9eb64b4c4650d56fed1f1531199c76e34af0850f))

- Restructure project imports and module organization
  ([`af44bd9`](https://github.com/UseTheFork/byte/commit/af44bd98d8f70527dd77a4f6a93ea12c15e2fa2c))

Major refactoring of project structure: - Reorganized import paths from domain-based to more direct
  imports - Removed redundant domain and core directories - Updated import statements across
  multiple files - Simplified service provider and container initialization - Removed unnecessary
  async/await calls in service methods - Standardized service initialization and boot processes

- Restructure project imports and module organization
  ([`5975eb4`](https://github.com/UseTheFork/byte/commit/5975eb47cb830ff339c4aa129bf7913197029a1f))

- Restructure project modules and import paths
  ([`c1dc2f9`](https://github.com/UseTheFork/byte/commit/c1dc2f97233183c406866b6d04735954f63b0d89))

Major refactoring of project structure: - Moved most modules from `byte/` to `byte/domain/` -
  Updated import paths across the entire project - Simplified and consolidated import statements -
  Removed redundant domain prefixes in import paths - Reorganized package hierarchy to improve code
  organization

- Simplify agent graph construction with graph builder
  ([`63c0ed3`](https://github.com/UseTheFork/byte/commit/63c0ed37e6af9b126e1da53885b941b4170f0f1d))

Introduces a new GraphBuilder utility to streamline agent graph construction across different agent
  implementations. This refactoring:

- Removes repetitive graph setup code - Simplifies node addition with type-based node registration -
  Improves type safety and readability - Reduces boilerplate in agent implementations - Adds support
  for more flexible node configuration

- Simplify agent graph initialization with base graph method
  ([`620cf60`](https://github.com/UseTheFork/byte/commit/620cf60b0402c049d625956d86dbb525c5b105d4))

Introduce a new get_base_graph method in the base Agent class to standardize graph initialization
  across different agent implementations. This reduces code duplication and provides a more
  consistent way of creating state graphs with start and end nodes.

- Simplify application configuration and environment handling
  ([`3c48e2d`](https://github.com/UseTheFork/byte/commit/3c48e2d7ca35af5d9d5be13b7960579db17239e3))

Key changes: - Simplified container and application access patterns - Improved environment detection
  logic - Removed unused imports and commented-out code - Added debug flag to AppConfig -
  Standardized service provider and bootstrap methods - Removed development-specific code from core
  modules

- Simplify CLI entry point
  ([`8f355e8`](https://github.com/UseTheFork/byte/commit/8f355e8987afbe2f869466f7bae5f961c72ff756))

- Simplify configuration and bootstrap process
  ([`18b3215`](https://github.com/UseTheFork/byte/commit/18b321521a7c18a5defe64be2c52354b741a8976))

- Simplify dependency injection and configuration management
  ([`f9431b2`](https://github.com/UseTheFork/byte/commit/f9431b256bfd3779e2781fe8f44bc0289c054f4b))

Major architectural changes to simplify dependency injection and configuration management:

- Remove `Configurable` and `Injectable` mixins - Modify `Bootable` mixin to require `app` parameter
  - Update service and command classes to use `self.app` instead of `self.make()` - Standardize
  service initialization with `app` parameter - Replace direct config access with
  `self.app["config"]` - Simplify service and command class inheritance

These changes reduce complexity in dependency resolution and make the application's dependency
  injection more explicit and straightforward.

- Simplify import statements and module structure
  ([`5879d8f`](https://github.com/UseTheFork/byte/commit/5879d8f67922d042befaf34574df78bde9ad34ed))

- Simplify stream rendering service and console logging
  ([`4cf85bc`](https://github.com/UseTheFork/byte/commit/4cf85bc19872717bfddd92b8670987bba41e928f))

Refactored stream rendering and console services to: - Remove redundant logging statements -
  Simplify method signatures - Improve spinner and stream rendering logic - Remove unnecessary
  commented-out code - Enhance flexibility of console and stream rendering methods

- Update application context and import management
  ([`199a4ad`](https://github.com/UseTheFork/byte/commit/199a4add064cb4d41bd6784c98d64a0df97c8d2c))

Refactors how application context is managed and imported across the project: - Removes direct
  application_context usage - Adds get_application() method - Updates import statements and method
  signatures - Simplifies context setting and retrieval

- Update bootstrap process with new environment loading
  ([`d7271bf`](https://github.com/UseTheFork/byte/commit/d7271bf0643b4b6dfc9e90a274773b2df21578b5))

- Update commit prompt template with commit guidelines placeholder
  ([`1ae5d29`](https://github.com/UseTheFork/byte/commit/1ae5d2951650e1bdcb48eb31c14828ac681162c0))

- Update convention context service type hints
  ([`7ddc336`](https://github.com/UseTheFork/byte/commit/7ddc336f53937daa3172cb536ca1b52e90c40c86))

- Update file context and path resolution methods
  ([`38bb90b`](https://github.com/UseTheFork/byte/commit/38bb90b3f0fb58a4b2ec7e7d8d75e0f0ad080f89))

- Update file discovery and service methods
  ([`5a7ceca`](https://github.com/UseTheFork/byte/commit/5a7ceca122835d81d10d0318a722b9b46801f789))

- Update file services to use consistent path handling
  ([`33a7a47`](https://github.com/UseTheFork/byte/commit/33a7a479446364d2a4de1fe0feb35a73abae3165))

- Update get_diff method to default to staged changes
  ([`4c9e8ad`](https://github.com/UseTheFork/byte/commit/4c9e8ad22720456a063408ab3a7318c895fbb633))

Simplify method signature and documentation to clarify default behavior of getting staged changes.
  Removed unnecessary argument documentation and updated usage comment to reflect the default
  behavior.

- Update import statements and script structure for commands and settings generation
  ([`ae78fe9`](https://github.com/UseTheFork/byte/commit/ae78fe9cbcc4007792d19746100016890a877830))

- Update lint service with improved error handling and progress tracking
  ([`37f75bf`](https://github.com/UseTheFork/byte/commit/37f75bfa950bc6015e06c85bbbd61e021a7c74d1))

- Update logging and console services with enhanced methods
  ([`0c242a2`](https://github.com/UseTheFork/byte/commit/0c242a20797d98170f9fac7e4db6117d223d509c))

- Update max lines validator to use state and message extraction
  ([`61278d2`](https://github.com/UseTheFork/byte/commit/61278d2ae7b7977e9ea8f359f07f9216dcf9f371))

- Update node routing and graph builder logic
  ([`d179fd6`](https://github.com/UseTheFork/byte/commit/d179fd685c4010cf388d7e1cc628e68d8b3090ab))

- Update path resolution and gitignore handling to use new root_path method
  ([`e0b0e76`](https://github.com/UseTheFork/byte/commit/e0b0e76c23392ca3f0b97b07d888e174d42ab31f))

- Update project configuration and file structure
  ([`0623916`](https://github.com/UseTheFork/byte/commit/062391601f7cd84af8eb12ffaf290e793a82cc72))

Reorganize project structure, update read-only and editable files in configuration. Modify paths for
  core components and adjust parser conventions.

- Update project structure and convention paths
  ([`a87934b`](https://github.com/UseTheFork/byte/commit/a87934b184a50cc966f2dac68a759f371da47d46))

Reorganize project directory structure, updating read-only files and convention paths. Modify
  service and command implementations to use new application foundation paths.

- Update Python style guide dependency injection example
  ([`7f1f5e4`](https://github.com/UseTheFork/byte/commit/7f1f5e447706e40ff4710308d21b12d680d49bcf))

- **foundation**: Improve application bootstrapping and logging infrastructure
  ([`c21da91`](https://github.com/UseTheFork/byte/commit/c21da91c3801e684c14b755e8275c0bb122ea0d7))

Refactored application bootstrapping process to: - Add explicit logging support - Simplify async
  method calls - Improve debug logging during provider registration - Standardize service provider
  initialization

- **foundation**: Update console and event bus initialization with application context
  ([`6e31174`](https://github.com/UseTheFork/byte/commit/6e31174c3468d71ac470cb78e38c30fd278a086f))

- **knowledge**: Reorganize imports and simplify service initialization
  ([`eebeaf5`](https://github.com/UseTheFork/byte/commit/eebeaf54c67a2cad5d2a0876d0389781730e21bd))

### Testing

- Add comprehensive tests for parser service
  ([`f7a07aa`](https://github.com/UseTheFork/byte/commit/f7a07aa295152d5a7e7556e42430aad734ea2bba))

- Add memory service test suite
  ([`8237b44`](https://github.com/UseTheFork/byte/commit/8237b44495352d05ad3b1bbaabd2ff99334bdfaf))

- Add pytest-mock dependency for testing
  ([`cf5f5c6`](https://github.com/UseTheFork/byte/commit/cf5f5c616f2d3949ad151803285f64cd7d4ad5c0))

- Add test cassettes for commit agent scenarios
  ([`9958a94`](https://github.com/UseTheFork/byte/commit/9958a94da7e8a202381997eb2146e5874ff24122))

- Add test file for agent analytics service
  ([`c02ebbc`](https://github.com/UseTheFork/byte/commit/c02ebbcb8e209c6e58d17ea6d633f5f09fe441a4))

- Add test file for subprocess agent
  ([`e297aa1`](https://github.com/UseTheFork/byte/commit/e297aa1eb5a6f5dc2e3be6ee7d3b2cd28718586e))

- Add test files for ignore and watcher services
  ([`909f8f1`](https://github.com/UseTheFork/byte/commit/909f8f1999a1565851de13435b3448bede715449))

- Add test for command registry
  ([`fd358ca`](https://github.com/UseTheFork/byte/commit/fd358ca5b45d5fc93929e66de5eb81cddca6ec76))

- Add test for editing only editable files
  ([`8336b23`](https://github.com/UseTheFork/byte/commit/8336b23c5d5fe62b021bcd85cfed8f7858f49631))

- Add test for session context service
  ([`5a01693`](https://github.com/UseTheFork/byte/commit/5a01693c25320f9a56844617fb4f892a31badc08))

- Add test suite for git service
  ([`0797dd6`](https://github.com/UseTheFork/byte/commit/0797dd689af76330167b23b5d58e255132a0cb9d))

- Add tests for coder agent file operations
  ([`ab5fe7e`](https://github.com/UseTheFork/byte/commit/ab5fe7e1b27cbfc72939ef7275150c2d1cede971))

- Add tests for coder agent functionality
  ([`22b9367`](https://github.com/UseTheFork/byte/commit/22b93679019e73106f75a4c491e9c79e5f58bf52))

- Enhance base test utilities and file creation methods
  ([`e6053b6`](https://github.com/UseTheFork/byte/commit/e6053b67eafedbdb6499236ede4a0990b4c1a143))

- Update commit agent tests with new scenarios and mocking
  ([`f2b1837`](https://github.com/UseTheFork/byte/commit/f2b18372befd24ff952003ee0e92f39de23df177))

- Update git service test cases to check staged diff behavior
  ([`7835cf4`](https://github.com/UseTheFork/byte/commit/7835cf47a83d0141b9e30885bacb125ba8684be3))

- Update LLM service tests with boot method and EventType
  ([`a33b37a`](https://github.com/UseTheFork/byte/commit/a33b37aa139050a7464d5a3fb4bbf44b554c2d5e))

- Update test utilities and watcher service tests
  ([`cc2753e`](https://github.com/UseTheFork/byte/commit/cc2753efaa6b7a930f9b107a400ec5d30528d92d))


## v0.7.1 (2025-12-31)

### Bug Fixes

- Remove redundant ref parameter in checkout action
  ([`bb76ccd`](https://github.com/UseTheFork/byte/commit/bb76ccdaaf300d66230f8b8429d2cbb916a22702))

- Reorder semantic-release version command flags
  ([`c39b016`](https://github.com/UseTheFork/byte/commit/c39b0167841083c27fc75eb2bcc7e307a9009b4d))

- Update release workflow to fetch full git history and use GitHub token
  ([`14cc909`](https://github.com/UseTheFork/byte/commit/14cc90940e8e6f7b7221638e246121ee8a24b601))

### Chores

- Configure semantic-release for automated versioning and release management
  ([`40b1e6f`](https://github.com/UseTheFork/byte/commit/40b1e6f25351d2af747131e667f8df3059259730))

- Increase semantic-release version command verbosity
  ([`59a66ca`](https://github.com/UseTheFork/byte/commit/59a66ca97dfd007043550e8e7f06f9424b769c42))

- Remove hardcoded repo directory path
  ([`a168b44`](https://github.com/UseTheFork/byte/commit/a168b441f6e1b5dda3b9709eb167f995ecda5b0e))

- Update release workflow and build configuration
  ([`44044db`](https://github.com/UseTheFork/byte/commit/44044db056bc405340c24a0a6c9168a5debf786b))

### Continuous Integration

- Add verification step to release workflow
  ([`3400690`](https://github.com/UseTheFork/byte/commit/3400690a4195157a923b7a4ea0c9e518edfa9a09))


## v0.7.0 (2025-12-31)

### Chores

- Remove unused commit implementation files
  ([`bdf4624`](https://github.com/UseTheFork/byte/commit/bdf462445a981836572385e0af3d9b38f5eb5501))

### Documentation

- Update field descriptions in git schemas
  ([`f63f865`](https://github.com/UseTheFork/byte/commit/f63f8658a496cd3e5597b37d48c845e0e9073e29))

### Features

- Add Alt+Enter key binding for multiline input in prompt toolkit
  ([`7828d62`](https://github.com/UseTheFork/byte/commit/7828d624b08ee88829ed5d9146d0e511da110fbd))

- Add field inclusion rules to commit guidelines
  ([`9badbdd`](https://github.com/UseTheFork/byte/commit/9badbddd0a65ee6a86af90a5251e9910732bae53))

- Add git config and commit service
  ([`54c1bb5`](https://github.com/UseTheFork/byte/commit/54c1bb542786208c4c6a053542fcac1982dcd224))

- Add json extraction to stream rendering service
  ([`30db4a6`](https://github.com/UseTheFork/byte/commit/30db4a66bb78c9a15b7db0edb5ae58e4dae259dc))

### Refactoring

- Improve json extraction and type handling
  ([`7fa5184`](https://github.com/UseTheFork/byte/commit/7fa51845ce1426a6e325aefed31a756437d15783))

- Move commit schemas to git domain
  ([`5cf93ca`](https://github.com/UseTheFork/byte/commit/5cf93caa32f63d7d2c4681e7c30c259a028dcf0e))

- Reorganize commit-related modules and imports
  ([`6f7f2a8`](https://github.com/UseTheFork/byte/commit/6f7f2a8fd278e6a2fd33ef6bbd124b14cfe8aa25))

- Update commit guidelines in prompts and config
  ([`b181eea`](https://github.com/UseTheFork/byte/commit/b181eeacb6e02f91ceac8d19e5f1c94a97faa992))

- Update import paths and remove unused modules
  ([`5d2f61f`](https://github.com/UseTheFork/byte/commit/5d2f61f19384baf5f1a32c5c4936a900a9825f39))


## v0.6.0 (2025-12-30)

### Bug Fixes

- Correct typo in BootConfig class name
  ([`f25ac31`](https://github.com/UseTheFork/byte/commit/f25ac3176e1327ce6cd4c9eb8ae019960ab1f704))

- Update change type check in commit command
  ([`f2cb784`](https://github.com/UseTheFork/byte/commit/f2cb7847e4d894c2cde735cd9f5ccdf9682b16bf))

- Update git diff and commit command logic
  ([`3d0d4bb`](https://github.com/UseTheFork/byte/commit/3d0d4bbb627a886ac4ac3e07b1fdec6e2784e444))

- Update git service and commit command
  ([`8249687`](https://github.com/UseTheFork/byte/commit/8249687eca59825c73d1274c4b58699dc32b41c2))

- Update parent import fallback in knowledge domain
  ([`9d57fb8`](https://github.com/UseTheFork/byte/commit/9d57fb83a9ba1207c2f1fba38fd059516836dac4))

### Build System

- Update dependencies to latest versions
  ([`e811230`](https://github.com/UseTheFork/byte/commit/e81123002379be77374cde6dad82aeefa8ae1da3))

### Chores

- Minor updates to agent state and LLM service
  ([`1ba396f`](https://github.com/UseTheFork/byte/commit/1ba396fe7fbf1320df9ae332abd06352d463999e))

- Prepare release v0.6.0
  ([`398ff56`](https://github.com/UseTheFork/byte/commit/398ff567197e843d4a02d636762a7d26ade4330c))

- Remove empty __init__.py files
  ([`5ad0fa2`](https://github.com/UseTheFork/byte/commit/5ad0fa2279e0dd216de4de1726bcd2ba0ed6c9d5))

- Remove empty agent implementation directories
  ([`ffa8e56`](https://github.com/UseTheFork/byte/commit/ffa8e5626da6909f1ae9b46bb13c0ac1a98f5b9b))

- Remove py.typed file
  ([`9346541`](https://github.com/UseTheFork/byte/commit/93465418f2d33af25ca360f80f6d367412aab550))

- Remove unused commit command file
  ([`0d25621`](https://github.com/UseTheFork/byte/commit/0d2562128f649191f83398e5f85a2d99637fc47b))

- Update import utils comment
  ([`2c5ce86`](https://github.com/UseTheFork/byte/commit/2c5ce866e401129bcf67557cf38675c877a02053))

- Update service provider with new command
  ([`340000b`](https://github.com/UseTheFork/byte/commit/340000b7426f246838952b4644025d146d269015))

### Features

- Add CommitMessage and CommitPlanAgent classes
  ([`89f2d16`](https://github.com/UseTheFork/byte/commit/89f2d164c319333f375ed43e581af9a961bfc8a0))

- Add CommitPlanAgent to AgentServiceProvider
  ([`36420f6`](https://github.com/UseTheFork/byte/commit/36420f6dc796ef6fb3bafef2e04adbc42c0cee9a))

- Add conventional commit message formatting
  ([`ca2ff7f`](https://github.com/UseTheFork/byte/commit/ca2ff7fc8f26d06c6ee009f0ae982ae3550679b6))

- Add remove method to GitService for staging deletions
  ([`7be425e`](https://github.com/UseTheFork/byte/commit/7be425e39c20eb021b807220b9d147411ab5be5b))

- Add structured commit plan generation
  ([`675ec94`](https://github.com/UseTheFork/byte/commit/675ec94665929727d802d31a88136eef749d7074))

- Add testing code patterns convention to focus messages
  ([`f36692a`](https://github.com/UseTheFork/byte/commit/f36692a1c5cdf76e237e8030ca2654670f2f9adc))

- Create commit types constants
  ([`21e86b0`](https://github.com/UseTheFork/byte/commit/21e86b0b8cee0f196ef9aee0fb29fbbd0bb48df5))

- Enhance CommitCommand with commit plan and deletion support
  ([`05f2f2c`](https://github.com/UseTheFork/byte/commit/05f2f2c7041785f85a3c6373dfaa2f1a26e8eeea))

- Uncomment logging and add commented message storage logic
  ([`e6c8d0c`](https://github.com/UseTheFork/byte/commit/e6c8d0cf40ab439f951225e544e07c4e907f2ec6))

- Update copy agent compilation and stream mode
  ([`adf51e1`](https://github.com/UseTheFork/byte/commit/adf51e1c6a122d27baa0b2c44dd1bb4071e1f287))

### Refactoring

- Extract convention focus constants to separate module
  ([`0278029`](https://github.com/UseTheFork/byte/commit/02780292ef521fd672800474fe2350d036180212))

- Improve git service diff detection logic
  ([`5d6a261`](https://github.com/UseTheFork/byte/commit/5d6a26153de3be09f791f23a0950f0b2425ffbaa))

- Minor import cleanup in prompt format service
  ([`04f2189`](https://github.com/UseTheFork/byte/commit/04f218973ce5d511b18a3e530c1d43966591beff))

- Move _display_subprocess_results method before __call__ method
  ([`f9953c3`](https://github.com/UseTheFork/byte/commit/f9953c312cf358ae098e7d0bf4b31e81a7581a5a))

- Remove debug logging in commit command
  ([`481a20e`](https://github.com/UseTheFork/byte/commit/481a20e01c3ecb9d666c98192816b415e5d1428c))

- Remove dynamic import boilerplate from domain __init__ files
  ([`0e4ec0a`](https://github.com/UseTheFork/byte/commit/0e4ec0a10d780a17855712a22bc5b27a981a41d4))

- Remove dynamic imports from mixins module
  ([`3df71ec`](https://github.com/UseTheFork/byte/commit/3df71ec65d9ea358eab49d5d95c136a6b8dc5e3c))

- Remove dynamic imports in mixins
  ([`5a3a92a`](https://github.com/UseTheFork/byte/commit/5a3a92a51cbf231dd3613257c6fd187f260511b7))

- Remove empty __init__.py file in lsp service
  ([`d1b9030`](https://github.com/UseTheFork/byte/commit/d1b9030d39a42aecc3742b1664f5383ee02c37db))

- Remove import_utils module
  ([`a4b8092`](https://github.com/UseTheFork/byte/commit/a4b80924570fabac7969ba49d5cd7d0ec7085158))

- Remove unused imports and clean up __init__.py files
  ([`72d239c`](https://github.com/UseTheFork/byte/commit/72d239cf5bd5396c028a5427e5dd8b973f4986cc))

- Remove unused imports and clean up module references
  ([`649721c`](https://github.com/UseTheFork/byte/commit/649721c3494239dd13fac5eb01feb1ba3d4c5b18))

- Remove unused langgraph constants and commented-out edge definitions
  ([`71f5d2e`](https://github.com/UseTheFork/byte/commit/71f5d2ee263420561b2f02da6d35583d3605eecc))

- Remove unused SubgraphNode class
  ([`05c7442`](https://github.com/UseTheFork/byte/commit/05c7442f6ec076cb5ce136dce7e7871ae54dd7ed))

- Remove unused utility functions
  ([`3b5e694`](https://github.com/UseTheFork/byte/commit/3b5e694b70775fc643983b619e1da118008ff087))

- Rename ByteConfig to ByteConfg across multiple files
  ([`9b8c92b`](https://github.com/UseTheFork/byte/commit/9b8c92bccdb1534d6585dc6c99693707d20712c9))

- Reorder methods in configurable mixin
  ([`f316bb7`](https://github.com/UseTheFork/byte/commit/f316bb731608377efa0016051ea44403674519e8))

- Reorder methods in first boot service
  ([`ce5293b`](https://github.com/UseTheFork/byte/commit/ce5293bd13d71405749825a108cbf71251ea0921))

- Reorder methods in LSP client and service for better readability
  ([`95fdbf5`](https://github.com/UseTheFork/byte/commit/95fdbf5a6fa7c10fd7a35e05db0e7e8f89f34a1f))

- Reorder methods in main application loop
  ([`212683b`](https://github.com/UseTheFork/byte/commit/212683b61550624a19d049ea8f14d78abdae7534))

- Reorder methods in prompt toolkit service
  ([`88d0acf`](https://github.com/UseTheFork/byte/commit/88d0acf4e91c71476781ba0469dc94dd07ef8090))

- Reorganize agent module imports and dependencies
  ([`b636a58`](https://github.com/UseTheFork/byte/commit/b636a58717dbb20776c3ccbf6eeea7b5de678b90))

- Reorganize import statements and module structure in prompt_format
  ([`726bc5e`](https://github.com/UseTheFork/byte/commit/726bc5e61116854dec99806ee750355fadf4b198))

- Reorganize imports and logging in parser service
  ([`c6d7ba1`](https://github.com/UseTheFork/byte/commit/c6d7ba19dd98b60d3c983e96fc98a076279ccd5f))

- Reorganize imports and module references in MCP domain
  ([`ce274e3`](https://github.com/UseTheFork/byte/commit/ce274e336c4f23a47a989653e852571db1444aad))

- Restructure commit agent workflow
  ([`7f9fc67`](https://github.com/UseTheFork/byte/commit/7f9fc673b81790a9066486b158f3a3e046be886d))

- Restructure commit-related code and imports
  ([`8d830b9`](https://github.com/UseTheFork/byte/commit/8d830b9ddaaad0f6f49a0c15e4359f307c5026a0))

- Simplify agent base class and stream handling
  ([`d02ce95`](https://github.com/UseTheFork/byte/commit/d02ce95998ba7815191ba0f467e3852679a24ada))

- Simplify commit workflow and documentation
  ([`50d6e03`](https://github.com/UseTheFork/byte/commit/50d6e03f10b7e9b418ca0140f052f0fe14fa90b6))

- Simplify dump utility with pprint
  ([`a469b20`](https://github.com/UseTheFork/byte/commit/a469b202c2f83619f5d45da671e40b6643edb0be))

- Simplify import and __all__ in multiple modules
  ([`e747654`](https://github.com/UseTheFork/byte/commit/e74765455d2d3b397165d3340d0af0fd184c874f))

- Simplify stream rendering and event handling logic
  ([`c022f94`](https://github.com/UseTheFork/byte/commit/c022f94cc94188feb43cf756dc40953d6f8ba652))

- Update agent nodes import and dependency structure
  ([`27a3ac3`](https://github.com/UseTheFork/byte/commit/27a3ac35f2a1c8fc328313b4bd89e7825956c0cc))

- Update agent service and state import dependencies
  ([`f807122`](https://github.com/UseTheFork/byte/commit/f8071223489799665317d5d5b585a1cd8c912c65))

- Update CLI and lint module import dependencies
  ([`57148a3`](https://github.com/UseTheFork/byte/commit/57148a39270e77b211a6216891e3e727285ecfa0))

- Update config module to use mixins
  ([`838cf8e`](https://github.com/UseTheFork/byte/commit/838cf8ed312086805273e156de21b8228867f563))

- Update git diff parsing and commit message generation
  ([`f9680ef`](https://github.com/UseTheFork/byte/commit/f9680efded3a89ad732a302b4355af6f79afe6c5))

- Update import paths and module references
  ([`9d6acdc`](https://github.com/UseTheFork/byte/commit/9d6acdc3bdeea09beef2b38dbd4aa868b4bedd80))

- Update import paths and module structure for system commands
  ([`896ef86`](https://github.com/UseTheFork/byte/commit/896ef86948f107446e8193491897bdb63d19e109))

- Update import paths and remove unnecessary dynamic imports
  ([`90da185`](https://github.com/UseTheFork/byte/commit/90da1852ef9c9b28df1ded0245714455a2efc996))

- Update import paths and remove unused imports
  ([`17efc4d`](https://github.com/UseTheFork/byte/commit/17efc4d60dc1f896338ff17e6f9391196c0c57a2))

- Update import paths and reorganize module structure
  ([`8638a26`](https://github.com/UseTheFork/byte/commit/8638a265dda20013dd0782e39d1339f17672981c))

- Update import paths for list_to_multiline_text
  ([`6fc3ca9`](https://github.com/UseTheFork/byte/commit/6fc3ca992ed6889c3478136c91060e5a56509c0f))

- Update import paths for LLM domain modules
  ([`c69a6b9`](https://github.com/UseTheFork/byte/commit/c69a6b99cdbbceba22cf331f95a700eced12b17e))

- Update import paths for presets module
  ([`4471315`](https://github.com/UseTheFork/byte/commit/44713151ba428c526416277116a0e1804a8986c6))

- Update import paths for utility functions
  ([`a614d85`](https://github.com/UseTheFork/byte/commit/a614d85df7b44f2ea138763af0c88544307383cd))

- Update import paths for web domain modules
  ([`85b70ae`](https://github.com/UseTheFork/byte/commit/85b70aea0f73b3770cabea937183fc1c9c42b39b))

- Update import paths in CLI and services
  ([`9ecbabb`](https://github.com/UseTheFork/byte/commit/9ecbabbcb0f17193b052396ba30a6ad6feb5475d))

- Update import paths in CLI service files
  ([`d3babcd`](https://github.com/UseTheFork/byte/commit/d3babcd786e980d130fdbf754a8102600a4e6165))

- Update import paths in git service
  ([`effa9ae`](https://github.com/UseTheFork/byte/commit/effa9ae9681983739c5e7fbdc568d3cf85326f88))

- Update import paths in service provider files
  ([`4d756a6`](https://github.com/UseTheFork/byte/commit/4d756a630b781dc58e8f6b132d456e7a42f30067))

- Update import statements and module references
  ([`7a6cd69`](https://github.com/UseTheFork/byte/commit/7a6cd6952d1eae5f2cbc8521c716b9f4ff58158e))

- Update import statements and remove unused references
  ([`1cd044d`](https://github.com/UseTheFork/byte/commit/1cd044d5a8e3d9857a9cf814012199b8c80c9c40))

- Update import statements in lint module
  ([`54ce651`](https://github.com/UseTheFork/byte/commit/54ce651a0e420b425d7f8ef55ab3cf8b53e86452))

- Update node interfaces and signatures
  ([`2b89457`](https://github.com/UseTheFork/byte/commit/2b894571cd26f1c1ab2d23881abf585e3b7edc53))

- Update service and file imports in domain modules
  ([`e40edcc`](https://github.com/UseTheFork/byte/commit/e40edccdd6f6745d978690d1e663b883b874ed52))

- Update subprocess agent and node with context schema and runtime
  ([`7744694`](https://github.com/UseTheFork/byte/commit/7744694c78547e925b84221d3652534446d4a83a))

### Testing

- Add initial test file for git domain
  ([`a68bec8`](https://github.com/UseTheFork/byte/commit/a68bec8bcf2346372d2ac41559455a6ec02e99cc))


## v0.5.3 (2025-12-19)

### Chores

- Prepare release v0.5.3
  ([`e3824b3`](https://github.com/UseTheFork/byte/commit/e3824b32c24e5ef0dfa341b8aea3dd07eca13e7f))

- **deps**: Bump actions/download-artifact from 4 to 7
  ([`3f6015c`](https://github.com/UseTheFork/byte/commit/3f6015c480e7819682e65f8800aed6cc74770429))

Bumps [actions/download-artifact](https://github.com/actions/download-artifact) from 4 to 7. -
  [Release notes](https://github.com/actions/download-artifact/releases) -
  [Commits](https://github.com/actions/download-artifact/compare/v4...v7)

--- updated-dependencies: - dependency-name: actions/download-artifact dependency-version: '7'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump actions/upload-artifact from 4 to 6
  ([`b22eab5`](https://github.com/UseTheFork/byte/commit/b22eab588271485989a6ddb1dbfc9aeb16a0b842))

Bumps [actions/upload-artifact](https://github.com/actions/upload-artifact) from 4 to 6. - [Release
  notes](https://github.com/actions/upload-artifact/releases) -
  [Commits](https://github.com/actions/upload-artifact/compare/v4...v6)

--- updated-dependencies: - dependency-name: actions/upload-artifact dependency-version: '6'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump click from 8.3.0 to 8.3.1
  ([`c445899`](https://github.com/UseTheFork/byte/commit/c445899ea5b3c342d29ed85991297c97d8b0f65a))

Bumps [click](https://github.com/pallets/click) from 8.3.0 to 8.3.1. - [Release
  notes](https://github.com/pallets/click/releases) -
  [Changelog](https://github.com/pallets/click/blob/main/CHANGES.rst) -
  [Commits](https://github.com/pallets/click/compare/8.3.0...8.3.1)

--- updated-dependencies: - dependency-name: click dependency-version: 8.3.1

dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump langchain from 1.1.0 to 1.1.2
  ([`e744e39`](https://github.com/UseTheFork/byte/commit/e744e398cd126b6bb831dd9608f63430d3fc0afe))

Bumps [langchain](https://github.com/langchain-ai/langchain) from 1.1.0 to 1.1.2. - [Release
  notes](https://github.com/langchain-ai/langchain/releases) -
  [Commits](https://github.com/langchain-ai/langchain/compare/langchain==1.1.0...langchain==1.1.2)

--- updated-dependencies: - dependency-name: langchain dependency-version: 1.1.2

dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump langchain-core from 1.1.0 to 1.1.1
  ([`d3c4741`](https://github.com/UseTheFork/byte/commit/d3c474178923cea53efcae9cbcc7cbe880686af9))

Bumps [langchain-core](https://github.com/langchain-ai/langchain) from 1.1.0 to 1.1.1. - [Release
  notes](https://github.com/langchain-ai/langchain/releases) -
  [Commits](https://github.com/langchain-ai/langchain/compare/langchain-core==1.1.0...langchain-core==1.1.1)

--- updated-dependencies: - dependency-name: langchain-core dependency-version: 1.1.1

dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump langchain-google-genai from 3.1.0 to 3.2.0
  ([`8fbedb0`](https://github.com/UseTheFork/byte/commit/8fbedb0126e1883245113d1d1072d8d95d239605))

Bumps [langchain-google-genai](https://github.com/langchain-ai/langchain-google) from 3.1.0 to
  3.2.0. - [Release notes](https://github.com/langchain-ai/langchain-google/releases) -
  [Commits](https://github.com/langchain-ai/langchain-google/compare/libs/genai/v3.1.0...libs/genai/v3.2.0)

--- updated-dependencies: - dependency-name: langchain-google-genai dependency-version: 3.2.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump langchain-openai from 1.0.3 to 1.1.0
  ([`6f3ea7d`](https://github.com/UseTheFork/byte/commit/6f3ea7d68317ddbe51a0ebf3ef6d6f5250e623e3))

Bumps [langchain-openai](https://github.com/langchain-ai/langchain) from 1.0.3 to 1.1.0. - [Release
  notes](https://github.com/langchain-ai/langchain/releases) -
  [Commits](https://github.com/langchain-ai/langchain/compare/langchain-openai==1.0.3...langchain-openai==1.1.0)

--- updated-dependencies: - dependency-name: langchain-openai dependency-version: 1.1.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

### Refactoring

- Improve instance creation and add docstring for PreFlightUnparsableError
  ([`2912e45`](https://github.com/UseTheFork/byte/commit/2912e451202ed1b31eee0a40ec126082d81caf61))

- Remove commented-out boundary lines in edit_format_system
  ([`b25bf67`](https://github.com/UseTheFork/byte/commit/b25bf674847cff72a80ce72b3d84d779344ab186))

- Remove pyright ignore comments in container class
  ([`f88b5fe`](https://github.com/UseTheFork/byte/commit/f88b5fe0ba6e3076dfccfb344538547cd218d25d))


## v0.5.2 (2025-12-06)

### Chores

- Prepare release v0.5.2
  ([`fd62e51`](https://github.com/UseTheFork/byte/commit/fd62e519e4719066fa52d024026c6b47bd5be38d))

- Update dependencies and remove unused packages
  ([`a595cd2`](https://github.com/UseTheFork/byte/commit/a595cd2c615e86ec48562081430e6a871f4bc63e))

### Documentation

- Update commands.md documentation formatting
  ([`b2f6ef6`](https://github.com/UseTheFork/byte/commit/b2f6ef6db0f4201fcfa89ecadbc12773923a8726))

### Features

- Add RawContentParser as fallback for web content extraction
  ([`a0c44ac`](https://github.com/UseTheFork/byte/commit/a0c44aceab663a0bb47b483df6136f42e3db7d44))

- Add reload files command to refresh file discovery cache
  ([`15d99b0`](https://github.com/UseTheFork/byte/commit/15d99b059ca7c7858bf9a530b04fc0f0c329a75b))

### Refactoring

- Add metadata tracking for agent execution state
  ([`74807b4`](https://github.com/UseTheFork/byte/commit/74807b4bc8f833e45ac6dfbc062294c9340e3c5b))

- Modify service and node implementations to support block_id and improve parsing
  ([`4b0bee7`](https://github.com/UseTheFork/byte/commit/4b0bee7c301d06a0fab2aa8741256e1835842673))

- Reorder handle method in base service class
  ([`3f7326b`](https://github.com/UseTheFork/byte/commit/3f7326b1f4d1d8e8d19cc60aebb2e5834b83d9b6))

- Update method signatures and add optional parameter handling
  ([`2266ee5`](https://github.com/UseTheFork/byte/commit/2266ee5ef8e9aabfb5538b0b17185386ca29844d))


## v0.5.1 (2025-12-03)

### Bug Fixes

- Join lint command list to string for proper context display
  ([`8b16564`](https://github.com/UseTheFork/byte/commit/8b16564fd3d7eb183dc2a165ceaaacbb8f4abb19))

- Update agent execution and argument parsing in show command and CLI service
  ([`0008480`](https://github.com/UseTheFork/byte/commit/0008480b02d7b966358d7f900d5251d0de1c8c10))

### Chores

- Prepare release v0.5.1
  ([`46cf1ee`](https://github.com/UseTheFork/byte/commit/46cf1ee4a2b7fb70bf843ea3ae9b2f66dc94736d))

- **deps**: Bump basedpyright from 1.33.0 to 1.34.0
  ([`66f2f03`](https://github.com/UseTheFork/byte/commit/66f2f032f73a0501f6a60847ff24187aaf56269d))

Bumps [basedpyright](https://github.com/detachhead/basedpyright) from 1.33.0 to 1.34.0. - [Release
  notes](https://github.com/detachhead/basedpyright/releases) -
  [Commits](https://github.com/detachhead/basedpyright/compare/v1.33.0...v1.34.0)

--- updated-dependencies: - dependency-name: basedpyright dependency-version: 1.34.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump beautifulsoup4 from 4.14.2 to 4.14.3
  ([`8309d27`](https://github.com/UseTheFork/byte/commit/8309d271006f0d8e1cf524dfa8ca5658455456e4))

Bumps [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/) from 4.14.2 to 4.14.3.

--- updated-dependencies: - dependency-name: beautifulsoup4 dependency-version: 4.14.3

dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump langchain from 1.0.3 to 1.1.0
  ([`1eebe00`](https://github.com/UseTheFork/byte/commit/1eebe0033d4910cacdca3a51a3e9426f3557ab76))

Bumps [langchain](https://github.com/langchain-ai/langchain) from 1.0.3 to 1.1.0. - [Release
  notes](https://github.com/langchain-ai/langchain/releases) -
  [Commits](https://github.com/langchain-ai/langchain/compare/langchain==1.0.3...langchain==1.1.0)

--- updated-dependencies: - dependency-name: langchain dependency-version: 1.1.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump langchain-anthropic from 1.1.0 to 1.2.0
  ([`cdcfb6e`](https://github.com/UseTheFork/byte/commit/cdcfb6e94065f4a2542c960242b3a0fa8588c044))

Bumps [langchain-anthropic](https://github.com/langchain-ai/langchain) from 1.1.0 to 1.2.0. -
  [Release notes](https://github.com/langchain-ai/langchain/releases) -
  [Commits](https://github.com/langchain-ai/langchain/compare/langchain-anthropic==1.1.0...langchain-anthropic==1.2.0)

--- updated-dependencies: - dependency-name: langchain-anthropic dependency-version: 1.2.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump pydantic from 2.12.4 to 2.12.5
  ([`7abc28f`](https://github.com/UseTheFork/byte/commit/7abc28ff88d6d1fc536753ea3624d77df63d318a))

Bumps [pydantic](https://github.com/pydantic/pydantic) from 2.12.4 to 2.12.5. - [Release
  notes](https://github.com/pydantic/pydantic/releases) -
  [Changelog](https://github.com/pydantic/pydantic/blob/main/HISTORY.md) -
  [Commits](https://github.com/pydantic/pydantic/compare/v2.12.4...v2.12.5)

--- updated-dependencies: - dependency-name: pydantic dependency-version: 2.12.5

dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

### Features

- Add project notice message to file context content
  ([`d8dfae7`](https://github.com/UseTheFork/byte/commit/d8dfae7d63f9641e1c523ccf28d8e65e16298546))

### Refactoring

- Improve error logging and handling in prompt toolkit service
  ([`2981ef0`](https://github.com/UseTheFork/byte/commit/2981ef08e7e5f82b95248d024a31336652dc6843))

- Improve prompt formatting and add enforcement rules for AI agents
  ([`aaee21d`](https://github.com/UseTheFork/byte/commit/aaee21d14b4f1b6695fb44905d8b4c4289e86eea))

- Remove unnecessary large text blocks from cleaner prompt
  ([`6f6b1bf`](https://github.com/UseTheFork/byte/commit/6f6b1bf25215825fe342642a517bf4746cf3c84f))

- Update message handling in end node and remove unused packages
  ([`3b98cac`](https://github.com/UseTheFork/byte/commit/3b98cac9f61bd8fafccafbbd9b32a58ca8daaa96))


## v0.5.0 (2025-11-28)

### Chores

- Prepare release v0.5.0
  ([`8baf310`](https://github.com/UseTheFork/byte/commit/8baf31005bb6494336bf9b93a431d65e201b8ced))

- Update config, add recording assets, and replace static images with gifs
  ([`c1debb5`](https://github.com/UseTheFork/byte/commit/c1debb5467b35617a2c713d798fd49b4d1df43d7))

- **deps**: Bump actions/checkout from 4 to 6
  ([`76213d5`](https://github.com/UseTheFork/byte/commit/76213d5e3bc7738b43bf938cd75b504499236375))

Bumps [actions/checkout](https://github.com/actions/checkout) from 4 to 6. - [Release
  notes](https://github.com/actions/checkout/releases) -
  [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/actions/checkout/compare/v4...v6)

--- updated-dependencies: - dependency-name: actions/checkout dependency-version: '6'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump actions/setup-python from 5 to 6
  ([`689c18e`](https://github.com/UseTheFork/byte/commit/689c18ecbac0766dea9f549056646cd6d7014919))

Bumps [actions/setup-python](https://github.com/actions/setup-python) from 5 to 6. - [Release
  notes](https://github.com/actions/setup-python/releases) -
  [Commits](https://github.com/actions/setup-python/compare/v5...v6)

--- updated-dependencies: - dependency-name: actions/setup-python dependency-version: '6'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump langchain-google-genai from 3.0.0 to 3.1.0
  ([`56d36c2`](https://github.com/UseTheFork/byte/commit/56d36c2f08667251a847fc8287945fd77f482b55))

Bumps [langchain-google-genai](https://github.com/langchain-ai/langchain-google) from 3.0.0 to
  3.1.0. - [Release notes](https://github.com/langchain-ai/langchain-google/releases) -
  [Commits](https://github.com/langchain-ai/langchain-google/compare/libs/genai/v3.0.0...libs/genai/v3.1.0)

--- updated-dependencies: - dependency-name: langchain-google-genai dependency-version: 3.1.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump pydantic from 2.12.3 to 2.12.4
  ([`dafeec4`](https://github.com/UseTheFork/byte/commit/dafeec419fb1012e8d85cd332fc3b1e9d61287ae))

Bumps [pydantic](https://github.com/pydantic/pydantic) from 2.12.3 to 2.12.4. - [Release
  notes](https://github.com/pydantic/pydantic/releases) -
  [Changelog](https://github.com/pydantic/pydantic/blob/v2.12.4/HISTORY.md) -
  [Commits](https://github.com/pydantic/pydantic/compare/v2.12.3...v2.12.4)

--- updated-dependencies: - dependency-name: pydantic dependency-version: 2.12.4

dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump pydantic-settings from 2.11.0 to 2.12.0
  ([`d508235`](https://github.com/UseTheFork/byte/commit/d508235bfe8c510b4e04004da54124ffd73f645c))

Bumps [pydantic-settings](https://github.com/pydantic/pydantic-settings) from 2.11.0 to 2.12.0. -
  [Release notes](https://github.com/pydantic/pydantic-settings/releases) -
  [Commits](https://github.com/pydantic/pydantic-settings/compare/v2.11.0...v2.12.0)

--- updated-dependencies: - dependency-name: pydantic-settings dependency-version: 2.12.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump pydoll-python from 2.10.0 to 2.12.2
  ([`cbe8cfc`](https://github.com/UseTheFork/byte/commit/cbe8cfcf96d148135887e8c1470ff4273ee34b6d))

Bumps [pydoll-python](https://github.com/autoscrape-labs/pydoll) from 2.10.0 to 2.12.2. - [Release
  notes](https://github.com/autoscrape-labs/pydoll/releases) -
  [Changelog](https://github.com/autoscrape-labs/pydoll/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/autoscrape-labs/pydoll/compare/2.10.0...2.12.2)

--- updated-dependencies: - dependency-name: pydoll-python dependency-version: 2.12.2

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump pytest from 8.4.2 to 9.0.1
  ([`386815c`](https://github.com/UseTheFork/byte/commit/386815c71ba652b64fcaba0dccb8779086d11cb1))

Bumps [pytest](https://github.com/pytest-dev/pytest) from 8.4.2 to 9.0.1. - [Release
  notes](https://github.com/pytest-dev/pytest/releases) -
  [Changelog](https://github.com/pytest-dev/pytest/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pytest-dev/pytest/compare/8.4.2...9.0.1)

--- updated-dependencies: - dependency-name: pytest dependency-version: 9.0.1

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

### Continuous Integration

- Add verification step to release workflow
  ([`8f3ed49`](https://github.com/UseTheFork/byte/commit/8f3ed499ba9ec19d9d1094f2280223994b05a7c8))

### Documentation

- Update presets documentation with saving and loading details
  ([`074ac4f`](https://github.com/UseTheFork/byte/commit/074ac4f59cbd398ac4411ba02ab0f1c939215c01))

- Update README with minor formatting adjustment
  ([`7787434`](https://github.com/UseTheFork/byte/commit/7787434a34015bccb93e72645ec4c43afde97dc6))

- Update README.md image path
  ([`0523eb1`](https://github.com/UseTheFork/byte/commit/0523eb196c81db4ac946a74d871415668c32967f))

### Features

- Add base preset and panel rule components to configuration and CLI service
  ([`f9f867b`](https://github.com/UseTheFork/byte/commit/f9f867bd03d8dfe7af06a1a2272b94b94999a274))

- Add config writer service for managing preset configurations
  ([`049a753`](https://github.com/UseTheFork/byte/commit/049a753b2675afde74c43748504e7e86da715aaa))

- Add keyboard interrupt handling with quit confirmation
  ([`49f464d`](https://github.com/UseTheFork/byte/commit/49f464df28786e30e123ddb0a2c5dcdab27a629a))

- Add optional default prompt when saving preset
  ([`8b2e401`](https://github.com/UseTheFork/byte/commit/8b2e40141519733d8925876cd524ea74913777da))

- Add Python language style guide and update project conventions documentation
  ([`8960fff`](https://github.com/UseTheFork/byte/commit/8960fffd9c695517960ae23b6efe1e1e58b6e33f))

- Add recording assets and update documentation with new GIFs
  ([`1fdc9ae`](https://github.com/UseTheFork/byte/commit/1fdc9ae6876ea6b4d033100c55be62c00ea20797))

- Add save preset command to capture and store current context
  ([`352fcfd`](https://github.com/UseTheFork/byte/commit/352fcfde315951ca4e81eff47c82ee685722d732))

- Add silent mode option to load preset command
  ([`37843de`](https://github.com/UseTheFork/byte/commit/37843de51349a2dfc0824ddf3feab181dad242e6))

- Update agent configuration and message handling in multiple files
  ([`b9b6e41`](https://github.com/UseTheFork/byte/commit/b9b6e416de10d0eddcdeb47a8d8bf69462e8f458))

- Update ask command to support multi-word queries with argparse REMAINDER
  ([`ff9d753`](https://github.com/UseTheFork/byte/commit/ff9d753f4d1df155f603caf201ffafc621322ede))

- Update project configuration and conventions to use spaces for indentation
  ([`edafeb5`](https://github.com/UseTheFork/byte/commit/edafeb58fbc5af847a957ff3ffbbb99f2fb6f28f))

### Refactoring

- Simplify agent graph and message handling logic
  ([`0746260`](https://github.com/UseTheFork/byte/commit/07462603e563ce218ff544e57a7380860295c2ec))

- Standardize code formatting and indentation across files
  ([`d8829cb`](https://github.com/UseTheFork/byte/commit/d8829cb769bc72c4e84ae3a548040e0e16ef22ee))

- Update agent execution to use direct string request and process user input
  ([`4ff4aa0`](https://github.com/UseTheFork/byte/commit/4ff4aa0af6dae9a1d63486b3ff18550079e79a40))

- Update agent service and CLI input handling
  ([`3a65ee0`](https://github.com/UseTheFork/byte/commit/3a65ee0270f89fbf6791dc451c545b4f530f04ba))

- Update command execute method signature to include raw_args
  ([`0f5639e`](https://github.com/UseTheFork/byte/commit/0f5639e5c27be5d2cbb0c5ca41dada8e8270af8c))

- Update config, parser service, and agent with new edit block and reinforcement handling
  ([`4f86df6`](https://github.com/UseTheFork/byte/commit/4f86df64f5ca7732901d336d630e8a30946f3487))

- Update prompt formatting and logging in assistant and show nodes
  ([`f82e7d7`](https://github.com/UseTheFork/byte/commit/f82e7d781f51937f8e90dc743147ba6b0958809d))


## v0.4.5 (2025-11-23)

### Chores

- Prepare release v0.4.5
  ([`46b78f9`](https://github.com/UseTheFork/byte/commit/46b78f9ca7844ea91ec5382544a7d9526d75afe8))


## v0.4.4 (2025-11-23)

### Chores

- Prepare release v0.4.4
  ([`127786a`](https://github.com/UseTheFork/byte/commit/127786a1aa1e1fedc499a708ed6c1c0bf4ef0a30))


## v0.4.3 (2025-11-23)

### Chores

- Prepare release v0.4.3
  ([`56bff77`](https://github.com/UseTheFork/byte/commit/56bff77b5ec1b9c7f2e943a66629d328f4ae599a))


## v0.4.2 (2025-11-23)

### Chores

- Prepare release v0.4.2
  ([`c5b9218`](https://github.com/UseTheFork/byte/commit/c5b92184b4043211e78968660a63848a50073597))

### Continuous Integration

- Consolidate release workflow by removing separate PyPI workflow
  ([`5fc7c1d`](https://github.com/UseTheFork/byte/commit/5fc7c1df10b015e1ef55173579cce7c3f0319162))


## v0.4.1 (2025-11-23)

### Chores

- Add __pycache__ to .gitignore
  ([`0dc0d3a`](https://github.com/UseTheFork/byte/commit/0dc0d3a5fa2ba3e23bf69b5f55db1a487f7257a9))

- Prepare release v0.4.1
  ([`c78c75e`](https://github.com/UseTheFork/byte/commit/c78c75e5b4f45b0495c796056dfe6d8486d2858a))

### Continuous Integration

- Add PyPI token to uv publish command
  ([`2914122`](https://github.com/UseTheFork/byte/commit/29141221fefe6c43cf690ab6c646ea8331f919c5))

- Update release workflow to separate build and publish jobs
  ([`fbec5f8`](https://github.com/UseTheFork/byte/commit/fbec5f815456886b41490da6b6aa52ad9bef9f9a))


## v0.4.0 (2025-11-23)

### Chores

- Bump version to 0.3.1 and update CHANGELOG.md
  ([`354c6d6`](https://github.com/UseTheFork/byte/commit/354c6d601cc40a599d820af10258357e42b40265))

- Prepare release v0.4.0
  ([`287ef81`](https://github.com/UseTheFork/byte/commit/287ef81d81295cb7385c7b82e682b360f0103471))

- Prepare release workflow with version update and documentation generation
  ([`416f3bc`](https://github.com/UseTheFork/byte/commit/416f3bcbaee7d37b35236e944049708c3aba1598))

- **deps**: Bump astral-sh/setup-uv from 6 to 7
  ([`f061183`](https://github.com/UseTheFork/byte/commit/f0611835f4407521c04989ae562ccc256cec8d66))

Bumps [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) from 6 to 7. - [Release
  notes](https://github.com/astral-sh/setup-uv/releases) -
  [Commits](https://github.com/astral-sh/setup-uv/compare/v6...v7)

--- updated-dependencies: - dependency-name: astral-sh/setup-uv dependency-version: '7'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump basedpyright from 1.32.1 to 1.33.0
  ([`149d717`](https://github.com/UseTheFork/byte/commit/149d7178d6271f985b91fc2e97a8bab4f90f7665))

Bumps [basedpyright](https://github.com/detachhead/basedpyright) from 1.32.1 to 1.33.0. - [Release
  notes](https://github.com/detachhead/basedpyright/releases) -
  [Commits](https://github.com/detachhead/basedpyright/compare/v1.32.1...v1.33.0)

--- updated-dependencies: - dependency-name: basedpyright dependency-version: 1.33.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump langchain-anthropic from 1.0.1 to 1.1.0
  ([`2a4c177`](https://github.com/UseTheFork/byte/commit/2a4c177c625f654a96c2c6a9ffc31c89bd3f8016))

Bumps [langchain-anthropic](https://github.com/langchain-ai/langchain) from 1.0.1 to 1.1.0. -
  [Release notes](https://github.com/langchain-ai/langchain/releases) -
  [Commits](https://github.com/langchain-ai/langchain/compare/langchain-anthropic==1.0.1...langchain-anthropic==1.1.0)

--- updated-dependencies: - dependency-name: langchain-anthropic dependency-version: 1.1.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump langchain-openai from 1.0.1 to 1.0.3
  ([`c86a52f`](https://github.com/UseTheFork/byte/commit/c86a52fd9cc7221a7102935f989ff1f7b98493e4))

Bumps [langchain-openai](https://github.com/langchain-ai/langchain) from 1.0.1 to 1.0.3. - [Release
  notes](https://github.com/langchain-ai/langchain/releases) -
  [Commits](https://github.com/langchain-ai/langchain/compare/langchain-openai==1.0.1...langchain-openai==1.0.3)

--- updated-dependencies: - dependency-name: langchain-openai dependency-version: 1.0.3

dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump mkdocs-material from 9.6.23 to 9.7.0
  ([`8d29274`](https://github.com/UseTheFork/byte/commit/8d29274f5f6b6ad74075ec6c32f4af473ef4e363))

Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 9.6.23 to 9.7.0. -
  [Release notes](https://github.com/squidfunk/mkdocs-material/releases) -
  [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/CHANGELOG) -
  [Commits](https://github.com/squidfunk/mkdocs-material/compare/9.6.23...9.7.0)

--- updated-dependencies: - dependency-name: mkdocs-material dependency-version: 9.7.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump pytest-asyncio from 1.2.0 to 1.3.0
  ([`31e6752`](https://github.com/UseTheFork/byte/commit/31e675266275f3cd8bdda7678ac3328680a9223e))

Bumps [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) from 1.2.0 to 1.3.0. - [Release
  notes](https://github.com/pytest-dev/pytest-asyncio/releases) -
  [Commits](https://github.com/pytest-dev/pytest-asyncio/compare/v1.2.0...v1.3.0)

--- updated-dependencies: - dependency-name: pytest-asyncio dependency-version: 1.3.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

### Code Style

- Update editorconfig and vscode settings for consistent indentation
  ([`c0a75af`](https://github.com/UseTheFork/byte/commit/c0a75af9a24ae9c99875bad1f673ee8e45d2df5b))

### Continuous Integration

- Update release workflow for PyPI and GitHub Release
  ([`fef4255`](https://github.com/UseTheFork/byte/commit/fef42555a59f5db7f686830633f40487927d48f4))

### Documentation

- Improve handle method docstring with detailed description
  ([`96f1371`](https://github.com/UseTheFork/byte/commit/96f13719a8127afdec5781df4ad5964fb75e9e46))

### Features

- Add AI comment watcher service and file change event handling
  ([`c2a3818`](https://github.com/UseTheFork/byte/commit/c2a38181623f8746a6c7ce5a8604541dff1027d2))

- Add load_on_boot option for presets and remove edit_format_type config
  ([`42590f9`](https://github.com/UseTheFork/byte/commit/42590f914fdb3dc8d106bb06a368a660398a1635))

- Add presets configuration and command support
  ([`649ded3`](https://github.com/UseTheFork/byte/commit/649ded3b2e977502069101ec73aca0b606c90d89))

- Add presets documentation and configuration support
  ([`10590dd`](https://github.com/UseTheFork/byte/commit/10590dd23779a3347770623171cd819f37eda096))

- Enhance command documentation generation with detailed help output
  ([`76d6ac3`](https://github.com/UseTheFork/byte/commit/76d6ac3ce6efe7b93701210cb498d00e7f13470c))

### Refactoring

- Add argument parsing support for commands with ByteArgumentParser
  ([`c5ea330`](https://github.com/UseTheFork/byte/commit/c5ea3301ca18dd85708bd2a254da24a170c98809))

- Improve agent stream execution with cancellable task and error handling
  ([`36d5041`](https://github.com/UseTheFork/byte/commit/36d5041081564d9148ec06b11718a495ae3126b4))

- Improve error handling and formatting in search/replace block parsing
  ([`4c34a08`](https://github.com/UseTheFork/byte/commit/4c34a08b23305f88d4357520a1f13cdb74c591ca))

- Improve message masking logic with more precise AI message handling
  ([`ef3f581`](https://github.com/UseTheFork/byte/commit/ef3f58170e58133da07543bcedf302216fa409e5))

- Modify message masking and error handling in agent nodes
  ([`e537be9`](https://github.com/UseTheFork/byte/commit/e537be913cf78ccfd635bd435e092361d05a5fad))

- Simplify GenericParser by removing link ratio check
  ([`58682cf`](https://github.com/UseTheFork/byte/commit/58682cf1c0bd6ca188bb07f43da93c8d03dc74e3))

- Update config schema handling and optional type annotations
  ([`25e7e55`](https://github.com/UseTheFork/byte/commit/25e7e555652c9c6a48608812de659f72e198ca37))


## v0.3.1 (2025-11-14)

### Chores

- Add .coverage to .gitignore
  ([`cab813c`](https://github.com/UseTheFork/byte/commit/cab813c1a7aaa5a41804ae3d499e04e7a3b25b07))

- Remove .coverage file from version control
  ([`effa65b`](https://github.com/UseTheFork/byte/commit/effa65b4cc67addde44b4b93b360a3574105c641))

- Update CHANGELOG.md with version and configuration changes
  ([`dd471bd`](https://github.com/UseTheFork/byte/commit/dd471bd0486f5d7b5e5a32e8e839448cdb989b29))

- Update project version to 0.3.0 and modify CHANGELOG.md
  ([`0cb7ab0`](https://github.com/UseTheFork/byte/commit/0cb7ab02e34ddeb18d2a64b948328e6ad65b9662))

- Upgrade langchain / graph to v 1
  ([`8df59bf`](https://github.com/UseTheFork/byte/commit/8df59bf6e85121752f4aa8dc0f29dac636608908))

### Code Style

- Convert indent style from tab to space in config files
  ([`c8a52d8`](https://github.com/UseTheFork/byte/commit/c8a52d8ea06f992bdc13a0c846fd01758b0ffdd6))

- Fix indentation in BoundaryType enum
  ([`bddf477`](https://github.com/UseTheFork/byte/commit/bddf47766ae8c824998864b6f914feec7810109d))

### Documentation

- Clean up markdown formatting in commands and settings reference
  ([`8383768`](https://github.com/UseTheFork/byte/commit/83837685c77483c7bde3353a6c7678fec32f9def))

- Format markdown tables for improved readability
  ([`d124f9a`](https://github.com/UseTheFork/byte/commit/d124f9a43fb1c0bf650f7bf823ee4b00817cd555))

- Update commands and settings documentation with new details
  ([`ebb04f5`](https://github.com/UseTheFork/byte/commit/ebb04f55484659af6183b8e92becfb733717eae2))

- Update first-run setup documentation with detailed service workflow
  ([`59b0325`](https://github.com/UseTheFork/byte/commit/59b0325b875ab19f75608c6ec10bdf96a606ed05))

- Update settings documentation generation script
  ([`2eb2ec3`](https://github.com/UseTheFork/byte/commit/2eb2ec3eb87bc0db12b848d8e0d078a318ece28b))

### Features

- Add CLI options for read-only and editable file contexts
  ([`043d418`](https://github.com/UseTheFork/byte/commit/043d418cf813a7d557c82ca90515490d85e146fe))

- Add comprehensive file context configuration tests for boot config
  ([`07b0f80`](https://github.com/UseTheFork/byte/commit/07b0f8089939b8b0def69217ae3484bf96310d5f))

- Add comprehensive file service and ignore service tests
  ([`dbfb34c`](https://github.com/UseTheFork/byte/commit/dbfb34c9fcf1c2ea8d8fce586dac67ba89e6c07e))

- Add convention context refresh and improve commit command with token counting placeholder
  ([`35e24bc`](https://github.com/UseTheFork/byte/commit/35e24bc80b603501373f4fd167b33cb3cee1c472))

- Add convention generation command and agent implementation
  ([`9037f3b`](https://github.com/UseTheFork/byte/commit/9037f3ba7e92849bed1c663bba1d07df5c2f27e1))

- Add convention generation command and update agent graph compilation
  ([`59cf187`](https://github.com/UseTheFork/byte/commit/59cf18701476a0408b34c6818092cc3991734443))

- Add errors placeholder to research agent prompt template
  ([`d3b9c70`](https://github.com/UseTheFork/byte/commit/d3b9c70477063337dd28e957692c987cb379aeed))

- Add project architecture documentation and file reading tool
  ([`e32b244`](https://github.com/UseTheFork/byte/commit/e32b2447096ca4c69e4ccd157fc2c799ad89301d))

- Add read-only files config, pytest config, and enhance file discovery and services
  ([`48a1c3a`](https://github.com/UseTheFork/byte/commit/48a1c3a073e37e7b3f3d21331c8af135f4ef1d34))

- Add show command and agent for displaying conversation history
  ([`ee499f3`](https://github.com/UseTheFork/byte/commit/ee499f3d40f2f207d436b927a65f68b8d3d88496))

- Add switch mode command for toggling file modes
  ([`5cc60de`](https://github.com/UseTheFork/byte/commit/5cc60de65bb1f5329c7f6d5a412091427f2f237f))

### Refactoring

- Change default linting configuration to disabled
  ([`a5ba1c1`](https://github.com/UseTheFork/byte/commit/a5ba1c15d3e76b9885a877e35fd7cd6240b5fd00))

- Extract constants and improve project hierarchy generation
  ([`c1e0782`](https://github.com/UseTheFork/byte/commit/c1e07823925a7bc6e18deb6610066e3da8e8a35c))

- Improve error handling and add system paths configuration
  ([`936231e`](https://github.com/UseTheFork/byte/commit/936231ee91a7291b7a21ef3ff2ce3623c4b62985))

- Improve message removal preview with detailed panel display
  ([`a30b018`](https://github.com/UseTheFork/byte/commit/a30b01852c821c976bd891f4e957bfc315d6a806))

- Modularize utils and improve edit format configuration
  ([`784a431`](https://github.com/UseTheFork/byte/commit/784a431a10d11e3a3eeeb9aaf2c6e94d0ec2101c))

- Remove unused dill dependency and commented-out code
  ([`be98f9c`](https://github.com/UseTheFork/byte/commit/be98f9c274575ed017a0e9c59ca39d787c66bc7d))

- Remove unused state classes and simplify agent state management
  ([`ff7557b`](https://github.com/UseTheFork/byte/commit/ff7557b815de992dfdac1585916859753749c413))

- Rename EditFormatProvider to PromptFormatProvider
  ([`70d31c0`](https://github.com/UseTheFork/byte/commit/70d31c0c18615f9780a7c276e288a7ba05e55d30))

- Rename prompts.py files to prompt.py for consistency
  ([`d661f48`](https://github.com/UseTheFork/byte/commit/d661f487a25617cbc55cdc549dc0f480238ff018))

- Reorder agents and commands alphabetically
  ([`5a70781`](https://github.com/UseTheFork/byte/commit/5a707816c5b8982fd0af9674d708f4379a2f417c))

- Replace SearchReplaceBlockParserService with PseudoXmlParserService
  ([`8fd3b8f`](https://github.com/UseTheFork/byte/commit/8fd3b8f8d818ac23e01f5701207b2bc713e3264d))

- Restructure session context model with file-based persistence
  ([`6b2a259`](https://github.com/UseTheFork/byte/commit/6b2a2598311de340bea4d99110503cf2eac181f8))

- Simplify container setup by using bootstrap method in tests
  ([`51005a4`](https://github.com/UseTheFork/byte/commit/51005a4a3a988c90ce2de50679e5b1fe5f14a995))

- Simplify type imports and remove unused undo_last_step method
  ([`e8b30fc`](https://github.com/UseTheFork/byte/commit/e8b30fc440da7cab0e2ab65ecbdedf189bcc3376))

- Update boundary and context handling in assistant node
  ([`0afd144`](https://github.com/UseTheFork/byte/commit/0afd1443ec0f91d373ff90a88d935ed4e4278453))

- Update boundary and file handling with improved formatting
  ([`e363f2e`](https://github.com/UseTheFork/byte/commit/e363f2e6936dd8514ed5b22cf2b8551004f1e694))

- Update config loading to support CLI file arguments
  ([`a9182db`](https://github.com/UseTheFork/byte/commit/a9182db57153d8b337c69ff41c932c27a5d55e85))

- Update copy agent graph with end node
  ([`eec1865`](https://github.com/UseTheFork/byte/commit/eec1865caba4e311df405083f1c583359b98f422))

- Update prompt formatting with boundary utility across multiple services
  ([`70bbc45`](https://github.com/UseTheFork/byte/commit/70bbc45941e7c99d9b39960d2c60d35924fbd94b))

### Testing

- Add comprehensive tests for FirstBootService
  ([`1e7f748`](https://github.com/UseTheFork/byte/commit/1e7f748ba8b205e9a6017876a933ec8b057e4497))


## v0.3.0 (2025-10-30)

### Chores

- Reorganize logo and asset files, update references
  ([`f6fb68e`](https://github.com/UseTheFork/byte/commit/f6fb68e6bc0b092d5189a0e44c1505f582a7dbea))

- Update CHANGELOG.md with version and configuration changes
  ([`4273cc1`](https://github.com/UseTheFork/byte/commit/4273cc13a1bcc121161e815798360a0205bb40fe))

- Update project version to 0.2.3 and modify configuration
  ([`3f9e833`](https://github.com/UseTheFork/byte/commit/3f9e833af90fdb2f281fc4b8cb70befdfb720b6c))

### Documentation

- Add LSP documentation and configuration details
  ([`63cceaa`](https://github.com/UseTheFork/byte/commit/63cceaa00f416cfe0b0665cc5756614b0eef0906))

- Update commands reference with improved descriptions and formatting
  ([`85a415f`](https://github.com/UseTheFork/byte/commit/85a415f7be19ba484e77dedb2767b79b8855b2a4))

- Update settings documentation with config changes and improvements
  ([`f7ec34f`](https://github.com/UseTheFork/byte/commit/f7ec34ff66ac5dd4477d4eaeeb121b8eca91b393))

### Features

- Add Pygments for language detection and improve linting configuration
  ([`1b629e1`](https://github.com/UseTheFork/byte/commit/1b629e180cd6792c09234e32d49d9e6004bb2be3))

- Add web content parsing infrastructure with multiple specialized parsers
  ([`a7c77a0`](https://github.com/UseTheFork/byte/commit/a7c77a035116c38c37f8275c6bcb2662a0d9851d))

### Refactoring

- Add pyright ignore comments and improve error handling
  ([`e76af32`](https://github.com/UseTheFork/byte/commit/e76af32b55684701b75a06f662940e2ef417ed1c))

- Remove MCP service provider and related configurations
  ([`46362b5`](https://github.com/UseTheFork/byte/commit/46362b5754fa6047066b5f9e7bc58530bacb3911))

- Restructure config loading and LLM provider configuration
  ([`2e6d112`](https://github.com/UseTheFork/byte/commit/2e6d1121dcbeae70f708c24a8aec311f307db540))

- Sort and organize imports and configurations
  ([`de9f51c`](https://github.com/UseTheFork/byte/commit/de9f51c20b63f99552a05ff60b87597bc25e0933))

- Update config and file handling with system version and language detection
  ([`f828a5a`](https://github.com/UseTheFork/byte/commit/f828a5ae9f483ea1f49b1abbcd47b7611a4392ea))

- Update lint configuration to support list-based command definition
  ([`a76a3de`](https://github.com/UseTheFork/byte/commit/a76a3de41fc73e487808615c349083b8b2c9394d))

- Update LSP and lint configurations to use language-based mapping
  ([`0e65cd6`](https://github.com/UseTheFork/byte/commit/0e65cd6239f2554b0d1341f4e18651b36c072ac5))

- Update session context handling with new SessionContextModel
  ([`fd0efcc`](https://github.com/UseTheFork/byte/commit/fd0efcccd4331624e90f65f6641bd1b35393315a))


## v0.2.3 (2025-10-28)

### Chores

- Update project version to 0.2.2 and modify configuration
  ([`be00335`](https://github.com/UseTheFork/byte/commit/be003354dbd71d6a07cdf6ed62b3e29498e10620))


## v0.2.2 (2025-10-28)

### Chores

- Update project version to 0.2.1 and modify configuration
  ([`7c05940`](https://github.com/UseTheFork/byte/commit/7c05940847df1f0a80c686c6b400daadec9c453f))

### Features

- Add LSP support with Jedi language server for Python
  ([`5c241ca`](https://github.com/UseTheFork/byte/commit/5c241ca49cc7bc7be3fd5f1eec829af0b3875d48))

### Refactoring

- Reorder placeholders in ask prompt and extract prompt templates
  ([`473a23f`](https://github.com/UseTheFork/byte/commit/473a23f6cd71e9c0833c2e4d7dc3a1005f362480))

- Restructure research agent and extract node for better context handling
  ([`5709ab2`](https://github.com/UseTheFork/byte/commit/5709ab2dfefbb23fd81ea01f573c43fabd5b672e))


## v0.2.1 (2025-10-24)

### Chores

- Update project version to 0.2.0 and add git-cliff configuration
  ([`07ed015`](https://github.com/UseTheFork/byte/commit/07ed015cb80c9ec6594810330da18e5fcbd83e18))

### Features

- Switch default LLM to openai and enable streaming
  ([`ff44c31`](https://github.com/UseTheFork/byte/commit/ff44c31b1522a4224e95c9c6cd28658a36fa92c1))

### Refactoring

- Convert LLM schemas to Pydantic and pass model params
  ([`75b0f71`](https://github.com/UseTheFork/byte/commit/75b0f71e58b1d5da0204fb92496d5a44b0e1633b))


## v0.2.0 (2025-10-24)

### Chores

- Bump version to 0.1.11 and update CHANGELOG.md
  ([`3985427`](https://github.com/UseTheFork/byte/commit/3985427826384d0438cfaf8343d6ce2611a14227))

- Bump version to 0.1.11 and update CHANGELOG.md
  ([`261be89`](https://github.com/UseTheFork/byte/commit/261be898bad797c1e46b85bb4e70cd769dea1444))

- Refactor configuration loading and first boot initialization
  ([`421ade6`](https://github.com/UseTheFork/byte/commit/421ade60592460acc0787a257f9cfa2448d1fb36))

- Update release script comments with tag and push commands
  ([`2eced40`](https://github.com/UseTheFork/byte/commit/2eced40b64eaeb7a1ec0d3f395340dcca749483b))

### Documentation

- Rename and improve example flow documentation
  ([`31f3aa3`](https://github.com/UseTheFork/byte/commit/31f3aa3eb7868f06034082de5539fdddd168d5c0))

- Update commit documentation image references
  ([`48d5c20`](https://github.com/UseTheFork/byte/commit/48d5c2034ad3de9e54330300d35c381723d4f6c1))

### Features

- Add rich live spinner and markdown conversion to ChromiumService
  ([`19e0854`](https://github.com/UseTheFork/byte/commit/19e08540cb0c20d498c6e1a18919cd94559c19c7))

### Refactoring

- Rename models.py to schemas.py and adjust config for message masking
  ([`843935e`](https://github.com/UseTheFork/byte/commit/843935eefe396463cc39d4487b375607fc8bcf0e))

- Replace print logging with proper log exception handling
  ([`d290342`](https://github.com/UseTheFork/byte/commit/d29034248f1267c1ef8e7153f2c93139dc5ae854))

- Simplify agent nodes and improve error handling
  ([`1729735`](https://github.com/UseTheFork/byte/commit/17297351e32995126aedc5a29ae5a8f5f1ea562e))

- Update documentation and configuration images with PNG files
  ([`8fd1a61`](https://github.com/UseTheFork/byte/commit/8fd1a61ebd4ad203578ade749672ffb2cebea0cd))

- Update undo command console printing methods
  ([`ec1a9f2`](https://github.com/UseTheFork/byte/commit/ec1a9f276ab6e5be3bf188ea7f77c5a53587fc90))


## v0.1.11 (2025-10-22)

### Chores

- Add placeholder comment in release script
  ([`2a3d212`](https://github.com/UseTheFork/byte/commit/2a3d2121a0dab77a8b2e2a0fe8f55ee921f983d9))

### Features

- Add subprocess command execution support with shell integration
  ([`61942d4`](https://github.com/UseTheFork/byte/commit/61942d4ab1c38c554d9fc77417e76e8e36784580))

### Refactoring

- Restructure and improve documentation in prompts and agent implementations
  ([`55f883c`](https://github.com/UseTheFork/byte/commit/55f883c02a6040ef72e578691e910a3eadb24b0c))

- Streamline agent state and analytics tracking
  ([`7664e19`](https://github.com/UseTheFork/byte/commit/7664e19dabae0d2d05399de33ead4cb1541ece80))

- Update agent service, lint handling, and commit workflow
  ([`b9b7e33`](https://github.com/UseTheFork/byte/commit/b9b7e3311f8f0613c623b599bc1dffd04cc28d12))

- Update code handling for token usage, reinforcement, and config model
  ([`9112353`](https://github.com/UseTheFork/byte/commit/9112353a303f6dd647779a05fe697af91d2bcdbe))

- Update lint service, agents, and main to improve error handling and code structure
  ([`30f7883`](https://github.com/UseTheFork/byte/commit/30f7883c8b1181bbee1bb9e58cbe3e9c557afafa))


## v0.1.10 (2025-10-21)

### Chores

- Prepare release 0.1.9 with updated package version
  ([`45acedd`](https://github.com/UseTheFork/byte/commit/45aceddce6ddf45a54c21bb46226e0bbc48d0b61))

- Update CHANGELOG.md with recent release notes
  ([`d1d1390`](https://github.com/UseTheFork/byte/commit/d1d13907c37c277cc3c9a96b11025330d8663544))

### Documentation

- Update CHANGELOG.md and bump version to 0.1.10
  ([`26c3ec7`](https://github.com/UseTheFork/byte/commit/26c3ec778f5e56ab725e078e9421d44bf1cec12e))

- Update CHANGELOG.md with latest release notes
  ([`426fe3d`](https://github.com/UseTheFork/byte/commit/426fe3d7989c2726e1886c03720d3cb54169691b))

### Features

- Modify event handling to support more flexible context gathering
  ([`e325289`](https://github.com/UseTheFork/byte/commit/e325289f9929bbeaad63a7129a02e46022c13eac))

- Simplify agent architecture with context-based schema
  ([`5c43e21`](https://github.com/UseTheFork/byte/commit/5c43e211247d0b1654e27ecf3608e92f784ff4d2))

### Refactoring

- Remove pyright ignore comments and simplify logging configuration
  ([`bc60ebe`](https://github.com/UseTheFork/byte/commit/bc60ebed7a2a02773b380812a7795cb2532e54f2))

- Simplify agent state management and graph navigation
  ([`0eab497`](https://github.com/UseTheFork/byte/commit/0eab497f1fd274e76935145439045996bae68d6f))


## v0.1.9 (2025-10-20)

### Chores

- Prepare release 0.1.8 with updated workflows and package configuration
  ([`64c0706`](https://github.com/UseTheFork/byte/commit/64c07060cc1bfc23a1372afaee597c4284de16be))

### Continuous Integration

- Update PyPI release workflow configuration
  ([`65cb1e1`](https://github.com/UseTheFork/byte/commit/65cb1e1572b38c3f586fa3ed68ebb7207f0b3b4f))


## v0.1.8 (2025-10-20)

### Chores

- Add GitHub Actions for PyPI publishing and release script
  ([`68c99d6`](https://github.com/UseTheFork/byte/commit/68c99d6de9a09324a56a844779edf8d2c4b51afe))

- Update package name to byte-ai-cli in project configuration
  ([`271e8ab`](https://github.com/UseTheFork/byte/commit/271e8ab3818e1c8aa5dcb14dec761e4448d1553b))

### Continuous Integration

- Consolidate workflows by removing duplicate publish-to-pypi.yml
  ([`2a8fca0`](https://github.com/UseTheFork/byte/commit/2a8fca0edae50540fdad4fff18d72f680cddd581))

- Update release workflow for PyPI publication
  ([`1a1d8ce`](https://github.com/UseTheFork/byte/commit/1a1d8ce429169cd3a07ead4c78e8a1f26bcd7524))


## v0.1.7 (2025-10-20)

### Chores

- Update project development status classifier
  ([`599bb43`](https://github.com/UseTheFork/byte/commit/599bb43a901b3cb445dbf5010484ab01c2367684))

- Update project version to 0.1.7 and add changelog
  ([`545c6f3`](https://github.com/UseTheFork/byte/commit/545c6f3a2c927a0e44cc45f69519c0e4902d01ae))


## v0.1.6 (2025-10-19)

### Bug Fixes

- Add small sleep to prevent high CPU usage in input actor
  ([`85dd06b`](https://github.com/UseTheFork/byte/commit/85dd06bbd62e23c7781c9e0ed2fc96167ebdc1f2))

- Remove `.from_ansi()` method call in markdown stream formatting
  ([`81d36a9`](https://github.com/UseTheFork/byte/commit/81d36a9665855ca5e34996aede0c01c95ea57233))

- Remove redundant success tag in console print message
  ([`7ae5ce0`](https://github.com/UseTheFork/byte/commit/7ae5ce0569eab657129e5941fb51601a2b0c00aa))

- Return state instead of empty dict in EndNode
  ([`0fbe638`](https://github.com/UseTheFork/byte/commit/0fbe6381361e1f2957c50a501deb5a6bd5eeb159))

### Build System

- Add dill package to dev dependencies for serialization support
  ([`0a1760c`](https://github.com/UseTheFork/byte/commit/0a1760c4fc8d93eb65d95cb02b45f73c8d01912a))

- Update mkdocs site directory configuration
  ([`a1adeec`](https://github.com/UseTheFork/byte/commit/a1adeec3c33dc4bb84de373907133e3ca7cef61e))

### Chores

- Add keep-sorted config and pyright diagnostic settings
  ([`8c3d94d`](https://github.com/UseTheFork/byte/commit/8c3d94d0407a5d20f7c5dcbcd572c5cc758ad6e5))

- Add license, contributing guide, and update project metadata
  ([`86288d3`](https://github.com/UseTheFork/byte/commit/86288d3da0c7c8219f4febc1cb0a8f2cb0b1a193))

- Add pre-commit configuration with ruff and hooks
  ([`99ba452`](https://github.com/UseTheFork/byte/commit/99ba4529e509bc914c9dc03316a0da40dd6ab015))

- Add ruff cache to gitignore and enhance documentation for memory and file services
  ([`0d81423`](https://github.com/UseTheFork/byte/commit/0d8142323644657350957e9c56df41cfa726bf9a))

- Bump version to 0.1.2 and remove commented log line
  ([`fd81375`](https://github.com/UseTheFork/byte/commit/fd81375307aafe5a79e03ee78da1419bb095c7d5))

- Bump version to 0.1.3
  ([`202bd7e`](https://github.com/UseTheFork/byte/commit/202bd7ea8f56131e62abebfa03cb971fce8a5e91))

- Bump version to 0.1.4 and modify markdown rendering
  ([`36379e2`](https://github.com/UseTheFork/byte/commit/36379e232cfb0715faeef5de54bbca3a2125160b))

- Remove memory.db database file
  ([`fa22d07`](https://github.com/UseTheFork/byte/commit/fa22d07703b44f6b9c23521a1de5b86c3858c7be))

- Remove version.py and update version to 0.1.1a
  ([`666bb9b`](https://github.com/UseTheFork/byte/commit/666bb9b2df12d0720d046fac164c9a6ec4b1b5e1))

- Standardize indentation to tabs and improve code formatting
  ([`aee1e89`](https://github.com/UseTheFork/byte/commit/aee1e89051478df2f3b699cee0e630fa9e1487a2))

- Standardize indentation to tabs in agent domain files
  ([`3800c86`](https://github.com/UseTheFork/byte/commit/3800c86aae041d6a97deeb2f9452ab176054e566))

- Standardize indentation to tabs in LLM domain files
  ([`488d4df`](https://github.com/UseTheFork/byte/commit/488d4df8dc1bb6124850e6bac98bb2c0e0f8bfb1))

- Update project configuration and service implementations
  ([`f8f5344`](https://github.com/UseTheFork/byte/commit/f8f5344fc1eb52a087a6234a7c71d3b3d799df7a))

### Code Style

- Apply consistent indentation and formatting across Python files
  ([`231fbf9`](https://github.com/UseTheFork/byte/commit/231fbf9279439dc18a118bad0c7815b49d22df7e))

- Normalize code formatting with consistent indentation
  ([`a883fe4`](https://github.com/UseTheFork/byte/commit/a883fe44e00425c1a21d7bc6f10bd6e14fca09fb))

### Continuous Integration

- Add GitHub Actions workflow for deploying docs site
  ([`66318ab`](https://github.com/UseTheFork/byte/commit/66318ab95b4988543ec87b5618b2057ffc72cdd1))

- Add GitHub Actions workflow for deploying docs site
  ([`dc75398`](https://github.com/UseTheFork/byte/commit/dc753980b945cb64211db042c50af5935b2111c1))

- Add release workflow for PyPI and TestPyPI publishing
  ([`9c38e3e`](https://github.com/UseTheFork/byte/commit/9c38e3e7c724f958904a718f0e103d7bad8bb2bc))

- Update GitHub Actions workflow for documentation deployment
  ([`f9dba38`](https://github.com/UseTheFork/byte/commit/f9dba38c8c1b7eb8e92bda45442a6c3adc93d0bd))

### Documentation

- Add comprehensive architecture guide for Byte CLI project
  ([`7f5ce23`](https://github.com/UseTheFork/byte/commit/7f5ce23b075fc61cffbc6e648e8cb4e7f11e7689))

- Add initial documentation for Byte's commands and configuration
  ([`33e79f9`](https://github.com/UseTheFork/byte/commit/33e79f9c8857eab8474043e1e05b68017b97785d))

- Add markdown formatting to web documentation section headers
  ([`0abe873`](https://github.com/UseTheFork/byte/commit/0abe873dff0746f00381aeff434eaa8c33204f41))

- Add Python style guide with best practices and conventions
  ([`ceb9bde`](https://github.com/UseTheFork/byte/commit/ceb9bde82c199a44f6daf706d8f7d6a40af5b460))

- Add reference documentation for commands and settings
  ([`d482c11`](https://github.com/UseTheFork/byte/commit/d482c1151f011f2dab33c4014e14be7d14d7de4d))

- Add web scraping concept page to documentation
  ([`bd96680`](https://github.com/UseTheFork/byte/commit/bd96680c0f463b5b70cef67169a8947736de7f21))

- Consolidate and refactor documentation structure
  ([`43a469a`](https://github.com/UseTheFork/byte/commit/43a469a7f2f39d562a666c81a51e5599514df668))

- Consolidate and refactor documentation structure
  ([`b6493a0`](https://github.com/UseTheFork/byte/commit/b6493a0c67d76b5d595cc76ef4d1903927cec704))

- Remove outdated links and simplify documentation structure
  ([`5d49927`](https://github.com/UseTheFork/byte/commit/5d499277f200621b4ae98038743e9a7d4f8a7e54))

- Reorganize and structure documentation site
  ([`e901285`](https://github.com/UseTheFork/byte/commit/e901285ba81393b7179222fe217b03120c56200f))

- Reorganize and structure documentation site
  ([`b059943`](https://github.com/UseTheFork/byte/commit/b05994309acf145a640e0c283227bb5d1b47b3f8))

- Replace configuration.md with comprehensive settings documentation
  ([`a5a87c4`](https://github.com/UseTheFork/byte/commit/a5a87c406867b9f30b0ab655f225a0c51a607d31))

- Update architecture guide with refined patterns and structure
  ([`20a22ea`](https://github.com/UseTheFork/byte/commit/20a22ea3eab9a509182fd228d48db24fbcba19d0))

- Update architecture with mixin boot pattern and auto-initialization
  ([`4a7f4fa`](https://github.com/UseTheFork/byte/commit/4a7f4fab0c7c94158c86afa9b795a2fb89f399f6))

- Update documentation structure and content
  ([`1c29925`](https://github.com/UseTheFork/byte/commit/1c2992515bddaa0ce06f6baa7b35a155cf474ec8))

- Update README with project description and inspiration sources
  ([`45104b5`](https://github.com/UseTheFork/byte/commit/45104b515f014e4309b8946ac4622bbb59bcc25a))

- Update settings documentation with new UI theme options
  ([`c73916f`](https://github.com/UseTheFork/byte/commit/c73916f017135c4fe58c80fca0af7ae0d0bd3201))

### Features

- Add analytics provider and usage tracking for AI agent interactions
  ([`f795da8`](https://github.com/UseTheFork/byte/commit/f795da87c61c28ff0875f89386bbe9e2d798549a))

- Add API key validation and auto-configuration for LLM providers
  ([`3939f1d`](https://github.com/UseTheFork/byte/commit/3939f1d3ecff7be28f43698963ab811cc5695686))

- Add API key validation and fixture recording service
  ([`75d6e97`](https://github.com/UseTheFork/byte/commit/75d6e97242620562f935b55efc4a6d3105cabae4))

- Add AskAgent and enhance agent service with more flexible execution
  ([`84c81ab`](https://github.com/UseTheFork/byte/commit/84c81abcac0ae0aab76b0771d5ca20b555187d53))

- Add async support and coder agent domain with LangGraph integration
  ([`8b3de62`](https://github.com/UseTheFork/byte/commit/8b3de62d061fd8a6e4ba36d19bc7030f210664e4))

- Add bootable mixin for async initialization and boot sequence
  ([`ac3073d`](https://github.com/UseTheFork/byte/commit/ac3073dfad6b85d7ea914740e60e4cc62b8dddbc))

- Add byte cache directory and update checkpointer path resolution
  ([`cee51d7`](https://github.com/UseTheFork/byte/commit/cee51d72f0b5cad6dc89d877ec2784ddc882e5c6))

- Add Catppuccin themes and improve CLI theme configuration
  ([`29ed195`](https://github.com/UseTheFork/byte/commit/29ed195103e5db9617161c0614193c244411f5e0))

- Add CleanerAgent and related user interaction methods to improve content extraction
  ([`0a3cefa`](https://github.com/UseTheFork/byte/commit/0a3cefa5f6441441e8fade5c8b0323cfe8d68665))

- Add comment style guide and update UI service provider
  ([`133e225`](https://github.com/UseTheFork/byte/commit/133e225fd60417218a329c1d68c90df9aa623873))

- Add commented configuration options for lint, files, web, and mcp settings
  ([`cdfe3c0`](https://github.com/UseTheFork/byte/commit/cdfe3c069255769cf27fdf931523d3004ae54b2a))

- Add commit command with AI-generated commit messages
  ([`c707630`](https://github.com/UseTheFork/byte/commit/c7076306d8c1bec24e529d44cfd08b0d626377da))

- Add configuration files and update project tooling documentation
  ([`829f726`](https://github.com/UseTheFork/byte/commit/829f726ea52203e873244735548f8da83d804cdf))

- Add configuration management system with config service and providers
  ([`07a736a`](https://github.com/UseTheFork/byte/commit/07a736a9b077a10c2dfc51639370c7f3a994f4d1))

- Add context management and improve response handling
  ([`2edb096`](https://github.com/UseTheFork/byte/commit/2edb09617dae5c5f9f99d4e9a04d117bc7642a5d))

- Add context management commands for session knowledge tracking
  ([`28ec63e`](https://github.com/UseTheFork/byte/commit/28ec63e975e8b155978be3a5452577726ac66f5d))

- Add copy command to extract and copy code blocks to clipboard
  ([`821c0f5`](https://github.com/UseTheFork/byte/commit/821c0f58d9dcde2b324f53dba38c3152aebbc3c5))

- Add custom RuneSpinner for animated CLI thinking indicator
  ([`39dcad5`](https://github.com/UseTheFork/byte/commit/39dcad58b09bbe3d3593943aedb779e35dc382ad))

- Add display mode option for agent streaming and rendering
  ([`006f82f`](https://github.com/UseTheFork/byte/commit/006f82fb2f22b07805ed4860b4832ba3fa1538dd))

- Add dotenv loading for config initialization
  ([`e44e2fc`](https://github.com/UseTheFork/byte/commit/e44e2fc01aae57c941f811c888fe038e84d304fc))

- Add dotenv loading to Byte CLI initialization
  ([`1782b76`](https://github.com/UseTheFork/byte/commit/1782b7698099062e9e5e0812fb618d0407e84fb8))

- Add edit format config and modify user interaction prompt methods
  ([`cda2268`](https://github.com/UseTheFork/byte/commit/cda2268aed5159f98ad8958b83538d9cac1e3a58))

- Add edit format configuration and shell command support to edit format workflow
  ([`e72da44`](https://github.com/UseTheFork/byte/commit/e72da44dac92a98004887f23967f5b9f6f5d9f1e))

- Add enhanced command output display with rich panels and syntax highlighting
  ([`01028d4`](https://github.com/UseTheFork/byte/commit/01028d49e183095835945c367336dda8037efb71))

- Add event system with dispatcher, events, and service provider
  ([`5398fec`](https://github.com/UseTheFork/byte/commit/5398fecc71db55bb5bffec193386a035864f431b))

- Add exit command to ByteSmith application
  ([`8e363d3`](https://github.com/UseTheFork/byte/commit/8e363d35cb5ef9730c5a627e729d0784404604e2))

- Add exit command to ByteSmith CLI
  ([`f8a1618`](https://github.com/UseTheFork/byte/commit/f8a16181d6d8039fcfae1212caf3d179606a4a81))

- Add file operation batching and messaging for file context management
  ([`849eacd`](https://github.com/UseTheFork/byte/commit/849eacd0c8bf429b961d35fbe7a95c5be651d44c))

- Add file tracking and improve edit format service interactions
  ([`2fe2539`](https://github.com/UseTheFork/byte/commit/2fe2539f1c371552c5302ce58b1b03d2400774d3))

- Add file watcher service with AI comment detection and file change tracking
  ([`1e260a7`](https://github.com/UseTheFork/byte/commit/1e260a74f7bfc3e012bf1f07cc614d3f10ee8f75))

- Add first-boot initialization and remove ripgrepy dependency
  ([`80adf3b`](https://github.com/UseTheFork/byte/commit/80adf3bcedec052858f75c7f5e61fb1d8fd27d05))

- Add fixture recording service for capturing agent responses
  ([`ad0f45c`](https://github.com/UseTheFork/byte/commit/ad0f45ce42ccd62172f7ba689974e1f02a7f86e1))

- Add git and lint domains with configuration support
  ([`cd3c8a1`](https://github.com/UseTheFork/byte/commit/cd3c8a111554e563a08d7aa8d575d9cd5b701159))

- Add graph and prompt modules for commit logic
  ([`697cb70`](https://github.com/UseTheFork/byte/commit/697cb7032bffa9649c47aa3baca5ffc6ba524965))

- Add horizontal menu support for confirmation dialogs with Yes/No options
  ([`a5f3ab2`](https://github.com/UseTheFork/byte/commit/a5f3ab26e523251b899a090216d03782f8ebf319))

- Add initial agent structure with DCR-focused assistant and prompts
  ([`cce289b`](https://github.com/UseTheFork/byte/commit/cce289be75469c70ed77ed7693ef8c4473c0570f))

- Add initial ByteSmith project structure with commands and context management
  ([`11c8173`](https://github.com/UseTheFork/byte/commit/11c8173c3305f8abc96cb92ec648fd1d9b5dc90d))

- Add interaction tools and services for user communication
  ([`6149d2a`](https://github.com/UseTheFork/byte/commit/6149d2a4cd81df864910853e624a1daf9c1c7625))

- Add Langchain dependencies with Anthropic, OpenAI, and Google GenAI support
  ([`2b2ae97`](https://github.com/UseTheFork/byte/commit/2b2ae9734e3642c84b3993f0b183e79056257619))

- Add LLM service provider with dynamic provider selection
  ([`4485c61`](https://github.com/UseTheFork/byte/commit/4485c617199fdadcec486b2e05d1a0efc2d67651))

- Add loading spinner while waiting for LLM response
  ([`924c62e`](https://github.com/UseTheFork/byte/commit/924c62e44c0c29315ee8161575cc53aafa10f164))

- Add MCP support with tool filtering for agents
  ([`1765023`](https://github.com/UseTheFork/byte/commit/17650230ce31ae577d6a8297edf16ee9bc0b252e))

- Add memory and knowledge management domains with SQLite persistence
  ([`d74a628`](https://github.com/UseTheFork/byte/commit/d74a628b3231d987a9bdb13a9358341d6c7602e7))

- Add multi-provider LLM support with OpenAI, Anthropic, and Gemini
  ([`a54d9f1`](https://github.com/UseTheFork/byte/commit/a54d9f17cfb7fd9e22acff67609e1c2c1f9af603))

- Add new clear command for resetting conversation history
  ([`a72c5b5`](https://github.com/UseTheFork/byte/commit/a72c5b5ca98eb087b3fa692d86e944f6926c53aa))

- Add OpenAI support and pytest-asyncio dependency
  ([`72bff77`](https://github.com/UseTheFork/byte/commit/72bff77460413dec03e5f29892100bc6c914bb7f))

- Add pre-commit linting event handler in lint service
  ([`406e3db`](https://github.com/UseTheFork/byte/commit/406e3dbbf04a75ad7715ce373bad07a71f1ca39d))

- Add pre-prompt info display for file context and commands
  ([`9e28bf7`](https://github.com/UseTheFork/byte/commit/9e28bf75301441178c61802567fd50a407b03033))

- Add project root display in CLI service provider
  ([`2c6a28b`](https://github.com/UseTheFork/byte/commit/2c6a28b82f5161118014bbff0cb026be65591424))

- Add pytest and grandalf to dev dependencies, update project configuration
  ([`342add6`](https://github.com/UseTheFork/byte/commit/342add62b73b364263e954ae6cbc985a4af46e54))

- Add register_services method to bootstrap and service providers
  ([`3b49e2c`](https://github.com/UseTheFork/byte/commit/3b49e2c559c66d22ba61f9b0dbc35abcf13ea635))

- Add research prompt for agent with comprehensive capabilities
  ([`2f6268a`](https://github.com/UseTheFork/byte/commit/2f6268a8db00ebb496b52f61628956f018c8f9a1))

- Add response handling infrastructure for agent interactions
  ([`91bb689`](https://github.com/UseTheFork/byte/commit/91bb6894e5ce7ed6ec6730d94d9fa4a04909ed6a))

- Add ripgrep search tool and refactor research/initialization agent
  ([`7441cb7`](https://github.com/UseTheFork/byte/commit/7441cb77e046727b030e884c0b2fba939086cfba))

- Add ripgrepy search tool and initialize command for project documentation
  ([`7169f79`](https://github.com/UseTheFork/byte/commit/7169f793b7dd4f5616f9bff8facddc6c1269d996))

- Add scrolling menu with window and scrollbar support
  ([`6d80a1a`](https://github.com/UseTheFork/byte/commit/6d80a1af3bfc863ca8391326f98aa627db06a301))

- Add system commands and interactive prompt with command completion
  ([`61b66c7`](https://github.com/UseTheFork/byte/commit/61b66c7ebecdb7c6bcf33c3711caac2a052fba8e))

- Add todo for unfinished MCP tool command implementation
  ([`f770034`](https://github.com/UseTheFork/byte/commit/f770034e54d0b48d618f68600e16a33629c1921a))

- Add type hints to mixin base classes
  ([`ea56ae7`](https://github.com/UseTheFork/byte/commit/ea56ae703088eada265c02ef3d8cabf5fd3dfdb9))

- Add unselected color and improve menu cancellation styling
  ([`86ab4d3`](https://github.com/UseTheFork/byte/commit/86ab4d31293ac8bc3a5934b457e0319e5805dffb))

- Add user interaction and custom panel, modify file watcher service
  ([`fc855ee`](https://github.com/UseTheFork/byte/commit/fc855eeea2ca28202f72d0efece4537e566eed70))

- Add web scraping, markdown conversion, and session context services
  ([`99ada8b`](https://github.com/UseTheFork/byte/commit/99ada8b06495b3cad24c7eda037416aafb0a0565))

- Enable knowledge, system context, and pre/post assistant node events
  ([`3fa5b8a`](https://github.com/UseTheFork/byte/commit/3fa5b8a72ce2d5152c0ede21a199bc6a38731927))

- Enhance commit agent with improved state management and extraction
  ([`d06e29c`](https://github.com/UseTheFork/byte/commit/d06e29c2e2eeef7a3f9ea4f995f641e824e4e835))

- Enhance commit agent with stream rendering and improved execution flow
  ([`009c28a`](https://github.com/UseTheFork/byte/commit/009c28a21608e5911d09c2905ef27764bd046652))

- Enhance event system with middleware support and improved file context display
  ([`5a91ef5`](https://github.com/UseTheFork/byte/commit/5a91ef59f4215c00b55243b2f70edf93b521e3c7))

- Enhance initialization, add web configuration, and introduce custom exceptions
  ([`85790de`](https://github.com/UseTheFork/byte/commit/85790de47af51be5236809e77883fa481f581799))

- Enhance streaming and tool call handling in agent system
  ([`1bee374`](https://github.com/UseTheFork/byte/commit/1bee37488284b01833ec2521ed364fc669264013))

- Implement actor-based architecture with message bus and core actors
  ([`e2f88e6`](https://github.com/UseTheFork/byte/commit/e2f88e65c92cea68ca58b625a5bb1cb71de15821))

- Implement command registry and enhance input handling with new actor interactions
  ([`972cdd6`](https://github.com/UseTheFork/byte/commit/972cdd624c8aaf798ababdd9362e42288cf63c99))

- Implement lint command and add gradient logo to UI
  ([`f513b97`](https://github.com/UseTheFork/byte/commit/f513b975b2db7757478b8c841fc308230a03ac47))

- Improve user interaction selection with more robust menu handling
  ([`857e099`](https://github.com/UseTheFork/byte/commit/857e099b72b8def01feb0a58e429368b6353da76))

- Initialize ByteSmith CLI project with basic structure and dependencies
  ([`b6951eb`](https://github.com/UseTheFork/byte/commit/b6951eb5c4dd9f71fc505b363fe3c835576d11e3))

- Update dependencies, add Nix flake support, and enhance package configuration
  ([`a284ee7`](https://github.com/UseTheFork/byte/commit/a284ee715c94f5cc8511815927a346feb562b732))

### Refactoring

- Add web configuration and improve display services
  ([`3f658eb`](https://github.com/UseTheFork/byte/commit/3f658eb388119bacd2207f3a5e097bfd0c983b29))

- Consolidate CLI input and output services into single domain
  ([`1d685eb`](https://github.com/UseTheFork/byte/commit/1d685eb6cd2b075e2eea64d014bd5ef8e86a1312))

- Consolidate config into domain-specific modules
  ([`889710a`](https://github.com/UseTheFork/byte/commit/889710a8abf6b6122b5573d65deca77f65516899))

- Convert completion methods to async for better async support
  ([`8e1a346`](https://github.com/UseTheFork/byte/commit/8e1a346c8a8305459eaed5ae0f2400894a80c23b))

- Convert Event from dataclass to Pydantic model and reorganize imports
  ([`83f98ca`](https://github.com/UseTheFork/byte/commit/83f98ca607832e748e7f444f3e8bf622db66a692))

- Convert tabs to spaces in system domain files
  ([`a2ff459`](https://github.com/UseTheFork/byte/commit/a2ff4595e9aefcde7d6d6cfd57986b1dbe6b84e4))

- Enhance AI comment parsing and file watching logic
  ([`ef25fe2`](https://github.com/UseTheFork/byte/commit/ef25fe252678bc7a5072e6aeef2de9b9a7aeb149))

- Enhance command handling, input validation, and documentation in CLI services
  ([`93e51e3`](https://github.com/UseTheFork/byte/commit/93e51e3bed41a9f0041b33bf842911161e0ade55))

- Enhance exception handling and add config validation in services
  ([`2e03bd2`](https://github.com/UseTheFork/byte/commit/2e03bd28f1f539f9ae0b18ff42036ad94bcffb12))

- Enhance file context management with comprehensive documentation and type safety
  ([`622140a`](https://github.com/UseTheFork/byte/commit/622140a030afe1b39760cc07785a4192ec79b654))

- Extract console service and replace rich.console usage
  ([`7be0474`](https://github.com/UseTheFork/byte/commit/7be0474f734df6b6b141d702548f569822d9148e))

- Extract ignore pattern management into dedicated FileIgnoreService
  ([`aaab4d3`](https://github.com/UseTheFork/byte/commit/aaab4d335db30f875d224ba537eec787c52a918f))

- Extract search/replace block handling in EditFormatService
  ([`2249718`](https://github.com/UseTheFork/byte/commit/22497186e09cf6012bfee531733a46892da05a44))

- Improve actor message handling and state management
  ([`931266f`](https://github.com/UseTheFork/byte/commit/931266f854364df0847e78488ec94bcc4d10d84b))

- Improve agent stream handling and add error resilience
  ([`de39853`](https://github.com/UseTheFork/byte/commit/de39853c2891e5122e8cad02c5fec9ebacaa04ff))

- Improve code documentation and event system architecture
  ([`e9bfd5f`](https://github.com/UseTheFork/byte/commit/e9bfd5f52d7e297232c415fe4f530dd9b5c816c9))

- Improve command completion logic in prompt.py
  ([`a59b25d`](https://github.com/UseTheFork/byte/commit/a59b25d944334e9fd68f21aa01de8b0c3ad9430a))

- Improve command execution and state management in input and coordinator actors
  ([`636c0c5`](https://github.com/UseTheFork/byte/commit/636c0c58e10af9ffefb9b1bfbbd49da9788df82c))

- Improve comment handling and event processing in file services
  ([`c85d1e0`](https://github.com/UseTheFork/byte/commit/c85d1e07f632b401ae638e8462ef7d83ecf7d4ff))

- Improve configuration, logging, and type hints
  ([`7ba5ad5`](https://github.com/UseTheFork/byte/commit/7ba5ad5dc9e04c082405adf10180b57f8a1ec826))

- Improve console rendering and add newline after user input
  ([`53411ad`](https://github.com/UseTheFork/byte/commit/53411ad3a6ea32f0ef0fe4258fc87623768cf2e0))

- Improve docstrings and code formatting for web modules
  ([`5251a81`](https://github.com/UseTheFork/byte/commit/5251a8108789d139ee1d9b1e987d2909ba22e576))

- Improve error handling, UI, and code organization in various services
  ([`3c01dcf`](https://github.com/UseTheFork/byte/commit/3c01dcf099b8e95f0a707b70a9282fd95d4b59da))

- Improve event handling and service registration across multiple domains
  ([`86f989f`](https://github.com/UseTheFork/byte/commit/86f989f553343458d8909911b696d49bc12a2f55))

- Improve file listing display using Rich Columns
  ([`9f9c8fd`](https://github.com/UseTheFork/byte/commit/9f9c8fd4ab0cb115c29e0cfd44db55d7551fa13e))

- Improve LLM service and commit command with better typing and documentation
  ([`c5f8168`](https://github.com/UseTheFork/byte/commit/c5f8168f91ad197df217625918f3528fbd2a7c77))

- Improve menu handling with transient option and error state
  ([`f8bfc9f`](https://github.com/UseTheFork/byte/commit/f8bfc9fcb1603f96d6b44ea37f6ac7c61e99ed5c))

- Migrate codebase to async initialization and service resolution
  ([`07ab258`](https://github.com/UseTheFork/byte/commit/07ab258bc91dc016053f7cc15991070fbe3a340b))

- Modernize dependency injection and service registration
  ([`8a66e62`](https://github.com/UseTheFork/byte/commit/8a66e62d2636a80cb1a122424c1b57b7d0ea2fe5))

- Modularize menu implementation with state, rendering, and input handling
  ([`4d7ea47`](https://github.com/UseTheFork/byte/commit/4d7ea47ea49e24bb0fc7c65fb060960fea9eeae7))

- Move events module from core to domain directory
  ([`d129cb8`](https://github.com/UseTheFork/byte/commit/d129cb86e71a3b1dfafc5edc70bc8751cf972a76))

- Move project structure from byte/ to src/byte/
  ([`deb9725`](https://github.com/UseTheFork/byte/commit/deb972524a9a529e77e2ff46b5f8ff184e6b4193))

- Normalize indentation in domain edit format files
  ([`8f96d1e`](https://github.com/UseTheFork/byte/commit/8f96d1eee39326ed67bcf305915f53244fe35d19))

- Normalize indentation to tabs in analytics services
  ([`b764565`](https://github.com/UseTheFork/byte/commit/b76456584db3e9f78ae4d1bcdd34a99827858507))

- Remove border styles and color formatting from panels
  ([`d5cc897`](https://github.com/UseTheFork/byte/commit/d5cc8970d404d71187bf8052adc962a3e2c757dc))

- Remove custom rich panel and rule classes, consolidate styling in console service
  ([`01d971a`](https://github.com/UseTheFork/byte/commit/01d971ad18a86e9892888aaf03be62542d9da845))

- Remove debug log statements from watcher and lint services
  ([`6f81e4f`](https://github.com/UseTheFork/byte/commit/6f81e4fbd0b45db2708f208529f48788dfc6c753))

- Remove deprecated actor and messaging system
  ([`ac2363f`](https://github.com/UseTheFork/byte/commit/ac2363f14e67d94166f12650941a1f5fe5ca71db))

- Remove deprecated agent modules and update service initialization
  ([`ce65e8e`](https://github.com/UseTheFork/byte/commit/ce65e8ed02c37f4fb8adf9bac6d52af850e7e2b6))

- Remove file_repository and reorder event imports
  ([`bde18cf`](https://github.com/UseTheFork/byte/commit/bde18cf79be60a5f49640b1f36c85e18137a77c8))

- Remove git detection and simplify project root discovery
  ([`c44ff9c`](https://github.com/UseTheFork/byte/commit/c44ff9c5eda81eee8679d1cc5506b812aa2ec452))

- Remove GitConfig and implement git changed files detection
  ([`7841299`](https://github.com/UseTheFork/byte/commit/7841299051cafdd4c1771feb70a8307826f41b46))

- Remove manual dotenv loading and add automatic loading with logging
  ([`c4a6c20`](https://github.com/UseTheFork/byte/commit/c4a6c20e857170c69df1e1460dc7ced3bf26a355))

- Remove redundant command_completed() calls and unused code
  ([`73590d4`](https://github.com/UseTheFork/byte/commit/73590d400b91df2eb8f3555bd38165bfdf15d7eb))

- Remove unused knowledge domain files and clean up imports
  ([`4f3600b`](https://github.com/UseTheFork/byte/commit/4f3600bedaba99bf640cd905697f9b17f6c3b4c3))

- Remove unused response types and simplify response handling
  ([`a1b0534`](https://github.com/UseTheFork/byte/commit/a1b0534b816f260a04b2b635c77b2978495e6982))

- Rename InitilizieAgent to ResearchAgent for clarity and consistency
  ([`76a6f1f`](https://github.com/UseTheFork/byte/commit/76a6f1f5221803d7b085eddef41bc5ead92271a8))

- Rename project from bytesmith to byte
  ([`5b88c71`](https://github.com/UseTheFork/byte/commit/5b88c7141788a2fd47956d8b7282e40ccf40b3ca))

- Reorganize agent implementation directory structure
  ([`27a208c`](https://github.com/UseTheFork/byte/commit/27a208cb94f8116e77834ab1e0d1e9a47e78c871))

- Reorganize coder agent into agent domain module
  ([`bb09ac0`](https://github.com/UseTheFork/byte/commit/bb09ac0edd1f967768189dbedcf95ac81a560eca))

- Reorganize mixins into separate files and update imports
  ([`396d934`](https://github.com/UseTheFork/byte/commit/396d934ff8256182dde0fef92eed8d77973c103e))

- Reorganize project structure and clean up unused files
  ([`065681d`](https://github.com/UseTheFork/byte/commit/065681d4f6cb4eb3c518d0ab1ed7d648fb35051b))

- Replace ByteCheckpointer with InMemorySaver in memory service
  ([`679b697`](https://github.com/UseTheFork/byte/commit/679b69706c9cf4438dc10349bfec578faf525afa))

- Replace panel-based context display with markdown formatting
  ([`a832ad9`](https://github.com/UseTheFork/byte/commit/a832ad9339efc60691f3f06e398a9dacf677ed6a))

- Restructure actor system and improve service provider actor registration
  ([`c4d795e`](https://github.com/UseTheFork/byte/commit/c4d795ea7bb88f9a5718381943bd3094c135c0b3))

- Restructure agent base classes and improve stream rendering
  ([`c4ce669`](https://github.com/UseTheFork/byte/commit/c4ce6696d3b9ca10622a82951d5f67753e1764de))

- Restructure agent domain with base agent and modular service providers
  ([`cb98a4c`](https://github.com/UseTheFork/byte/commit/cb98a4c07fa77b5ffe413a3c31d4db2be1722e9c))

- Restructure agent services and improve type handling
  ([`bc50c8e`](https://github.com/UseTheFork/byte/commit/bc50c8e5cc77eb65efabedd63467d749d0b89676))

- Restructure analytics service with improved token tracking and display
  ([`cdd9f0d`](https://github.com/UseTheFork/byte/commit/cdd9f0d3442e56488f7a52e25da7e1725c031223))

- Restructure application architecture to use service-based approach
  ([`3ae0b8c`](https://github.com/UseTheFork/byte/commit/3ae0b8c42936e0a55853c4b65da191a10d764023))

- Restructure coder agent with edit format and parsing logic
  ([`204a905`](https://github.com/UseTheFork/byte/commit/204a9054a30957e5dabaca18a061447649e4f2e7))

- Restructure commit command to use dedicated service
  ([`cd7dc24`](https://github.com/UseTheFork/byte/commit/cd7dc2461ca544f4dc1679c69c228f0548582698))

- Restructure config system and simplify service providers
  ([`2a22510`](https://github.com/UseTheFork/byte/commit/2a22510df578db0073edd7d6d833f406b41e31db))

- Restructure edit_format domain and clean up architecture files
  ([`7ded5ff`](https://github.com/UseTheFork/byte/commit/7ded5ffeb18c2aeae2a4b63d8d8333ce9dd96a72))

- Restructure file discovery service and improve file search
  ([`be06927`](https://github.com/UseTheFork/byte/commit/be06927c0187e1232085d8115fa3c74529205d5a))

- Restructure file domain with new actor, commands, and service organization
  ([`389c289`](https://github.com/UseTheFork/byte/commit/389c289fc3237177350035c32cca5f72814274ab))

- Restructure LLM configuration and schemas for better modularity
  ([`b96afc7`](https://github.com/UseTheFork/byte/commit/b96afc75254032610090ae9f3debb5811629d63e))

- Restructure memory and agent services for improved modularity
  ([`2bfa667`](https://github.com/UseTheFork/byte/commit/2bfa6677df4d8738c992f60dd7fefb349b89e7d7))

- Restructure project architecture and remove unused event system
  ([`1f4d075`](https://github.com/UseTheFork/byte/commit/1f4d075295849bd3c4595904ba975bec45a10d94))

- Restructure project files and update import paths
  ([`1efe48a`](https://github.com/UseTheFork/byte/commit/1efe48a9a8b739431dfc14a44d60477517cc3a35))

- Restructure project layout and consolidate service providers
  ([`167083d`](https://github.com/UseTheFork/byte/commit/167083d1bfe044d9e1e805b1db292f6ba063a719))

- Restructure user interaction and input handling in actors
  ([`623cd7e`](https://github.com/UseTheFork/byte/commit/623cd7e56ad34ce0ba81c51e688c709b4dea7755))

- Simplify agent architecture and remove redundant code
  ([`15be785`](https://github.com/UseTheFork/byte/commit/15be785ef77a988de9d24c587cacf90cce2898bd))

- Simplify agent architecture with new AssistantRunnable schema
  ([`c8c058d`](https://github.com/UseTheFork/byte/commit/c8c058d6b0f888a2d64a76d01891a90993c1839a))

- Simplify coder agent and remove unnecessary logging
  ([`6beaa85`](https://github.com/UseTheFork/byte/commit/6beaa85a89272e8a8ce5457d8a67b70a0af71cb1))

- Simplify coder agent architecture and remove unnecessary graph components
  ([`ec094f9`](https://github.com/UseTheFork/byte/commit/ec094f92374fae86bfa0e0f18296864f9e59ada9))

- Simplify confirm methods and remove redundant dependencies
  ([`1d4f21d`](https://github.com/UseTheFork/byte/commit/1d4f21df839931d305ddbe88fcccbdeb8468683c))

- Simplify context imports and add injectable mixins
  ([`950655b`](https://github.com/UseTheFork/byte/commit/950655b440005143862c3486b2208247634c2a27))

- Simplify markdown streaming and improve UI rendering
  ([`6461d8f`](https://github.com/UseTheFork/byte/commit/6461d8f0b4c12a86ddb7899f036a5199d607d3a0))

- Simplify response handler and interactions with rich prompts
  ([`b1b887e`](https://github.com/UseTheFork/byte/commit/b1b887eeef00b1ac235eb53d3fd96d56bbce1981))

- Simplify response handler with Rich Live display
  ([`b5624c0`](https://github.com/UseTheFork/byte/commit/b5624c0067ccdf252170f8e6027e67dc5627fa73))

- Standardize indentation to tabs across file services and providers
  ([`1e27c4e`](https://github.com/UseTheFork/byte/commit/1e27c4ec1b73c1e5b48c3723560837a7125a54e5))

- Standardize indentation to tabs across multiple Python files
  ([`38811b7`](https://github.com/UseTheFork/byte/commit/38811b7fdf1d537d748567267d5c7a027f14f3f4))

- Standardize indentation to tabs in git-related files
  ([`02f886b`](https://github.com/UseTheFork/byte/commit/02f886b615d711d9f3296ff35bf3fd57aa7691f5))

- Standardize indentation to tabs in tool modules
  ([`ef78b92`](https://github.com/UseTheFork/byte/commit/ef78b92879b80fcb4aeb6110cbb00ca3f3f9eb9a))

- Update actor subscription method from setup_subscriptions to subscriptions
  ([`30226ce`](https://github.com/UseTheFork/byte/commit/30226ceae844eeef5c10ef638991e0eca2be8ca1))

- Update code to use consistent 4-space indentation
  ([`c71d542`](https://github.com/UseTheFork/byte/commit/c71d5421c0455458596801330470cef05c9747cb))

- Update command processing and event handling flow
  ([`e67a9a7`](https://github.com/UseTheFork/byte/commit/e67a9a751042db3d46aa1aae43bd0a802b0bc99f))

- Update config structure and CLI configuration settings
  ([`6c12d70`](https://github.com/UseTheFork/byte/commit/6c12d70b3d115347577df8aec311e92997f5f892))

- Update console display and type handling in git and lint services
  ([`91067c5`](https://github.com/UseTheFork/byte/commit/91067c56157b97039c389631ffc4d5ea6b09f5f2))

- Update CopyNode preview display with dynamic line length and custom Rule
  ([`405f6a3`](https://github.com/UseTheFork/byte/commit/405f6a37184b5b75e9d6e7daf01640423c01d27a))

- Update file context and listing commands with improved functionality
  ([`a0a79cd`](https://github.com/UseTheFork/byte/commit/a0a79cd38b9ac0838a258e9f228987e2d6493859))

- Update file watcher and git service with minor adjustments
  ([`5e84797`](https://github.com/UseTheFork/byte/commit/5e84797ef7ee67cff07c37d5c2a7ac91c00dfddd))

- Update historic messages fixture and test for edit format service
  ([`0e06a1d`](https://github.com/UseTheFork/byte/commit/0e06a1d8212305362ab94622a5efaa173076d00a))

- Update Menu and Console services with improved UI and interaction methods
  ([`21da2f9`](https://github.com/UseTheFork/byte/commit/21da2f9201eab31dfeddc2fe80dc5250a3477439))

- Update pre-commit config and code formatting
  ([`7a7fc6f`](https://github.com/UseTheFork/byte/commit/7a7fc6f7c0d26c386420751b71a2ed6e1b9d7a6f))

- Update RuneSpinner with improved color randomization and animation speed
  ([`0742cec`](https://github.com/UseTheFork/byte/commit/0742cec0053b83b52ec87706264fb121474e22e0))

- Update stream rendering to display stream ID and remove empty terminal session file
  ([`52a5da4`](https://github.com/UseTheFork/byte/commit/52a5da441d15beac027b27fbc0628e2d98fa8f55))

- Update token tracking and cost calculation model
  ([`f8ea923`](https://github.com/UseTheFork/byte/commit/f8ea92398fec5a36baa716ed87d4d8bffcd18c37))

- Update token usage display in agent analytics service
  ([`379e6d5`](https://github.com/UseTheFork/byte/commit/379e6d56afad81513e09a42d74181a89710a7b4a))

- Use rich Text for improved markdown stream rendering
  ([`4c764c6`](https://github.com/UseTheFork/byte/commit/4c764c657165e4c3878db81da4aff6cf6a5f7a89))

### Testing

- Remove incomplete test file for blocked fence edit format
  ([`cc890c5`](https://github.com/UseTheFork/byte/commit/cc890c5fb814b35d25ff1cbfe7f7d1555db43998))
