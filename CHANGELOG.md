# CHANGELOG


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
