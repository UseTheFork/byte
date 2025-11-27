Source assets/_config.tape
Source assets/_boot.tape

Wait+Line       />/
Sleep 2s

Type "/add main."
Sleep 500ms
Down
Sleep 500ms
Enter
Sleep 1s

Wait+Line       />/
Type "complete the doc block for the `run` method"
Enter
Wait+Line@20s      />/
Sleep 3s

Output docs/images/recording/example_coder.gif
