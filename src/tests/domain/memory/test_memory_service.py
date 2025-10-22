"""Test suite for MemoryService.

Tests thread management, checkpoint operations, and undo functionality.
"""

import pytest

from byte.domain.memory.service.memory_service import MemoryService


# TODO: Finish this
class TestMemoryServiceThreadManagement:
	"""Test suite for thread creation and management."""

	@pytest.mark.asyncio
	async def test_create_thread(self, test_container):
		"""Test creating a new thread returns a unique UUID."""
		memory_service = await test_container.make(MemoryService)

		thread_id = memory_service.create_thread()

		assert thread_id is not None
		assert isinstance(thread_id, str)
		assert len(thread_id) > 0

	@pytest.mark.asyncio
	async def test_create_multiple_threads_are_unique(self, test_container):
		"""Test that multiple thread creations return unique IDs."""
		memory_service = await test_container.make(MemoryService)

		thread_id_1 = memory_service.create_thread()
		thread_id_2 = memory_service.create_thread()

		assert thread_id_1 != thread_id_2

	@pytest.mark.asyncio
	async def test_set_current_thread(self, test_container):
		"""Test setting the current active thread."""
		memory_service = await test_container.make(MemoryService)
		thread_id = memory_service.create_thread()

		await memory_service.set_current_thread(thread_id)

		assert memory_service.get_current_thread() == thread_id

	@pytest.mark.asyncio
	async def test_get_current_thread_initially_none(self, test_container):
		"""Test that current thread is None before being set."""
		memory_service = await test_container.make(MemoryService)

		assert memory_service.get_current_thread() is None

	@pytest.mark.asyncio
	async def test_get_or_create_thread_creates_when_none(self, test_container):
		"""Test that get_or_create_thread creates a new thread when none exists."""
		memory_service = await test_container.make(MemoryService)

		thread_id = await memory_service.get_or_create_thread()

		assert thread_id is not None
		assert memory_service.get_current_thread() == thread_id

	@pytest.mark.asyncio
	async def test_get_or_create_thread_returns_existing(self, test_container):
		"""Test that get_or_create_thread returns existing thread when set."""
		memory_service = await test_container.make(MemoryService)

		original_thread_id = await memory_service.get_or_create_thread()
		same_thread_id = await memory_service.get_or_create_thread()

		assert original_thread_id == same_thread_id

	@pytest.mark.asyncio
	async def test_new_thread_creates_and_sets(self, test_container):
		"""Test that new_thread creates a new thread and sets it as current."""
		memory_service = await test_container.make(MemoryService)

		thread_id = await memory_service.new_thread()

		assert thread_id is not None
		assert memory_service.get_current_thread() == thread_id


class TestMemoryServiceCheckpointer:
	"""Test suite for checkpointer initialization and access."""

	@pytest.mark.asyncio
	async def test_get_checkpointer_initializes(self, test_container):
		"""Test that get_checkpointer initializes InMemorySaver."""
		memory_service = await test_container.make(MemoryService)

		checkpointer = await memory_service.get_checkpointer()

		assert checkpointer is not None
		from langgraph.checkpoint.memory import InMemorySaver

		assert isinstance(checkpointer, InMemorySaver)

	@pytest.mark.asyncio
	async def test_get_checkpointer_returns_same_instance(self, test_container):
		"""Test that get_checkpointer returns the same instance on multiple calls."""
		memory_service = await test_container.make(MemoryService)

		checkpointer_1 = await memory_service.get_checkpointer()
		checkpointer_2 = await memory_service.get_checkpointer()

		assert checkpointer_1 is checkpointer_2

	@pytest.mark.asyncio
	async def test_get_saver_returns_checkpointer(self, test_container):
		"""Test that get_saver returns the same checkpointer instance."""
		memory_service = await test_container.make(MemoryService)

		saver = await memory_service.get_saver()
		checkpointer = await memory_service.get_checkpointer()

		assert saver is checkpointer


