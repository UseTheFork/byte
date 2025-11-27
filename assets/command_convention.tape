Source assets/_config.tape
Source assets/_boot.tape

Wait+Line       />/
Sleep 2s

Type "/conv"
Sleep 500ms
Down
Sleep 500ms
Enter

Wait+Line@60s       /╰────────/
Sleep 1s
Up 1
Sleep 2s
Down 1
Sleep 4s
Enter

Wait+Line@60s       /╰────────/
Sleep 1s
Enter
Sleep 2s

Wait+Line@60s       /╰────────/
Sleep 1s
Enter
Sleep 2s

Wait+Line@120s       />/
Sleep 2s

Output docs/images/recording/command_convention.gif
