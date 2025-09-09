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
		--read CONVENTIONS-FRONTEND.MD \
		--read CONVENTIONS-BACKEND.MD \
		--lint-cmd "just lint" \
		--add-gitignore-files


[group('Aider')]
[doc('with Backend conventions')]
ai-back:
		aider \
		--no-show-release-notes \
		--model claude-opus-4-20250514 \
		--watch-files \
		--no-suggest-shell-commands \
		--no-detect-urls \
		--git-commit-verify \
		--read CONVENTIONS-BACKEND.MD \
		--lint-cmd "just lint" \
		--input-history-file ./.aider.backend.input.history \
		--chat-history-file  ./.aider.backend.chat.history.md \
		--llm-history-file .aider.backend.llm.history \
		--add-gitignore-files \
		--aiderignore .aiderignore.backend

##		--model gemini \
##		--model anthropic/claude-3-5-sonnet-20241022 \
#		--model gemini/gemini-2.5-pro-preview-06-05 --thinking-tokens 32k \

[group('Aider')]
[doc('with Frontend conventions')]
ai-front:
		aider \
		--no-show-release-notes \
		--model claude-opus-4-20250514 \
		--watch-files \
		--no-suggest-shell-commands \
		--no-detect-urls \
		--git-commit-verify \
		--read CONVENTIONS-FRONTEND.MD \
		--lint-cmd "just lint" \
		--input-history-file ./.aider.frontend.input.history \
		--chat-history-file  ./.aider.frontend.chat.history.md \
		--llm-history-file .aider.frontend.llm.history \
		--add-gitignore-files \
		--aiderignore .aiderignore.frontend

[doc('Startes All Services')]
up:
		process-compose up -t

[doc('Lint files')]
lint files:
		pre-commit run --files {{files}}


[group('Laravel')]
[doc('run artisan command')]
[positional-arguments]
a argument:
		php artisan "$1"

[group('Laravel')]
[confirm]
[doc('Rollback last Migration')]
rollback:
		php artisan migrate:rollback

[group('Laravel')]
[doc('Run Migrations')]
migrate:
		php artisan migrate

[group('Laravel')]
[doc('List Routes')]
routes:
		php artisan route:list

[group('Laravel')]
[doc('List schedule')]
schedule:
		php artisan schedule:list

[doc('Loads database from production')]
load:
		php artisan run:migrate-rider
		php artisan run:migrate-dish
		php artisan run:migrate-clients
		php artisan run:migrate-menu
		php artisan run:migrate-route-address


mariadb:
	docker compose -f "./docker-compose.yml" run --rm mariadb mariadb

# --model sonnet \


[group('CI')]
[doc('Run NPM and dploy result to prod')]
deploy:
		#!/bin/sh

		git push

		# Run deployment script on server
		ssh -i ~/.ssh/id_ed25519 sincorea@70.32.23.118 "cd /home/sincorea/sysadmin.rubabsexpress.com && ./bin/deploy.sh"

		# Build
		npm run build

		# Sync files (faster than SFTP for multiple files)
		rsync -avz --delete -e "ssh -i ~/.ssh/id_ed25519" \
		public/build/ sincorea@70.32.23.118:/home/sincorea/sysadmin.rubabsexpress.com/public/build

[group('CI')]
[doc('Pull CCCI files from server (add new files only)')]
pull-ccci:
		#!/bin/sh

		# Pull CCCI files from server without deleting local files
		rsync -avz -e "ssh -i ~/.ssh/id_ed25519" \
		sincorea@70.32.23.118:/home/sincorea/sysadmin.rubabsexpress.com/storage/app/ccci/ storage/app/ccci/

[group('CI')]
[doc('Pull Trade files from server (add new files only)')]
pull-trade:
		#!/bin/sh

		# Pull CCCI files from server without deleting local files
		rsync -avz -e "ssh -i ~/.ssh/id_ed25519" \
		sincorea@70.32.23.118:/home/sincorea/sysadmin.rubabsexpress.com/storage/app/trade-files/ storage/app/trade-files/

[group('CI')]
[doc('Pull logs from server (empty local directory first)')]
pull-logs:
		#!/bin/sh

		# Empty the local logs directory first
		rm -rf storage/logs/*

		# Pull logs from server
		rsync -avz -e "ssh -i ~/.ssh/id_ed25519" \
		sincorea@70.32.23.118:/home/sincorea/sysadmin.rubabsexpress.com/storage/logs/ storage/logs/
