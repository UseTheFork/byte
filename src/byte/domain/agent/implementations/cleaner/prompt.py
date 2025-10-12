from textwrap import dedent

from langchain_core.prompts.chat import ChatPromptTemplate

cleaner_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
	[
		(
			"system",
			dedent(
				"""
				# Task
				You are an expert at extracting relevant information from content.
				Your goal is to identify and preserve only the essential information while removing noise, redundancy, and irrelevant details.

				# Guidelines
				- Focus on key concepts, facts, and actionable information
				- Remove boilerplate, excessive formatting, and repetitive content
				- Preserve important context and relationships between ideas
				- Maintain clarity and coherence in the extracted information
				- Use concise language while keeping all critical details

				# Output Requirements
				Return only the cleaned, relevant content without explanations or meta-commentary.
				Organize the information in a clear, structured format if appropriate.
				"""
			),
		),
		("placeholder", "{messages}"),
	]
)
