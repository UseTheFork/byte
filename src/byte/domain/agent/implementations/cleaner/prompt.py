from langchain_core.prompts.chat import ChatPromptTemplate

# Content cleaning prompt for extracting relevant information
cleaner_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "# Task\n"
            "You are an expert at extracting relevant information from content.\n"
            "Your goal is to identify and preserve only the essential information while removing noise, redundancy, and irrelevant details.\n\n"
            "# Guidelines\n"
            "- Focus on key concepts, facts, and actionable information\n"
            "- Remove boilerplate, excessive formatting, and repetitive content\n"
            "- Preserve important context and relationships between ideas\n"
            "- Maintain clarity and coherence in the extracted information\n"
            "- Use concise language while keeping all critical details\n\n"
            "# Output Requirements\n"
            "Return only the cleaned, relevant content without explanations or meta-commentary.\n"
            "Organize the information in a clear, structured format if appropriate.",
        ),
        ("placeholder", "{messages}"),
    ]
)
