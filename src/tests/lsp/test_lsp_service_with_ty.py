"""Test suite for LSPService with Ty LSP server running."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide LSPServiceProvider for LSP service tests."""
    from byte.lsp import LSPServiceProvider

    return [LSPServiceProvider]


@pytest.fixture
def config():
    """Create a ByteConfig instance with Ty LSP enabled."""
    from byte.config import ByteConfig
    from byte.lsp import PresetServerConfig

    config = ByteConfig()
    config.lsp.enable = True
    config.lsp.servers = {"python": PresetServerConfig(preset="ty", server_type="container")}
    return config


@pytest_asyncio.fixture
async def lsp_service(application: Application):
    """Create and start LSP service with Ty, reused across tests."""
    from byte.lsp import LSPService

    lsp_service = application.make(LSPService)

    # Wait for the LSP client to be ready
    import asyncio

    max_wait = 10  # Maximum wait time in seconds
    wait_interval = 0.2  # Check every 0.2 seconds

    for _ in range(int(max_wait / wait_interval)):
        if "python" in lsp_service.clients and lsp_service.clients["python"] is not None:
            break
        await asyncio.sleep(wait_interval)
    else:
        pytest.fail("LSP service failed to start within timeout")

    yield lsp_service

    # Cleanup after all tests
    await lsp_service.shutdown_all()


@pytest.mark.asyncio
async def test_starts_ty_preset_client(lsp_service):
    """Test that LSP service can start a Ty preset client."""
    # Verify language map was built
    assert "python" in lsp_service.language_map
    assert lsp_service.language_map["python"] == "python"

    # Verify client was created
    assert "python" in lsp_service.clients
    assert lsp_service.clients["python"] is not None


@pytest.mark.asyncio
async def test_get_hover_for_python_file(application: Application, lsp_service):
    """Test that LSP service can get hover information for a Python file."""
    from pathlib import Path

    # Create a test Python file with a simple function
    test_file = application.base_path("test_hover.py")
    test_file.write_text("def hello():\n    pass\n")

    # Get hover info for the function name
    hover_result = await lsp_service.get_hover(Path(test_file), line=0, character=4)

    # Should get hover information
    assert hover_result is not None
    assert hover_result.contents is not None
    assert len(hover_result.contents) > 0


@pytest.mark.asyncio
async def test_find_references_for_python_file(application: Application, lsp_service):
    """Test that LSP service can find references for a Python symbol."""
    from pathlib import Path

    # Create a test Python file with a function and its usage
    test_file = application.base_path("test_references.py")
    test_file.write_text("def greet():\n    pass\n\ngreet()\ngreet()\n")

    # Find references to the function name at its definition
    references = await lsp_service.find_references(Path(test_file), line=0, character=4)

    # Should find references (definition + 2 calls = 3 total)
    assert references is not None
    assert isinstance(references, list)
    assert len(references) >= 2  # At least the two calls


@pytest.mark.asyncio
async def test_goto_definition_for_python_file(application: Application, lsp_service):
    """Test that LSP service can go to definition for a Python symbol."""
    from pathlib import Path

    # Create a test Python file with a function and its usage
    test_file = application.base_path("test_definition.py")
    test_file.write_text("def greet():\n    pass\n\ngreet()\n")

    # Go to definition from the function call
    definitions = await lsp_service.goto_definition(Path(test_file), line=3, character=0)

    # Should find the definition
    assert definitions is not None
    assert isinstance(definitions, list)
    assert len(definitions) >= 1

    # Verify the definition points to the function declaration
    definition = definitions[0]
    assert definition.range.start.line == 0
    assert definition.range.start.character == 4


@pytest.mark.asyncio
async def test_get_completions_for_python_file(application: Application, lsp_service):
    """Test that LSP service can get completions for a Python file."""
    from pathlib import Path

    # Create a test Python file with some code
    test_file = application.base_path("test_completions.py")
    test_file.write_text("import os\n\nos.pat")

    # Get completions after typing "os.pat"
    completions = await lsp_service.get_completions(Path(test_file), line=2, character=6)

    # Should get completion suggestions
    assert completions is not None
    assert isinstance(completions, list)
    assert len(completions) > 0

    # Should include "path" in the completions
    labels = [item.label for item in completions]
    assert any("path" in label.lower() for label in labels)


