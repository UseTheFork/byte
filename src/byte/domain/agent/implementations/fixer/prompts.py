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

				# Guidelines
				- Always use best practices when coding
				- Respect and use existing conventions, libraries, etc that are already present in the code base
				- Take requests for changes to the supplied code
				- If the request is ambiguous, ask clarifying questions before proceeding
				- Keep changes simple don't build more then what is asked for

				# Output Requirements
				{edit_format_system}
				"""
			),
		),
		("placeholder", "{examples}"),
		("placeholder", "{messages}"),
		("placeholder", "{errors}"),
	]
)
