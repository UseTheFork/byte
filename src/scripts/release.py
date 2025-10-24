# todo:

# Update Commands in documentation
# uv run python src/scripts/commands_to_md.py

# Update settings in documentation
# uv run python src/scripts/settings_to_md.py

# Commit here with somekind of default message.

# get the version based on git cliff
# git cliff --bump --context | jq -r .[0].version
# Generates somthing like `v0.2.0`

# Then add the version
# git tag {version}

# Update the changelog
# git-cliff --tag {version} -o

# Update uv version
# uv version {version}

# finally
# git push --tags