@pytest.mark.asyncio
async def test_goto_declaration_for_python_file(application: Application, lsp_service):
    """Test that LSP service can go to declaration for a Python symbol."""
    from pathlib import Path

    # Create a test Python file with a function and its usage
    test_file = application.base_path("test_declaration.py")
    test_file.write_text("def greet():\n    pass\n\ngreet()\n")

    # Go to declaration from the function call
    declarations = await lsp_service.goto_declaration(Path(test_file), line=3, character=0)

    # Should find the declaration
    assert declarations is not None
    assert isinstance(declarations, list)
    assert len(declarations) >= 1

    # Verify the declaration points to the function declaration
    declaration = declarations[0]
    assert declaration.range.start.line == 0
    assert declaration.range.start.character == 4


@pytest.mark.asyncio
async def test_goto_type_definition_for_python_file(application: Application, lsp_service):
    """Test that LSP service can go to type definition for a Python symbol."""
    from pathlib import Path

    # Create a test Python file with a class and its usage
    test_file = application.base_path("test_type_definition.py")
    test_file.write_text("class MyClass:\n    pass\n\nobj = MyClass()\n")

    # Go to type definition from the variable
    type_definitions = await lsp_service.goto_type_definition(Path(test_file), line=3, character=0)

    # Should find the type definition
    assert type_definitions is not None
    assert isinstance(type_definitions, list)
    assert len(type_definitions) >= 1

    # Verify the type definition points to the class declaration
    type_def = type_definitions[0]
    assert type_def.range.start.line == 0


@pytest.mark.asyncio
async def test_get_signature_help_for_python_file(application: Application, lsp_service):
    """Test that LSP service can get signature help for a Python function call."""
    from pathlib import Path

    # Create a test Python file with a function call
    test_file = application.base_path("test_signature_help.py")
    test_file.write_text("def greet(name: str, age: int) -> str:\n    return f'Hello {name}, {age}'\n\ngreet(\n")

    # Get signature help inside the function call parentheses
    signature_help = await lsp_service.get_signature_help(Path(test_file), line=3, character=6)

    # Should get signature help information
    assert signature_help is not None
    assert isinstance(signature_help, dict)
    assert "signatures" in signature_help


@pytest.mark.asyncio
async def test_handle_hover_operation(application: Application, lsp_service):
    """Test that handle method works for hover operation."""
    from pathlib import Path

    # Create a test Python file
    test_file = application.base_path("test_handle_hover.py")
    test_file.write_text("def hello():\n    pass\n")

    # Call handle with hover operation
    result = await lsp_service.handle(operation="hover", file_path=Path(test_file), line=0, character=4)

    # Should get hover result
    assert result is not None
    assert hasattr(result, "contents")


@pytest.mark.asyncio
async def test_handle_references_operation(application: Application, lsp_service):
    """Test that handle method works for references operation."""
    from pathlib import Path

    # Create a test Python file
    test_file = application.base_path("test_handle_references.py")
    test_file.write_text("def greet():\n    pass\n\ngreet()\ngreet()\n")

    # Call handle with references operation
    result = await lsp_service.handle(operation="references", file_path=Path(test_file), line=0, character=4)

    # Should get list of references
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 2


