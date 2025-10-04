{
  lib,
  self,
  stdenv,
  buildPythonPackage,
  gitMinimal,
  pythonOlder,
  pythonAtLeast,
  # Build system
  uv-build,
  # Runtime dependencies
  aiosqlite,
  beautifulsoup4,
  click,
  gitpython,
  # langchain-mcp-adapters,
  langchain,
  langchain-core,
  langchain-anthropic,
  langchain-google-genai,
  langchain-openai,
  langgraph,
  langgraph-checkpoint-sqlite,
  markdownify,
  pathspec,
  prompt-toolkit,
  pydantic,
  pydantic-settings,
  # pydoll-python,
  python-dotenv,
  pyyaml,
  rich,
  watchfiles,
  # Test dependencies
  pytestCheckHook,
  callPackage,

}:
let
  version = "0.0.1";
  byte = buildPythonPackage {
    pname = "byte";
    inherit version;
    pyproject = true;

    # disabled = pythonOlder "3.10" || pythonAtLeast "3.13";

    src = ./.;

    pythonRelaxDeps = true;

    # build-system = [ setuptools-scm ];
    build-system = [ uv-build ];

    dependencies = [
      aiosqlite
      beautifulsoup4
      click
      gitpython
      (callPackage ./flake/python/langchain-mcp-adapters.nix { inherit self; })
      (callPackage ./flake/python/pydoll-python.nix { inherit self; })
      langchain
      langchain-core
      langchain-anthropic
      langchain-google-genai
      langchain-openai
      langgraph
      langgraph-checkpoint-sqlite
      markdownify
      pathspec
      prompt-toolkit
      pydantic
      pydantic-settings
      python-dotenv
      pyyaml
      rich
      watchfiles
    ];

    buildInputs = [ ];

    nativeCheckInputs = [
      pytestCheckHook
      gitMinimal
    ];

    # postPatch = ''
    #   substituteInPlace aider/linter.py --replace-fail "\"flake8\"" "\"${flake8}\""
    # '';

    # disabledTestPaths = [
    #   # Tests require network access
    #   "tests/scrape/test_scrape.py"
    #   # Expected 'mock' to have been called once
    #   "tests/help/test_help.py"
    # ];

    doCheck = false; # YOLO

    # makeWrapperArgs = [
    #   "--set"
    #   "AIDER_CHECK_UPDATE"
    #   "false"
    #   "--set"
    #   "AIDER_ANALYTICS"
    #   "false"
    #   "--set"
    #   "PLAYWRIGHT_BROWSERS_PATH"
    #   "${playwright-driver.browsers}"
    #   "--set"
    #   "PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS"
    #   "true"
    # ];

    preCheck = ''
      export HOME=$(mktemp -d)
    '';

    # propagatedBuildInputs = [ playwright-driver.browsers ];

    meta = {
      description = "AI pair programming in your terminal";
      homepage = "https://github.com/paul-gauthier/aider";
      changelog = "https://github.com/paul-gauthier/aider/blob/v${version}/HISTORY.md";
      license = lib.licenses.asl20;
      maintainers = with lib.maintainers; [
        UseTheFork
      ];
      mainProgram = "byte";
    };
  };
in
byte
