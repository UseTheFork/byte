from datetime import datetime
from textwrap import dedent

from langchain_core.prompts import ChatPromptTemplate

coder_prompt = ChatPromptTemplate.from_messages(
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
        ("placeholder", "{examples}"),
        (
            "user",
            dedent("""
            ## Current Context:
            Current date: {time}
            """),
        ),
        ("placeholder", "{messages}"),
        ("user", "{file_context}"),
        ("placeholder", "{errors}"),
    ]
).partial(time=datetime.now().strftime("%Y-%m-%d"))


# From https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/watch_prompts.py#L6
watch_prompt = """I've written your instructions in comments in the code and marked them with "ai"
Find them in the code files I've shared with you, and follow their instructions.

After completing those instructions, also be sure to remove all the "AI" comments from the code too."""

# You can see the "AI" comments shown below (marked with █).