class TestMemoryServiceUndo:
	"""Test suite for undo functionality."""

	@pytest.mark.asyncio
	async def test_undo_with_no_current_thread(self, test_container):
		"""Test that undo returns False when no thread is set."""
		memory_service = await test_container.make(MemoryService)

		result = await memory_service.undo_last_step()

		assert result is False

	@pytest.mark.asyncio
	async def test_undo_with_no_checkpoints(self, test_container):
		"""Test that undo returns False when thread has no checkpoints."""
		memory_service = await test_container.make(MemoryService)

		# Create and set a thread but don't create any checkpoints
		await memory_service.new_thread()

		result = await memory_service.undo_last_step()

		assert result is False

	@pytest.mark.asyncio
	async def test_undo_with_single_checkpoint(self, test_container):
		"""Test that undo returns False when thread has only one checkpoint."""
		from langgraph.graph import END, START, StateGraph
		from typing_extensions import TypedDict

		memory_service = await test_container.make(MemoryService)
		thread_id = await memory_service.new_thread()
		checkpointer = await memory_service.get_checkpointer()

		# Create a simple graph with checkpointer
		class State(TypedDict):
			value: int

		def node_a(state: State):
			return {"value": state["value"] + 1}

		workflow = StateGraph(State)
		workflow.add_node("node_a", node_a)
		workflow.add_edge(START, "node_a")
		workflow.add_edge("node_a", END)

		graph = workflow.compile(checkpointer=checkpointer)

		# Run graph once to create a single checkpoint
		config = {"configurable": {"thread_id": thread_id}}
		await graph.ainvoke({"value": 0}, config)

		# Try to undo - should fail as we need at least 2 checkpoints
		result = await memory_service.undo_last_step()

		assert result is False

	@pytest.mark.asyncio
	async def test_undo_with_multiple_checkpoints(self, test_container):
		"""Test that undo successfully rolls back to previous checkpoint."""
		from langgraph.graph import END, START, StateGraph
		from typing_extensions import TypedDict

		memory_service = await test_container.make(MemoryService)
		thread_id = await memory_service.new_thread()
		checkpointer = await memory_service.get_checkpointer()

		# Create a simple graph with checkpointer
		class State(TypedDict):
			value: int

		def node_a(state: State):
			return {"value": state["value"] + 1}

		def node_b(state: State):
			return {"value": state["value"] + 10}

		workflow = StateGraph(State)
		workflow.add_node("node_a", node_a)
		workflow.add_node("node_b", node_b)
		workflow.add_edge(START, "node_a")
		workflow.add_edge("node_a", "node_b")
		workflow.add_edge("node_b", END)

		graph = workflow.compile(checkpointer=checkpointer)

		# Run graph to create multiple checkpoints
		config = {"configurable": {"thread_id": thread_id}}
		result = await graph.ainvoke({"value": 0}, config)

		# After execution: value should be 11 (0 + 1 + 10)
		assert result["value"] == 11

		# Undo should succeed
		undo_result = await memory_service.undo_last_step()
		assert undo_result is True

		# Get current state - should be rolled back
		state = await graph.aget_state(config)

		# State should be from before the last node executed
		# The exact value depends on which checkpoint we rolled back to
		assert state.values["value"] < 11

	@pytest.mark.asyncio
	async def test_undo_preserves_earlier_checkpoints(self, test_container):
		"""Test that undo doesn't delete earlier checkpoint history."""
		from langgraph.graph import END, START, StateGraph
		from typing_extensions import TypedDict

		memory_service = await test_container.make(MemoryService)
		thread_id = await memory_service.new_thread()
		checkpointer = await memory_service.get_checkpointer()

		class State(TypedDict):
			value: int

		def node_a(state: State):
			return {"value": state["value"] + 1}

		def node_b(state: State):
			return {"value": state["value"] + 10}

		workflow = StateGraph(State)
		workflow.add_node("node_a", node_a)
		workflow.add_node("node_b", node_b)
		workflow.add_edge(START, "node_a")
		workflow.add_edge("node_a", "node_b")
		workflow.add_edge("node_b", END)

		graph = workflow.compile(checkpointer=checkpointer)

		# Run graph
		config = {"configurable": {"thread_id": thread_id}}
		await graph.ainvoke({"value": 0}, config)

		# Get initial history count
		initial_history = [checkpoint async for checkpoint in checkpointer.alist(config)]
		initial_count = len(initial_history)

		# Undo
		await memory_service.undo_last_step()

		# Get history after undo
		after_undo_history = [checkpoint async for checkpoint in checkpointer.alist(config)]

		# History should still exist (checkpoints aren't deleted, just rolled back)
		assert len(after_undo_history) >= initial_count - 1

	@pytest.mark.asyncio
	async def test_undo_multiple_times(self, test_container):
		"""Test that undo can be called multiple times to roll back further."""
		from langgraph.graph import END, START, StateGraph
		from typing_extensions import TypedDict

		memory_service = await test_container.make(MemoryService)
		thread_id = await memory_service.new_thread()
		checkpointer = await memory_service.get_checkpointer()

		class State(TypedDict):
			value: int

		def node_a(state: State):
			return {"value": state["value"] + 1}

		def node_b(state: State):
			return {"value": state["value"] + 10}

		def node_c(state: State):
			return {"value": state["value"] + 100}

		workflow = StateGraph(State)
		workflow.add_node("node_a", node_a)
		workflow.add_node("node_b", node_b)
		workflow.add_node("node_c", node_c)
		workflow.add_edge(START, "node_a")
		workflow.add_edge("node_a", "node_b")
		workflow.add_edge("node_b", "node_c")
		workflow.add_edge("node_c", END)

		graph = workflow.compile(checkpointer=checkpointer)

		# Run graph
		config = {"configurable": {"thread_id": thread_id}}
		result = await graph.ainvoke({"value": 0}, config)

		# Final value should be 111 (0 + 1 + 10 + 100)
		assert result["value"] == 111

		# First undo
		first_undo = await memory_service.undo_last_step()
		assert first_undo is True

		# Second undo
		second_undo = await memory_service.undo_last_step()

		# Second undo should also succeed as we have enough checkpoints
		assert second_undo is True