@pytest.mark.asyncio
async def test_handle_definition_operation(application: Application, lsp_service):
    """Test that handle method works for definition operation."""
    from pathlib import Path

    # Create a test Python file
    test_file = application.base_path("test_handle_definition.py")
    test_file.write_text("def greet():\n    pass\n\ngreet()\n")

    # Call handle with definition operation
    result = await lsp_service.handle(operation="definition", file_path=Path(test_file), line=3, character=0)

    # Should get list of definitions
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_handle_declaration_operation(application: Application, lsp_service):
    """Test that handle method works for declaration operation."""
    from pathlib import Path

    # Create a test Python file
    test_file = application.base_path("test_handle_declaration.py")
    test_file.write_text("def greet():\n    pass\n\ngreet()\n")

    # Call handle with declaration operation
    result = await lsp_service.handle(operation="declaration", file_path=Path(test_file), line=3, character=0)

    # Should get list of declarations
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_handle_type_definition_operation(application: Application, lsp_service):
    """Test that handle method works for type_definition operation."""
    from pathlib import Path

    # Create a test Python file
    test_file = application.base_path("test_handle_type_definition.py")
    test_file.write_text("class MyClass:\n    pass\n\nobj = MyClass()\n")

    # Call handle with type_definition operation
    result = await lsp_service.handle(operation="type_definition", file_path=Path(test_file), line=3, character=0)

    # Should get list of type definitions
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_handle_completions_operation(application: Application, lsp_service):
    """Test that handle method works for completions operation."""
    from pathlib import Path

    # Create a test Python file
    test_file = application.base_path("test_handle_completions.py")
    test_file.write_text("import os\n\nos.pat")

    # Call handle with completions operation
    result = await lsp_service.handle(operation="completions", file_path=Path(test_file), line=2, character=6)

    # Should get list of completions
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_handle_signature_help_operation(application: Application, lsp_service):
    """Test that handle method works for signature_help operation."""
    from pathlib import Path

    # Create a test Python file
    test_file = application.base_path("test_handle_signature_help.py")
    test_file.write_text("def greet(name: str, age: int) -> str:\n    return f'Hello {name}, {age}'\n\ngreet(\n")

    # Call handle with signature_help operation
    result = await lsp_service.handle(operation="signature_help", file_path=Path(test_file), line=3, character=6)

    # Should get signature help
    assert result is not None
    assert isinstance(result, dict)
    assert "signatures" in result


@pytest.mark.asyncio
async def test_handle_invalid_operation(application: Application, lsp_service):
    """Test that handle method returns None for invalid operation."""
    from pathlib import Path

    # Create a test Python file
    test_file = application.base_path("test_handle_invalid.py")
    test_file.write_text("def hello():\n    pass\n")

    # Call handle with invalid operation
    result = await lsp_service.handle(operation="invalid_operation", file_path=Path(test_file), line=0, character=0)

    # Should return None
    assert result is None


@pytest.mark.asyncio
async def test_handle_missing_parameters(lsp_service):
    """Test that handle method returns None when missing required parameters."""
    # Call handle without operation
    result = await lsp_service.handle(file_path="test.py")
    assert result is None

    # Call handle without file_path
    result = await lsp_service.handle(operation="hover")
    assert result is None


# Error Handling Tests


@pytest.mark.asyncio
async def test_get_hover_non_existent_file(lsp_service):
    """Test that get_hover returns None for a non-existent file."""
    from pathlib import Path

    # Try to get hover for a file that doesn't exist
    non_existent_file = Path("/tmp/this_file_does_not_exist.py")
    hover_result = await lsp_service.get_hover(non_existent_file, line=0, character=0)

    # Should return None since file doesn't exist
    assert hover_result is None


@pytest.mark.asyncio
async def test_find_references_non_existent_file(lsp_service):
    """Test that find_references returns empty list for a non-existent file."""
    from pathlib import Path

    # Try to find references in a file that doesn't exist
    non_existent_file = Path("/tmp/this_file_does_not_exist.py")
    references = await lsp_service.find_references(non_existent_file, line=0, character=0)

    # Should return empty list
    assert references == []


@pytest.mark.asyncio
async def test_goto_definition_non_existent_file(lsp_service):
    """Test that goto_definition returns empty list for a non-existent file."""
    from pathlib import Path

    # Try to go to definition in a file that doesn't exist
    non_existent_file = Path("/tmp/this_file_does_not_exist.py")
    definitions = await lsp_service.goto_definition(non_existent_file, line=0, character=0)

    # Should return empty list
    assert definitions == []


@pytest.mark.asyncio
async def test_get_completions_non_existent_file(lsp_service):
    """Test that get_completions returns empty list for a non-existent file."""
    from pathlib import Path

    # Try to get completions for a file that doesn't exist
    non_existent_file = Path("/tmp/this_file_does_not_exist.py")
    completions = await lsp_service.get_completions(non_existent_file, line=0, character=0)

    # Should return empty list
    assert completions == []


