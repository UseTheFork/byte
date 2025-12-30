# Commit type definitions with descriptions
COMMIT_TYPES = {
    "feat": "Commits that add or remove a new feature to the API or UI",
    "fix": "Commits that fix an API or UI bug of a preceded feat commit",
    "refactor": "Commits that rewrite/restructure code without changing API or UI behaviour",
    "perf": "Commits that improve performance (special refactor commits)",
    "style": "Commits that do not affect meaning (white-space, formatting, missing semi-colons, etc)",
    "test": "Commits that add missing tests or correct existing tests",
    "build": "Commits that affect build components (build tool, CI pipeline, dependencies, project version, etc)",
    "ops": "Commits that affect operational components (infrastructure, deployment, backup, recovery, etc)",
    "docs": "Commits that affect documentation only",
    "chore": "Commits that represent tasks (initial commit, modifying .gitignore, etc)",
}

# Simple list for prompts (most common use case)
COMMIT_TYPE_LIST = ", ".join(COMMIT_TYPES.keys())

# Guidelines as constants
COMMIT_GUIDELINES = [
    "Starts with the appropriate prefix.",
    'Is in the imperative mood (e.g., "add feature" not "added feature" or "adding feature").',
    "Does not exceed 72 characters.",
]
