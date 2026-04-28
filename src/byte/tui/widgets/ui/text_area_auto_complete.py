"""Autocomplete widget for TextArea - supports slash commands and file paths."""

from dataclasses import dataclass
from operator import itemgetter
from typing import TYPE_CHECKING

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.content import Content
from textual.css.query import NoMatches
from textual.style import Style
from textual.widget import Widget
from textual.widgets import OptionList, TextArea
from textual.widgets.option_list import Option
from textual_autocomplete.fuzzy_search import FuzzySearch

if TYPE_CHECKING:
    from byte.tui import ByteTUI


# Credits to https://github.com/mrocklin/claudechic/blob/c2ed949eebe903b5359406084423446098f872d9/claudechic/screens/chat.py#L17
def parse_shell_input(text: str) -> tuple[str, str]:
    """Parse shell input into (command, current_arg).

    Returns:
        (command, current_arg) where current_arg is what's being typed
    """
    # Strip leading ! or "/shell "
    if text.startswith("!"):
        text = text[1:]
    elif text.startswith("/shell "):
        text = text[7:]
    else:
        return "", text

    # Split by whitespace, keeping track of what's being typed
    parts = text.split()

    if not parts:
        return "", ""

    if text.endswith(" "):
        # Space after last word - completing new argument
        return parts[0], ""
    elif len(parts) == 1:
        # Still typing the command
        return "", parts[0]
    else:
        # Typing an argument
        return parts[0], parts[-1]


@dataclass
class TargetState:
    """State of the target TextArea."""

    text: str
    cursor_position: int  # Linear position in text


