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
    ]
).partial(time=datetime.now().strftime("%Y-%m-%d"))