@pytest.mark.asyncio
async def test_unsupported_language_file(application: Application, lsp_service):
    """Test that LSP operations return None/empty for unsupported file types."""
    from pathlib import Path

    # Create a text file (no LSP server configured for .txt)
    test_file = application.base_path("test.txt")
    test_file.write_text("This is a text file\nwith some content\n")

    # All operations should return None or empty
    hover_result = await lsp_service.get_hover(Path(test_file), line=0, character=0)
    assert hover_result is None

    references = await lsp_service.find_references(Path(test_file), line=0, character=0)
    assert references == []

    definitions = await lsp_service.goto_definition(Path(test_file), line=0, character=0)
    assert definitions == []

    completions = await lsp_service.get_completions(Path(test_file), line=0, character=0)
    assert completions == []


@pytest.mark.asyncio
async def test_invalid_position(application: Application, lsp_service):
    """Test LSP operations with invalid line/character positions."""
    from pathlib import Path

    # Create a small Python file
    test_file = application.base_path("test_invalid_pos.py")
    test_file.write_text("def hello():\n    pass\n")

    # Try with line number way beyond file length
    hover_result = await lsp_service.get_hover(Path(test_file), line=1000, character=0)
    # LSP server should handle gracefully, likely returning None
    assert hover_result is None or isinstance(hover_result.contents, str)

    # Try with negative line number
    hover_result = await lsp_service.get_hover(Path(test_file), line=-1, character=0)
    assert hover_result is None or isinstance(hover_result.contents, str)


# Edge Cases Tests


@pytest.mark.asyncio
async def test_empty_file(application: Application, lsp_service):
    """Test LSP operations on an empty Python file."""
    from pathlib import Path

    # Create an empty Python file
    test_file = application.base_path("test_empty.py")
    test_file.write_text("")

    # Operations should handle empty file gracefully
    hover_result = await lsp_service.get_hover(Path(test_file), line=0, character=0)
    assert hover_result is None or isinstance(hover_result.contents, str)

    references = await lsp_service.find_references(Path(test_file), line=0, character=0)
    assert isinstance(references, list)

    definitions = await lsp_service.goto_definition(Path(test_file), line=0, character=0)
    assert isinstance(definitions, list)


@pytest.mark.asyncio
async def test_file_with_syntax_errors(application: Application, lsp_service):
    """Test LSP operations on a Python file with syntax errors."""
    from pathlib import Path

    # Create a Python file with syntax errors
    test_file = application.base_path("test_syntax_error.py")
    test_file.write_text("def broken(\n    this is not valid python\n")

    # LSP should still respond, though results may be limited
    hover_result = await lsp_service.get_hover(Path(test_file), line=0, character=4)
    # Should either return None or some hover info
    assert hover_result is None or isinstance(hover_result.contents, str)

    # Completions might still work in some contexts
    completions = await lsp_service.get_completions(Path(test_file), line=1, character=0)
    assert isinstance(completions, list)


@pytest.mark.asyncio
async def test_whitespace_only_file(application: Application, lsp_service):
    """Test LSP operations on a file with only whitespace."""
    from pathlib import Path

    # Create a Python file with only whitespace
    test_file = application.base_path("test_whitespace.py")
    test_file.write_text("   \n\n\t\t\n   ")

    # Operations should handle whitespace-only file gracefully
    hover_result = await lsp_service.get_hover(Path(test_file), line=0, character=0)
    assert hover_result is None or isinstance(hover_result.contents, str)

    completions = await lsp_service.get_completions(Path(test_file), line=0, character=0)
    assert isinstance(completions, list)


@pytest.mark.asyncio
async def test_position_at_end_of_line(application: Application, lsp_service):
    """Test LSP operations at the end of a line."""
    from pathlib import Path

    # Create a Python file
    test_file = application.base_path("test_eol.py")
    test_file.write_text("def hello():\n    pass\n")

    # Try hover at the end of the first line
    line_length = len("def hello():")
    hover_result = await lsp_service.get_hover(Path(test_file), line=0, character=line_length)
    # Should handle gracefully
    assert hover_result is None or isinstance(hover_result.contents, str)


@pytest.mark.asyncio
async def test_position_beyond_line_end(application: Application, lsp_service):
    """Test LSP operations beyond the end of a line."""
    from pathlib import Path

    # Create a Python file
    test_file = application.base_path("test_beyond_eol.py")
    test_file.write_text("def hello():\n    pass\n")

    # Try hover way beyond the line length
    hover_result = await lsp_service.get_hover(Path(test_file), line=0, character=1000)
    # LSP server should handle gracefully
    assert hover_result is None or isinstance(hover_result.contents, str)