class DropdownItem(Option):
    """A single autocomplete option."""

    def __init__(
        self,
        main: str | Content,
        prefix: str | Content | None = None,
        id: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.main = Content(main) if isinstance(main, str) else main
        self.prefix = Content(prefix) if isinstance(prefix, str) else prefix
        prompt = self.main
        if self.prefix:
            prompt = Content.assemble(self.prefix, self.main)
        super().__init__(prompt, id, disabled)

    @property
    def value(self) -> str:
        """Get plain text value of the option (without prefix)."""
        return self.main.plain


class TextAreaAutoComplete(Widget):
    """Autocomplete dropdown for TextArea widgets.

    Supports two modes:
    - Slash commands: triggered by `/` at start of input
    - File paths: triggered by `@` anywhere in input
    """

    DEFAULT_CSS = """\
    TextAreaAutoComplete {
        height: 16;
        display: none;
        background: $surface;

        & OptionList {
            border: none;
            height: 1fr;
            padding: 0;
            margin: 0 1;
            overflow: hidden;
            text-wrap: nowrap;
            text-overflow: ellipsis;
        }

        & OptionList > .option-list--option-highlighted {
            background: $surface-lighten-1;
            color: $text;
        }

        & .autocomplete--highlight-match {
            text-style: bold;
            color: $primary;
        }
    }
    """

    COMPONENT_CLASSES = {"autocomplete--highlight-match"}

    app: ByteTUI

    def __init__(
        self,
        target: TextArea | str,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._target = target
        self._file_index: list[str] = []  # Set by app
        self._fuzzy_search = FuzzySearch()
        self._mode: str | None = None  # "slash" or "path" or None
        self._trigger_pos: int = 0  # Position of / or @
        self._completing: bool = False  # Flag to prevent re-showing during completion
        self._suppressed: bool = False  # Suppress until user types
        self._search_timer = None  # Timer for debounced file search

        self.slash_commands = self.app.command_registry.get_all_slash_command_names()

    @property
    def file_index(self) -> list[str]:
        """Get file index from app if available."""
        if hasattr(self.app, "file_index") and self.app.file_index:
            return self.app.file_index.files  # type: ignore[attr-defined]
        return self._file_index

    @file_index.setter
    def file_index(self, value: list[str]) -> None:
        self._file_index = value

    def compose(self) -> ComposeResult:
        option_list = OptionList()
        option_list.can_focus = False
        yield option_list

    @property
    def target(self) -> TextArea:
        """Resolve target widget (accepts selector string or widget instance)."""
        if isinstance(self._target, TextArea):
            return self._target
        return self.screen.query_one(self._target, TextArea)

    @property
    def option_list(self) -> OptionList:
        return self.query_one(OptionList)

    def _get_cursor_position(self) -> int:
        """Get linear cursor position from TextArea's (row, col) tuple."""
        target = self.target
        row, col = target.cursor_location
        lines = target.text.split("\n")
        pos = sum(len(lines[i]) + 1 for i in range(row)) + col
        return pos

    def _get_target_state(self) -> TargetState:
        return TargetState(
            text=self.target.text,
            cursor_position=self._get_cursor_position(),
        )

    def _cancel_search_timer(self) -> None:
        """Cancel any pending search timer."""
        if self._search_timer is not None:
            self._search_timer.stop()
            self._search_timer = None

    async def _do_slash_arg_search_async(self, state: TargetState) -> None:
        """Async slash argument search using command's get_completions."""
        if not self.app.command_registry:
            return

        text = state.text[: state.cursor_position] if state.cursor_position > 0 else state.text

        # Get completions from registry (which delegates to command)
        completions = await self.app.command_registry.get_slash_completions(text)

        # Convert to DropdownItems
        candidates = [DropdownItem(comp, prefix="") for comp, _desc in completions]

        # Update option list
        option_list = self.option_list
        option_list.clear_options()
        if candidates:
            option_list.add_options(list(reversed(candidates)))
            option_list.highlighted = len(candidates) - 1

        if option_list.option_count > 0:
            self.action_show()
        else:
            self.action_hide()

    def _do_slash_arg_search(self) -> None:
        """Execute debounced slash command argument search."""
        self._search_timer = None

        current_state = self._get_target_state()
        if not current_state.text.startswith("/") or " " not in current_state.text:
            self.action_hide()
            return
        self.run_worker(self._do_slash_arg_search_async(current_state), exclusive=True)

    def _should_show(self, search_string: str) -> bool:
        """Determine if dropdown should be shown."""
        option_count = self.option_list.option_count
        if option_count == 0:
            return False
        # Shell mode requires user to start typing something
        if self._mode == "shell" and not search_string:
            return False
        if option_count == 1:
            first_option = self.option_list.get_option_at_index(0).prompt
            text = first_option.plain if isinstance(first_option, Text) else str(first_option)
            # For slash commands, compare with the full command
            if self._mode == "slash":
                return text != search_string.lstrip("/")
            return text != search_string
        return True

    def _get_search_string(self, state: TargetState) -> str:
        """Get the string to search/filter with."""
        # Use text up to cursor, or full text if cursor at start
        text_to_check = state.text[: state.cursor_position] if state.cursor_position > 0 else state.text

        if self._mode == "slash":
            return text_to_check  # Include the /
        elif self._mode == "path":
            # Return full query after @ for fuzzy file matching
            return text_to_check[self._trigger_pos + 1 :]
        return ""

    def _get_path_candidates(self, state: TargetState) -> list[DropdownItem]:
        """Get file path candidates from index with fuzzy matching."""
        query = self._get_search_string(state)
        files = self.file_index

        if not files:
            return []

        # Use fuzzy search with highlighting
        # results = search_files(query, files, limit=15)
        results = []

        items = []
        for path, _score, indices in results:
            # Create highlighted content
            content = Content(path)
            match_style = Style.from_rich_style(
                self.get_component_rich_style("autocomplete--highlight-match", partial=True)
            )
            for idx in indices:
                if idx < len(path):
                    content = content.stylize(match_style, idx, idx + 1)

            items.append(DropdownItem(content))

        return items

    def _get_candidates(self, state: TargetState) -> list[DropdownItem]:
        """Get autocomplete candidates based on mode."""
        if self._mode == "slash":
            return [DropdownItem(cmd) for cmd in self.slash_commands]
        elif self._mode == "path":
            return self._get_path_candidates(state)
        return []

    def _apply_highlights(self, candidate: Content, offsets: tuple[int, ...]) -> Content:
        """Highlight matched characters."""
        match_style = Style.from_rich_style(
            self.get_component_rich_style("autocomplete--highlight-match", partial=True)
        )
        plain = candidate.plain
        for offset in offsets:
            if offset < len(plain) and not plain[offset].isspace():
                candidate = candidate.stylize(match_style, offset, offset + 1)
        return candidate

    def _get_matches(self, candidates: list[DropdownItem], search_string: str) -> list[DropdownItem]:
        """Filter and score candidates against search string."""
        if not search_string:
            return candidates

        # For slash commands, strip the leading slashes
        query = search_string.lstrip("/") if self._mode == "slash" else search_string
        if not query:
            return candidates

        matches_and_scores: list[tuple[DropdownItem, float]] = []
        for candidate in candidates:
            candidate_string = candidate.value.strip("/")  # Strip slashes for matching
            score, offsets = self._fuzzy_search.match(query, candidate_string)
            if score > 0:
                # Bonus for match starting at position 0
                if offsets and offsets[0] == 0:
                    score += 10.0
                # Adjust offsets if main has leading / that was stripped for matching
                adjusted_offsets = offsets
                if self._mode == "slash" and candidate.main.plain.startswith("/"):
                    adjusted_offsets = [o + 1 for o in offsets]
                highlighted = self._apply_highlights(candidate.main, tuple(adjusted_offsets))
                item = DropdownItem(
                    main=highlighted,
                    prefix=candidate.prefix,
                    id=candidate.id,
                    disabled=candidate.disabled,
                )
                matches_and_scores.append((item, score))

        matches_and_scores.sort(key=itemgetter(1), reverse=True)
        return [m for m, _ in matches_and_scores]

    def _rebuild_options(self, state: TargetState) -> None:
        """Rebuild dropdown options."""
        option_list = self.option_list
        option_list.clear_options()

        candidates = self._get_candidates(state)

        # For path/shell mode, candidates are already filtered
        if self._mode in ("path", "shell"):
            matches = candidates
        else:
            search_string = self._get_search_string(state)
            matches = self._get_matches(candidates, search_string)

        if matches:
            # Reverse order so best match is at bottom (near cursor)
            option_list.add_options(list(reversed(matches)))
            option_list.highlighted = len(matches) - 1  # Select bottom item

    def _show_options(self, state: TargetState) -> None:
        """Build and show options for current state."""
        self._rebuild_options(state)
        if self.option_list.option_count > 0:
            search = self._get_search_string(state)
            if self._should_show(search):
                self.action_show()
            else:
                self.action_hide()
        else:
            self.action_hide()

    def _do_path_search(self) -> None:
        """Execute debounced path search."""
        self._search_timer = None
        # Re-check that we're still in path mode with same trigger
        current_state = self._get_target_state()
        text_to_check = (
            current_state.text[: current_state.cursor_position]
            if current_state.cursor_position > 0
            else current_state.text
        )
        if "@" not in text_to_check:
            self.action_hide()
            return
        at_pos = text_to_check.rfind("@")
        if at_pos != self._trigger_pos:
            return  # Trigger position changed, skip this search
        self._show_options(current_state)

    async def _do_shell_search_async(self, state: TargetState) -> None:
        """Async shell search - runs executable scan off main thread."""
        text = state.text[: state.cursor_position] if state.cursor_position > 0 else state.text
        cmd, arg = parse_shell_input(text)

        if not cmd:
            # completions = await complete_command_async(arg, limit=20)
            completions = []
            candidates = [DropdownItem(c, prefix="$ ") for c in completions]
        # else:
        #     completions = await asyncio.to_thread(complete_path, arg, cwd, 20)
        #     candidates = [DropdownItem(c, prefix="📄 ") for c in completions]

        # Re-verify we're still in shell mode (user may have changed input)
        current_state = self._get_target_state()
        if not (current_state.text.startswith("!") or current_state.text.startswith("/shell ")):
            self.action_hide()
            return

        option_list = self.option_list
        option_list.clear_options()
        if candidates:
            option_list.add_options(list(reversed(candidates)))
            option_list.highlighted = len(candidates) - 1

        search = self._get_search_string(current_state)
        if option_list.option_count > 0 and self._should_show(search):
            self.action_show()
        else:
            self.action_hide()

    def _do_shell_search(self) -> None:
        """Execute debounced shell completion search (kicks off async)."""
        self._search_timer = None
        current_state = self._get_target_state()
        # Verify still in shell mode
        if not (current_state.text.startswith("!") or current_state.text.startswith("/shell ")):
            self.action_hide()
            return
        # Run async to avoid blocking on executable scan
        self.run_worker(self._do_shell_search_async(current_state), exclusive=True)

    def _handle_text_change(self) -> None:
        """Called when TextArea content changes."""
        if self._completing or self._suppressed:
            return
        state = self._get_target_state()
        # Use text up to cursor, or full text if cursor at start (common when setting text directly)
        text_to_check = state.text[: state.cursor_position] if state.cursor_position > 0 else state.text

        # Detect mode
        self._mode = None
        self._trigger_pos = 0

        # Check for shell command (! prefix or /shell)
        if state.text.startswith("!") or state.text.startswith("/shell "):
            self._mode = "shell"
            self._trigger_pos = 0
            self._cancel_search_timer()
            self._search_timer = self.set_timer(0.1, self._do_shell_search)
        # Check for slash command at start of input
        elif state.text.startswith("/"):
            self._mode = "slash"
            self._trigger_pos = 0
            # Check if we're completing arguments (space after command)
            if " " in state.text:
                # Debounce like path search since get_completions may be async
                self._cancel_search_timer()
                self._search_timer = self.set_timer(0.1, self._do_slash_arg_search)
            else:
                # Completing command name (instant)
                self._cancel_search_timer()
                self._show_options(state)
        # Check for @ path reference
        elif "@" in text_to_check:
            at_pos = text_to_check.rfind("@")
            # Make sure it's not in the middle of a word
            if at_pos == 0 or text_to_check[at_pos - 1] in " \n\t":
                self._mode = "path"
                self._trigger_pos = at_pos

                self._cancel_search_timer()
                self._search_timer = self.set_timer(0.15, self._do_path_search)
        else:
            self._cancel_search_timer()
            self.action_hide()

    def _on_selection_change(self) -> None:
        """Called when cursor position changes."""
        self._handle_text_change()

    def _handle_key(self, event) -> None:
        """Handle key events from target (via message_signal)."""
        from textual import events

        if not isinstance(event, events.Key):
            return

        # Only handle escape via signal (up/down handled by ChatInput actions)
        if event.key == "escape":
            self.handle_key(event.key)

    def _on_target_message(self, event) -> None:
        """Handle messages from the target TextArea."""
        from textual import events

        if isinstance(event, TextArea.Changed):
            self._handle_text_change()
        elif isinstance(event, events.Key):
            # Clear suppression on any printable key (user is typing)
            if self._suppressed and event.character and event.character.isprintable():
                self._suppressed = False
            self._handle_key(event)

    def on_mount(self) -> None:
        self.target.message_signal.subscribe(self, self._on_target_message)
        # Watch selection for cursor moves
        self.watch(self.target, "selection", self._on_selection_change)
        # Register with target for key interception
        if hasattr(self.target, "_autocomplete"):
            self.target._autocomplete = self  # type: ignore[attr-defined]

    def _apply_completion(self, value: str, state: TargetState) -> None:
        """Insert the completion into the TextArea."""
        target = self.target
        text = state.text
        # Use actual text length if cursor is at 0
        cursor_pos = state.cursor_position if state.cursor_position > 0 else len(text)

        if self._mode == "slash":
            if " " in state.text[:cursor_pos]:
                # Completing an argument - replace the partial argument
                parts = text[:cursor_pos].split(" ")
                if len(parts) > 1:
                    # Find where current arg starts
                    arg_start = cursor_pos - len(parts[-1])
                    new_text = text[:arg_start] + value + " " + text[cursor_pos:]
                    target.text = new_text
                    # Move cursor after completion + space
                    new_cursor = arg_start + len(value) + 1
                    lines = new_text[:new_cursor].split("\n")
                    row = len(lines) - 1
                    col = len(lines[-1])
                    target.move_cursor((row, col))
            else:
                # Completing command name (existing behavior)
                target.text = value + " "  # Add space after command
                target.move_cursor((0, len(value) + 1))
        elif self._mode == "path":
            # Replace @query with the selected path (keep the @), add trailing space
            replace_start = self._trigger_pos + 1  # After @
            new_text = text[:replace_start] + value + " " + text[cursor_pos:]
            target.text = new_text
            new_cursor = replace_start + len(value) + 1  # +1 for space
            # Convert linear position to (row, col)
            lines = new_text[:new_cursor].split("\n")
            row = len(lines) - 1
            col = len(lines[-1])
            target.move_cursor((row, col))

    def _complete(self, option_index: int, submit: bool = False) -> None:
        """Apply the selected completion.

        Args:
            option_index: Index of the option to complete
            submit: If True, also trigger submit after completing (for Enter key)
        """
        if not self.display or self.option_list.option_count == 0:
            return

        option = self.option_list.get_option_at_index(option_index)
        value = option.prompt.plain if isinstance(option.prompt, Text) else str(option.prompt)

        state = self._get_target_state()
        self._completing = True
        self._apply_completion(value, state)

        # Use call_after_refresh to hide after all pending updates
        def hide_and_reset():
            self._completing = False
            self.action_hide()
            # Only auto-submit for slash commands (complete actions)
            # File paths are usually part of a larger message
            if submit and self._mode == "slash" and hasattr(self.target, "action_submit"):
                self.target.action_submit()  # type: ignore[attr-defined]

        self.call_after_refresh(hide_and_reset)

    def handle_key(self, key: str) -> bool:  # type: ignore[override]
        """Handle a key press. Returns True if the key was consumed.

        Call this from the target widget's key handler to intercept keys
        before the target processes them.
        """
        try:
            option_list = self.option_list
        except NoMatches:
            return False

        if not option_list.option_count or not self.display:
            return False

        highlighted = option_list.highlighted or 0

        # Up moves visually up (lower index = top of list)
        # Down moves visually down (higher index = bottom of list)
        if key == "up":
            option_list.highlighted = max(highlighted - 1, 0)
            return True
        elif key == "down":
            option_list.highlighted = min(highlighted + 1, option_list.option_count - 1)
            return True
        elif key == "tab":
            self._complete(highlighted)
            return True
        elif key == "enter":
            self._complete(highlighted, submit=True)
            return True
        elif key == "escape":
            self.action_hide()
            return True

        return False

    def action_hide(self) -> None:
        """Hide the autocomplete dropdown."""
        self.styles.display = "none"

    def action_show(self) -> None:
        """Show the autocomplete dropdown."""
        self.styles.display = "block"

    def suppress(self) -> None:
        """Suppress autocomplete until user types a printable character."""
        self._suppressed = True
        self._cancel_search_timer()
        self.action_hide()

    @on(OptionList.OptionSelected)
    def _on_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle mouse click on option."""
        self._complete(event.option_index)
