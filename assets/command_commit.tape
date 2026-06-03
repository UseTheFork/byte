Source assets/_config.tape
Source assets/_boot.tape

Wait+Screen       /╭─ Analytics/
Sleep 2s

Type "/comm"
Sleep 500ms
Tab
Sleep 500ms
Enter

Wait+Screen       /Add unstaged and untracked/
Sleep 500ms
Enter

Wait+Screen       /Approve Commit/
Sleep 500ms
Enter

Wait+Screen       /╭─ Analytics/
Sleep 3s

Output docs/images/recording/command_commit.gif
