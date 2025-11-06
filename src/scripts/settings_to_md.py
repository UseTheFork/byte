from pathlib import Path
from typing import Any, Dict

from byte.core.config.config import ByteConfg


def format_type(type_info: Any) -> str:
    """Format type information into a readable string.

    Usage: `format_type({"type": "string"})` -> "string"
    Usage: `format_type({"type": "array", "items": {"type": "string"}})` -> "array[string]"
    Usage: `format_type({"enum": ["a", "b"]})` -> "a, b"
    """
    if isinstance(type_info, dict):
        if "enum" in type_info:
            # Handle Literal types - use commas to avoid breaking table format
            return ", ".join(type_info["enum"])
        elif "type" in type_info:
            base_type = type_info["type"]
            if base_type == "array" and "items" in type_info:
                item_type = format_type(type_info["items"])
                return f"array[{item_type}]"
            return base_type
        elif "anyOf" in type_info:
            types = [format_type(t) for t in type_info["anyOf"]]
            return " | ".join(types)
        elif "$ref" in type_info:
            # Extract just the model name from the reference
            return type_info["$ref"].split("/")[-1]
    return str(type_info)


def format_default(default: Any) -> str:
    """Format default value for markdown display.

    Usage: `format_default(True)` -> "`true`"
    Usage: `format_default([])` -> "`[]`"
    """
    if default is None or default == "":
        return "-"
    if isinstance(default, bool):
        return f"`{str(default).lower()}`"
    if isinstance(default, list | dict):
        if not default:
            return f"`{default}`"
        return f"`{default}`"
    return f"`{default}`"


def get_nested_properties(schema: Dict[str, Any], ref_key: str) -> Dict[str, Any]:
    """Extract nested properties from schema definitions.

    Usage: `get_nested_properties(schema, "CLIConfig")` -> dict of CLI config properties
    """
    if "$defs" in schema and ref_key in schema["$defs"]:
        return schema["$defs"][ref_key].get("properties", {})
    return {}


def get_all_nested_configs(schema: Dict[str, Any], properties: Dict[str, Any]) -> list[tuple[str, Dict[str, Any]]]:
    """Recursively find all nested configuration objects.

    Returns a list of tuples containing (section_name, properties_dict) for each
    nested config found within the given properties. Also handles nested models
    within arrays (e.g., array[LintCommand]).

    Usage: `get_all_nested_configs(schema, props)` -> [("Provider: Anthropic", {...}), ...]
    """
    nested_configs = []

    for field_name, prop in properties.items():
        # Check for direct $ref
        if "$ref" in prop:
            ref_key = prop["$ref"].split("/")[-1]
            nested_props = get_nested_properties(schema, ref_key)

            if nested_props:
                # Create a readable section name
                section_name = field_name.replace("_", " ").title()
                nested_configs.append((section_name, nested_props))

        # Check for array with nested BaseModel items
        elif prop.get("type") == "array" and "items" in prop:
            items = prop["items"]
            if "$ref" in items:
                ref_key = items["$ref"].split("/")[-1]
                nested_props = get_nested_properties(schema, ref_key)

                if nested_props:
                    # Create a readable section name for the array item type
                    section_name = ref_key.replace("Config", "").replace("_", " ")
                    nested_configs.append((section_name, nested_props))

    return nested_configs


def create_section_table(
    section_name: str, properties: Dict[str, Any], exclude_nested: bool = False, description: str = ""
) -> str:
    """Create a markdown table for a configuration section.

    Args:
            section_name: Display name for the configuration section
            properties: Dictionary of property definitions from schema
            exclude_nested: If True, skip fields that are direct $ref objects (but keep arrays)
            description: Optional description text to display under the section name

    Usage: `create_section_table("CLI", {"key": {...}})` -> markdown table string
    """
    lines = [
        f"## {section_name}",
        "",
    ]

    if description:
        lines.append(description)
        lines.append("")

    lines.extend(
        [
            "| Field | Type | Default | Description |",
            "|-------|------|---------|-------------|",
        ]
    )

    for field_name, prop in properties.items():
        # Skip nested config objects if exclude_nested is True (but keep arrays)
        if exclude_nested and "$ref" in prop:
            continue

        field_type = format_type(prop)
        description = prop.get("description", "").replace("\n", " ")
        default = format_default(prop.get("default"))

        lines.append(f"| `{field_name}` | `{field_type}` | {default} | {description} |")

    lines.append("")
    return "\n".join(lines)


def schema_to_markdown(schema: Dict[str, Any]) -> str:
    """Convert ByteConfg schema to markdown documentation.

    Creates separate tables for each configuration section (cli, llm, files, etc).
    Recursively processes nested configs like LLMProviderConfig.
    Excludes internal fields marked with exclude=True.

    Usage: `schema_to_markdown(ByteConfg.model_json_schema())` -> full markdown string
    """
    sections = []

    # Add header
    sections.append("# Byte Configuration Settings")
    sections.append("")
    sections.append(
        "Byte's configuration system uses a YAML file located at `.byte/config.yaml` to control all aspects of the application's behavior. Configuration is organized into logical sections covering CLI behavior, LLM providers, file handling, and feature-specific settings."
    )
    sections.append("")
    sections.append("---")
    sections.append("")

    # Process each top-level property that's not excluded
    for field_name, prop in schema.get("properties", {}).items():
        # Skip excluded fields (development and system are marked with exclude=True)
        if prop.get("exclude", False):
            continue

        if field_name == "development" or field_name == "system":
            continue

        # Skip if field doesn't have a $ref (not a nested config object)
        if "$ref" not in prop:
            continue

        # Extract the reference key (e.g., "CLIConfig")
        ref_key = prop["$ref"].split("/")[-1]

        # Get the nested properties for this section
        nested_props = get_nested_properties(schema, ref_key)

        if nested_props:
            # Create section name from field name (e.g., "cli" -> "CLI")
            section_name = field_name.title()

            # Get the description for this section from the schema definition
            section_description = prop.get("description", "")

            # Check for sub-configs within this section (e.g., LLMProviderConfig within LLMConfig)
            sub_configs = get_all_nested_configs(schema, nested_props)
            has_nested = len(sub_configs) > 0

            # Create main section table, excluding nested configs if any exist
            sections.append(
                create_section_table(
                    section_name, nested_props, exclude_nested=has_nested, description=section_description
                )
            )

            # Create separate tables for each sub-config
            for sub_name, sub_props in sub_configs:
                # Create nested section header (e.g., "LLM > Anthropic")
                full_section_name = f"{section_name} > {sub_name}"
                sections.append(create_section_table(full_section_name, sub_props, exclude_nested=False))

    return "\n".join(sections)


def main():
    """Generate settings documentation and write to docs/settings.md.

    Usage: `python src/scripts/settings_to_md.py`
    """
    schema = ByteConfg.model_json_schema()
    markdown = schema_to_markdown(schema)

    # Write to docs/settings.md
    docs_dir = Path(__file__).parent.parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)

    output_file = docs_dir / "reference" / "settings.md"
    output_file.write_text(markdown, encoding="utf-8")

    print(f"Settings documentation written to {output_file}")


if __name__ == "__main__":
    main()
