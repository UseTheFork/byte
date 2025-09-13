[private]
[doc('Display the list of recipes')]
default:
  @just --list


[group('Aider')]
[doc('General')]
ai:
		aider \
		--no-show-release-notes \
		--model sonnet \
		--watch-files \
		--no-detect-urls \
		--git-commit-verify \
		--read .byte/conventions/COMMENT_STYLEGUIDE.md \
		--lint-cmd "just lint" \
		--add-gitignore-files
