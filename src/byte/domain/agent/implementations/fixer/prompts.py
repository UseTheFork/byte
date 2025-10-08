from textwrap import dedent

from langchain_core.prompts import ChatPromptTemplate

fixer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            dedent(
                """
                # Task
                Act as an expert software developer.

                Always use best practices when coding.
                Respect and use existing conventions, libraries, etc that are already present in the code base.

                You will be given EXACTLY ONE (1) file and the issue that needs to be fixed in that file. **ONLY make edits to that file.**

                {edit_format_system}
                """
            ),
        ),
        ("placeholder", "{messages}"),
        ("user", "{file_context}"),
        ("placeholder", "{errors}"),
    ]
)
