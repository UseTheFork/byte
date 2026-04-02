from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    pass


# Credits To https://github.com/charmbracelet/crush/blob/main/internal/tui/components/anim/anim.go
class RuneSpinner(Static):
    def _tick(self):
        self.update(f"Thinking {self.frames[self.phase % len(self.frames)]}")
        self.phase += 1

    def on_mount(self):
        self.set_interval(0.1, self._tick)
        self.phase = 0

        runes = list("0123456789abcdefABCDEF~!@#$%^&*()+=_")
        colors = ["primary", "secondary", "dim"]
        num_frames = 16  # Number of frames in the animation
        spinner_size = 5  # Number of runes per frame

        self.frames = []
        for frame_no in range(num_frames):
            frame_chars = []
            for i in range(spinner_size):
                # Use frame number and position to select rune
                seed = (frame_no * 31 + i * 17) % len(runes)

                # Randomly pick a color from the colors array
                color = colors[seed % len(colors)]
                color_tag = f"[${color}]"
                close_tag = f"[/${color}]"
                frame_chars.append(f"{color_tag}{runes[seed]}{close_tag}")
            self.frames.append("".join(frame_chars))
