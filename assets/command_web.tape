Source assets/_config.tape
Source assets/_boot.tape

Wait+Screen       /╭─ Analytics/
Sleep 2s

Type "/web https://pydoll.tech/docs/"
Sleep 500ms
Enter

Wait+Line       /Add this content to the LLM context/
Sleep 1s
Down 1
Sleep 2s
Up 1
Sleep 2s
Enter

Wait+Screen@30s       /╭─ Analytics/
Sleep 2s


Output docs/images/recording/command_web.gif
