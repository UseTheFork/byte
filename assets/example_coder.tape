Source assets/_config.tape
Source assets/_boot.tape

Wait+Screen       /╭─ Analytics/
Sleep 2s

Type "/add main."
Sleep 500ms
Tab
Enter
Sleep 1s

Type "complete the doc block for the `cli` method"
Enter
Wait+Screen@30s       /╭─ Analytics/
Sleep 3s

Output docs/images/recording/example_coder.gif
