from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate

coder_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """# Task
Act as an expert code analyst.

Answer questions about the supplied code.

If you need to describe code changes, do so *briefly*.

## Current Context:
Current date: {time}
            """,
        ),
        ("placeholder", "{messages}"),
        ("user", "{file_context}"),
    ]
).partial(time=datetime.now().strftime("%Y-%m-%d"))


# From https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/watch_prompts.py#L6
watch_prompt = """Find the "AI" comments below in the code files I've shared with you.
They contain my questions that I need you to answer and other instructions for you."""

# You can see the "AI" comments shown below (marked with █).
