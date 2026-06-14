from byte.orchestration import PromptAssembler
from byte.orchestration.leaves.leaf import Leaf
from byte.support import MD, Section, SectionType


class DocumentationGuidelines(Leaf):
    """Render documentation framework and style guidelines for the agent."""

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:

        config = prompt_assembler.get_app()["config"]
        documentation_guidelines = []

        documentation_guidelines.append(Section.start(SectionType.RULES))
        documentation_guidelines.append(Section.sub_heading("Documentation Framework", 2, True))

        documentation_guidelines.append(MD.bullet(f"Framework: **{config.documentation.framework}**"))

        documentation_guidelines.append(Section.sub_heading("Feature Flags", 2))

        feature_flags = []
        if config.documentation.enable_mermaid:
            feature_flags.append(MD.bullet("Mermaid diagrams are **enabled**"))
        else:
            feature_flags.append(MD.bullet("Mermaid diagrams are **disabled**"))

        documentation_guidelines.append("\n".join(feature_flags))

        documentation_guidelines.append(Section.sub_heading("Additional Guidelines", 2))

        if config.documentation.extra_guidelines:
            guidelines_list = "\n".join(MD.bullet(guideline) for guideline in config.documentation.extra_guidelines)
            documentation_guidelines.append(guidelines_list)
        else:
            documentation_guidelines.append(MD.bullet("No additional guidelines configured"))

        style = config.documentation.style.lower()

        if style == "diataxis":
            guidelines = [
                Section.sub_heading("Documentation Structure (Diátaxis Framework)", 2),
                "Structure documentation following the Diátaxis framework with four distinct categories:",
                MD.bullet("**Tutorials**: Learning-oriented, hands-on guides that teach concepts through practice"),
                MD.bullet(
                    "**How-to Guides**: Task-oriented, step-by-step instructions for accomplishing specific goals"
                ),
                MD.bullet(
                    "**Explanation**: Understanding-oriented, conceptual discussions providing context and theory"
                ),
                MD.bullet("**Reference**: Information-oriented, lookup material like API docs and configuration specs"),
                "Each documentation page should clearly belong to exactly one of these categories.",
            ]
        elif style == "google":
            guidelines = [
                Section.sub_heading("Documentation Style (Google Developer Documentation Style Guide)", 2),
                "Follow Google Developer Documentation Style Guide conventions:",
                MD.bullet("Use second person ('you') to address the reader directly"),
                MD.bullet("Maintain task-oriented, action-focused language"),
                MD.bullet("Use clear, descriptive headings that preview content"),
                MD.bullet("Keep sentences short and scannable (aim for <25 words per sentence)"),
                MD.bullet("Use active voice and imperative mood when appropriate"),
                MD.bullet("Break complex topics into small, digestible sections"),
            ]
        elif style == "microsoft":
            guidelines = [
                Section.sub_heading("Documentation Style (Microsoft Writing Style Guide)", 2),
                "Follow Microsoft Writing Style Guide conventions:",
                MD.bullet("Use conversational but professional tone"),
                MD.bullet("Focus on action-oriented, task-based content"),
                MD.bullet("Prioritize accessibility: clear language, good contrast, descriptive links"),
                MD.bullet("Use second person ('you') to engage readers"),
                MD.bullet("Avoid jargon; explain technical terms where necessary"),
                MD.bullet("Use lists and formatting to improve scannability"),
            ]
        elif style == "minimal":
            guidelines = [
                Section.sub_heading("Documentation Style (Minimal/Reference)", 2),
                "Prioritize brevity and scannability in a minimal style:",
                MD.bullet("Reduce prose to the absolute minimum necessary"),
                MD.bullet("Focus on reference material: code examples, API specs, configuration"),
                MD.bullet("Use concise section headers and bullet points"),
                MD.bullet("Avoid explanatory prose padding unless essential for clarity"),
                MD.bullet("Optimize for quick lookup and copy-paste utility"),
            ]
        else:
            guidelines = [
                Section.sub_heading(f"Documentation Style ({style})", 2),
                f"Using configured documentation style: '{style}'",
                "No specific guidance available for this style; follow general documentation best practices.",
            ]

        documentation_guidelines.extend(guidelines)

        return MD.list_to_text(documentation_guidelines)
