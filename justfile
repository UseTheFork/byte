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
		--read .byte/conventions/PYTHON_STYLEGUIDE.md \
		--file byte/bootstrap.py \
		--file byte/container.py \
		--file byte/main.py \
		--file byte/core/actors/base.py \
		--file byte/core/actors/message.py \
		--file byte/core/actors/streams.py \
		--lint-cmd "just lint" \
		--add-gitignore-files

[doc('Lint files')]
lint files:
		pre-commit run --files {{files}}
