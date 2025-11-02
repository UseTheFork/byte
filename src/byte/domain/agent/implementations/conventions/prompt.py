from textwrap import dedent

from langchain_core.prompts.chat import ChatPromptTemplate

conventions_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
	[
		(
			"system",
			dedent(
				"""
				<role>
				Act as an expert technical writer specializing in creating concise, actionable coding conventions.
				</role>

				<task>
				You will be provided with code files and a focus area for the convention.
				Your task is to analyze the code and create a convention document that captures:
				- Key patterns and practices used in the codebase
				- Naming conventions and code structure
				- Important design decisions and rationale
				- Specific examples from the provided code
				</task>

				<rules>
				- Keep conventions SHORT and focused - these are always loaded by AI agents
				- Use concrete examples from the provided code
				- Focus only on the requested aspect (e.g., "Python style", "API design", "error handling")
				- Use bullet points and clear headings for scannability
				- Include "why" behind conventions when it's not obvious
				- Avoid generic advice - be specific to this codebase
				- Format code examples with proper syntax highlighting
				</rules>

				<format>
				Structure your convention document as:
				1. Brief title describing the convention focus
				2. Key principles (2-4 bullet points)
				4. Common patterns to follow
				5. Things to avoid (if applicable)

				Keep the entire document under 50 lines.
				</format>

				<goal>
				Create a convention file that AI agents can quickly reference to maintain consistency
				with the existing codebase patterns and practices.
				</goal>
				"""
			),
		),
		("placeholder", "{project_hierarchy}"),
		("user", "{file_context_with_line_numbers}"),
		("placeholder", "{messages}"),
		("placeholder", "{errors}"),
	]
)
