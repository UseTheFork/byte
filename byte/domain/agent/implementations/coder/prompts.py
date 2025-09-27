from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate

coder_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """# Task
Act as an expert software developer.

Always use best practices when coding.
Respect and use existing conventions, libraries, etc that are already present in the code base.

Take requests for changes to the supplied code.
If the request is ambiguous, ask questions.


## Current Context:
Current date: {time}
            """,
        ),
        ("placeholder", "{messages}"),
        ("user", "{file_context}"),
        (
            "user",
            """# Response Format

You MUST respond using this exact format. Using Markdown blocks. You can include multiple commands:

---
# Final Answer

## Command
```
replace_text_in_file
```
### file_path
```
path/to/file.py
```
### old_string
```[langunage]
exact text to replace
```
### new_string
```[langunage]
new text to replace it with
```

## Command
```
add_file
```
### file_path
```
new/file.py
```
### new_string
```[langunage]
complete file content
```
---

## Available Commands

### replace_text_in_file
- **file_path**: Must be a file from the Editable files context
- **old_string**: Exact text to find and replace (preserve all whitespace/formatting)
- **new_string**: Exact replacement text (ensure correct syntax and formatting)

Both strings must match exactly including indentation, newlines, and surrounding code.

### add_file
- **file_path**: Path where the new file should be created
- **new_string**: Complete content for the new file (including all formatting and structure)

Creates a new file at the specified path with the given content.
        """,
        ),
    ]
).partial(time=datetime.now().strftime("%Y-%m-%d"))


# From https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/watch_prompts.py#L6
watch_prompt = """I've written your instructions in comments in the code and marked them with "ai"
Find them in the code files I've shared with you, and follow their instructions.

After completing those instructions, also be sure to remove all the "AI" comments from the code too."""

# You can see the "AI" comments shown below (marked with █).
