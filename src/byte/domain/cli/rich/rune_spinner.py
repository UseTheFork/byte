from rich.console import RenderResult
from rich.spinner import Spinner
from rich.text import Text


# Credits To https://github.com/charmbracelet/crush/blob/main/internal/tui/components/anim/anim.go
class RuneSpinner(Spinner):
    """A custom spinner that animates random runes with theme-based colors.

    Extends Rich's Spinner to display cycling random characters with gradient colors
    based on the console's theme primary and secondary colors.
    Usage: `spinner = RuneSpinner("Thinking...", size=8)`
    """

    def __init__(
        self,
        text: str = "",
        *,
        speed: float = 1.0,
        size: int = 6,
    ) -> None:
        """Initialize the animated spinner.

        Args:
                name: Base spinner name (used for timing)
                text: Text to display next to spinner
                style: Style override (optional)
                speed: Animation speed multiplier
                size: Number of animated characters to display
        """
        super().__init__("dots", text, style=None, speed=speed)
        self.size = size
        self.runes = list("0123456789abcdefABCDEF~!@#$%^&*()+=_")

    def render(self, time: float) -> "RenderResult":
        """Render the animated spinner with cycling runes.

        Args:
                time: Current time in seconds

        Returns:
                Text object with animated runes and optional text
        """
        if self.start_time is None:
            self.start_time = time

        # Calculate frame based on time and speed
        elapsed = (time - self.start_time) * self.speed
        frame_no = int(elapsed * 25)  # 25 fps for rune cycling

        # Available theme colors to randomly pick from
        colors = ["primary", "secondary", "text"]

        # Generate animated runes
        animated_chars = []
        for i in range(self.size):
            # Use frame and position to seed randomness for consistent animation
            seed = (frame_no + i) * 31  # Prime number for better distribution
            rune_index = seed % len(self.runes)
            char = self.runes[rune_index]

            # Randomly pick color using the same seeding approach for consistency
            color_seed = (frame_no + i) * 37  # Different prime for color selection
            color_index = color_seed % len(colors)
            color = colors[color_index]
            animated_chars.append(f"[{color}]{char}[/{color}]")

        spinner_text = "".join(animated_chars)

        if not self.text:
            return Text.from_markup(spinner_text)  # pyright: ignore[reportReturnType]
        else:
            return Text.from_markup(f"{spinner_text} {self.text}")  # pyright: ignore[reportReturnType]