class TestMemoryServiceUndoCommand:
	"""Test suite for UndoCommand integration."""

	@pytest.mark.asyncio
	async def test_undo_command_with_no_thread(self, test_container):
		"""Test UndoCommand handles case when no thread is active."""
		from io import StringIO

		from rich.console import Console

		from byte.domain.memory.command.undo_command import UndoCommand

		command = await test_container.make(UndoCommand)

		# Capture console output
		string_io = StringIO()
		test_console = Console(file=string_io, force_terminal=True)

		# Replace console in container for this test
		console_service = await test_container.make("byte.domain.cli.service.console_service.ConsoleService")
		console_service.console = test_console

		# Execute command
		await command.execute("")

		# Output should indicate failure
		output = string_io.getvalue()
		assert "no previous checkpoint" in output.lower() or "failed" in output.lower()

	@pytest.mark.asyncio
	async def test_undo_command_with_successful_undo(self, test_container):
		"""Test UndoCommand handles successful undo operation."""
		from io import StringIO

		from langgraph.graph import END, START, StateGraph
		from rich.console import Console
		from typing_extensions import TypedDict

		from byte.domain.memory.command.undo_command import UndoCommand
		from byte.domain.memory.service.memory_service import MemoryService

		memory_service = await test_container.make(MemoryService)
		command = await test_container.make(UndoCommand)

		# Setup graph with checkpoints
		thread_id = await memory_service.new_thread()
		checkpointer = await memory_service.get_checkpointer()

		class State(TypedDict):
			value: int

		def node_a(state: State):
			return {"value": state["value"] + 1}

		def node_b(state: State):
			return {"value": state["value"] + 10}

		workflow = StateGraph(State)
		workflow.add_node("node_a", node_a)
		workflow.add_node("node_b", node_b)
		workflow.add_edge(START, "node_a")
		workflow.add_edge("node_a", "node_b")
		workflow.add_edge("node_b", END)

		graph = workflow.compile(checkpointer=checkpointer)

		# Run graph to create checkpoints
		config = {"configurable": {"thread_id": thread_id}}
		await graph.ainvoke({"value": 0}, config)

		# Capture console output
		string_io = StringIO()
		test_console = Console(file=string_io, force_terminal=True)

		console_service = await test_container.make("byte.domain.cli.service.console_service.ConsoleService")
		console_service.console = test_console

		# Execute undo command
		await command.execute("")

		# Output should indicate success
		output = string_io.getvalue()
		assert "success" in output.lower()
