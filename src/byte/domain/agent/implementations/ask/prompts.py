from datetime import datetime
from textwrap import dedent

from langchain_core.prompts import ChatPromptTemplate

ask_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            dedent("""
            # Task
            Act as an expert software developer.

            Always use best practices when coding.
            Respect and use existing conventions, libraries, etc that are already present in the code base.

            Take requests for changes to the supplied code.
            If the request is ambiguous, ask questions.

            {edit_format_system}
            """),
        ),
        (
            "user",
            dedent("""
            ## Current Context:
            Current date: {time}
            """),
        ),
        ("placeholder", "{messages}"),
        ("user", "{file_context}"),
    ]
).partial(time=datetime.now().strftime("%Y-%m-%d"))
