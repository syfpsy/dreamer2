from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from io import TextIOBase
from typing import Iterable


STYLE_CODES = {
    "none": "\x1b[0m",
    "structural": "\x1b[2;37m",
    "signal": "\x1b[36m",
    "symbolic": "\x1b[33m",
    "decay": "\x1b[2;31m",
    "ui_muted": "\x1b[2;37m",
    "ui_bright": "\x1b[37m",
}


@dataclass(slots=True)
class Cell:
    char: str = " "
    style: str = "none"


class CellGrid:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.rows: list[list[Cell]] = [
            [Cell() for _ in range(width)] for _ in range(height)
        ]

    def set(self, x: int, y: int, char: str, style: str = "none") -> None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        self.rows[y][x] = Cell(char=char[:1], style=style)

    def write(self, x: int, y: int, text: str, style: str = "none") -> None:
        for offset, char in enumerate(text):
            self.set(x + offset, y, char, style)

    def overlay_lines(
        self,
        x: int,
        y: int,
        lines: Iterable[str],
        style: str,
        transparent_spaces: bool = True,
    ) -> None:
        for row_index, line in enumerate(lines):
            for col_index, char in enumerate(line):
                if transparent_spaces and char == " ":
                    continue
                self.set(x + col_index, y + row_index, char, style)

    def fill_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        char: str,
        style: str = "none",
    ) -> None:
        for row in range(y, y + height):
            for col in range(x, x + width):
                self.set(col, row, char, style)

    def signature_rows(self) -> list[str]:
        signatures: list[str] = []
        for row in self.rows:
            signatures.append("".join(f"{cell.char}\x00{cell.style}\x01" for cell in row))
        return signatures

    def ansi_rows(self, no_color: bool = False) -> list[str]:
        return [_row_to_ansi(row, no_color=no_color) for row in self.rows]

    def plain_rows(self) -> list[str]:
        return ["".join(cell.char for cell in row) for row in self.rows]

    def row_run_payloads(self) -> list[dict[str, object]]:
        payloads: list[dict[str, object]] = []
        for index, row in enumerate(self.rows):
            payloads.append(
                {
                    "index": index,
                    "signature": "".join(f"{cell.char}\x00{cell.style}\x01" for cell in row),
                    "runs": _row_to_runs(row),
                }
            )
        return payloads

    def payload(self) -> dict[str, object]:
        return {
            "width": self.width,
            "height": self.height,
            "rows": self.row_run_payloads(),
        }


class AnsiDiffRenderer:
    def __init__(
        self,
        stream: TextIOBase | None = None,
        *,
        use_diff: bool = True,
        no_color: bool = False,
    ) -> None:
        self.stream = stream or sys.stdout
        self.use_diff = use_diff
        self.no_color = no_color
        self._previous_signature: list[str] = []
        self._entered = False

    @property
    def interactive(self) -> bool:
        return bool(self.stream.isatty())

    def enter(self) -> None:
        if self._entered:
            return
        enable_windows_vt()
        if self.interactive:
            self.stream.write("\x1b[?1049h\x1b[?25l\x1b[2J\x1b[H")
            self.stream.flush()
        self._entered = True

    def leave(self) -> None:
        if not self._entered:
            return
        if self.interactive:
            self.stream.write("\x1b[0m\x1b[?25h\x1b[?1049l")
            self.stream.flush()
        self._entered = False
        self._previous_signature = []

    def render(self, grid: CellGrid, *, force_full: bool = False) -> None:
        ansi_rows = grid.ansi_rows(no_color=self.no_color)
        signature_rows = grid.signature_rows()

        if not self.interactive:
            self.stream.write("\n".join(grid.plain_rows()) + "\n")
            self.stream.flush()
            return

        if force_full or not self.use_diff or not self._previous_signature:
            self.stream.write("\x1b[H")
            self.stream.write("\n".join(ansi_rows))
            self.stream.write("\x1b[0m")
            self.stream.flush()
            self._previous_signature = signature_rows
            return

        for row_index, signature in enumerate(signature_rows):
            if row_index >= len(self._previous_signature) or signature != self._previous_signature[row_index]:
                self.stream.write(f"\x1b[{row_index + 1};1H{ansi_rows[row_index]}\x1b[0m")
        self.stream.flush()
        self._previous_signature = signature_rows

    def snapshot(self, grid: CellGrid) -> str:
        return "\n".join(grid.plain_rows())


def enable_windows_vt() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        return


def _row_to_ansi(row: list[Cell], no_color: bool) -> str:
    if no_color:
        return "".join(cell.char for cell in row)

    rendered: list[str] = []
    current_style = "none"
    rendered.append(STYLE_CODES[current_style])
    for cell in row:
        if cell.style != current_style:
            current_style = cell.style
            rendered.append(STYLE_CODES.get(current_style, STYLE_CODES["none"]))
        rendered.append(cell.char)
    rendered.append(STYLE_CODES["none"])
    return "".join(rendered)


def _row_to_runs(row: list[Cell]) -> list[dict[str, str]]:
    if not row:
        return []

    runs: list[dict[str, str]] = []
    current_style = row[0].style
    current_chars: list[str] = [row[0].char]

    for cell in row[1:]:
        if cell.style == current_style:
            current_chars.append(cell.char)
            continue

        runs.append({"style": current_style, "text": "".join(current_chars)})
        current_style = cell.style
        current_chars = [cell.char]

    runs.append({"style": current_style, "text": "".join(current_chars)})
    return runs
