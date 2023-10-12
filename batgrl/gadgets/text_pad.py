"""
A text-pad gadget for multiline editable text.
"""
from wcwidth import wcswidth

from ..colors import Color, ColorPair
from ..io import Key, KeyEvent, Mods, MouseButton, MouseEvent, PasteEvent
from .behaviors.focusable import Focusable
from .behaviors.themable import Themable
from .gadget import Gadget
from .scroll_view import (
    DEFAULT_INDICATOR_HOVER,
    DEFAULT_INDICATOR_NORMAL,
    DEFAULT_INDICATOR_PRESS,
    DEFAULT_SCROLLBAR_COLOR,
    ScrollView,
)
from .text import (
    Point,
    PosHint,
    PosHintDict,
    Size,
    SizeHint,
    SizeHintDict,
    Text,
    add_text,
    style_char,
)

__all__ = [
    "Point",
    "PosHint",
    "PosHintDict",
    "Size",
    "SizeHint",
    "SizeHintDict",
    "TextPad",
]

WORD_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_")


class TextPad(Themable, Focusable, ScrollView):
    """
    A text-pad gadget for multiline editable text.

    Supports pasting, mouse selection, and cursor navigation.

    Parameters
    ----------
    indicator_normal_color : Color, default: DEFAULT_INDICATOR_NORMAL
        Scrollbar indicator normal color.
    indicator_hover_color : Color, default: DEFAULT_INDICATOR_HOVER
        Scrollbar indicator hover color.
    indicator_press_color : Color, default: DEFAULT_INDICATOR_PRESS
        Scrollbar indicator press color.
    scrollbar_color : Color, default: DEFAULT_SCROLLBAR_COLOR
        Background color of scrollbar.
    allow_vertical_scroll : bool, default: True
        Allow vertical scrolling.
    allow_horizontal_scroll : bool, default: True
        Allow horizontal scrolling.
    show_vertical_bar : bool, default: True
        Show the vertical scrollbar.
    show_horizontal_bar : bool, default: True
        Show the horizontal scrollbar.
    scrollwheel_enabled : bool, default: True
        Allow vertical scrolling with scrollwheel.
    arrow_keys_enabled : bool, default: False
        Allow scrolling with arrow keys.
    is_grabbable : bool, default: True
        If false, grabbable behavior is disabled.
    disable_ptf : bool, default: False
        If true, gadget will not be pulled to front when grabbed.
    mouse_button : MouseButton, default: MouseButton.LEFT
        Mouse button used for grabbing.
    size : Size, default: Size(10, 10)
        Size of gadget.
    pos : Point, default: Point(0, 0)
        Position of upper-left corner in parent.
    size_hint : SizeHint | SizeHintDict | None, default: None
        Size as a proportion of parent's height and width.
    pos_hint : PosHint | PosHintDict | None , default: None
        Position as a proportion of parent's height and width.
    is_transparent : bool, default: False
        Whether :attr:`background_char` and :attr:`background_color_pair` are painted.
    is_visible : bool, default: True
        Whether gadget is visible. Gadget will still receive input events if not
        visible.
    is_enabled : bool, default: True
        Whether gadget is enabled. A disabled gadget is not painted and doesn't receive
        input events.
    background_char : str | None, default: None
        The background character of the gadget if the gadget is not transparent.
        Character must be single unicode half-width grapheme.
    background_color_pair : ColorPair | None, default: None
        The background color pair of the gadget if the gadget is not transparent.

    Attributes
    ----------
    text : str
        The textpad's text.
    is_focused : bool
        Return true if gadget has focus.
    any_focused : bool
        Return true if any gadget has focus.
    view : Gadget | None
        The scrolled gadget.
    allow_vertical_scroll : bool
        Allow vertical scrolling.
    allow_horizontal_scroll : bool
        Allow horizontal scrolling.
    show_vertical_bar : bool
        Show the vertical scrollbar.
    show_horizontal_bar : bool
        Show the horizontal scrollbar.
    scrollwheel_enabled : bool
        Allow vertical scrolling with scrollwheel.
    arrow_keys_enabled : bool
        Allow scrolling with arrow keys.
    scrollbar_color : Color
        Background color of scrollbar.
    indicator_normal_color : Color
        Scrollbar indicator normal color.
    indicator_hover_color : Color
        Scrollbar indicator hover color.
    indicator_press_color : Color
        Scrollbar indicator press color.
    vertical_proportion : float
        Vertical scroll position as a proportion of total.
    horizontal_proportion : float
        Horizontal scroll position as a proportion of total.
    is_grabbable : bool
        If false, grabbable behavior is disabled.
    disable_ptf : bool
        If true, gadget will not be pulled to front when grabbed.
    mouse_button : MouseButton
        Mouse button used for grabbing.
    is_grabbed : bool
        True if gadget is grabbed.
    mouse_dyx : Point
        Last change in mouse position.
    mouse_dy : int
        Last vertical change in mouse position.
    mouse_dx : int
        Last horizontal change in mouse position.
    size : Size
        Size of gadget.
    height : int
        Height of gadget.
    rows : int
        Alias for :attr:`height`.
    width : int
        Width of gadget.
    columns : int
        Alias for :attr:`width`.
    pos : Point
        Position of upper-left corner.
    top : int
        Y-coordinate of top of gadget.
    y : int
        Y-coordinate of top of gadget.
    left : int
        X-coordinate of left side of gadget.
    x : int
        X-coordinate of left side of gadget.
    bottom : int
        Y-coordinate of bottom of gadget.
    right : int
        X-coordinate of right side of gadget.
    center : Point
        Position of center of gadget.
    absolute_pos : Point
        Absolute position on screen.
    size_hint : SizeHint
        Size as a proportion of parent's height and width.
    pos_hint : PosHint
        Position as a proportion of parent's height and width.
    background_char : str | None
        The background character of the gadget if the gadget is not transparent.
    background_color_pair : ColorPair | None
        Background color pair.
    parent : Gadget | None
        Parent gadget.
    children : list[Gadget]
        Children gadgets.
    is_transparent : bool
        True if gadget is transparent.
    is_visible : bool
        True if gadget is visible.
    is_enabled : bool
        True if gadget is enabled.
    root : Gadget | None
        If gadget is in gadget tree, return the root gadget.
    app : App
        The running app.

    Methods
    -------
    update_theme():
        Paint the gadget with current theme.
    focus():
        Focus gadget.
    blur():
        Un-focus gadget.
    focus_next():
        Focus next focusable gadget.
    focus_previous():
        Focus previous focusable gadget.
    on_focus():
        Called when gadget is focused.
    on_blur():
        Called when gadget loses focus.
    grab(mouse_event):
        Grab the gadget.
    ungrab(mouse_event):
        Ungrab the gadget.
    grab_update(mouse_event):
        Update gadget with incoming mouse events while grabbed.
    on_size():
        Called when gadget is resized.
    apply_hints():
        Apply size and pos hints.
    to_local(point):
        Convert point in absolute coordinates to local coordinates.
    collides_point(point):
        True if point collides with an uncovered portion of gadget.
    collides_gadget(other):
        True if other is within gadget's bounding box.
    add_gadget(gadget):
        Add a child gadget.
    add_gadgets(\\*gadgets):
        Add multiple child gadgets.
    remove_gadget(gadget):
        Remove a child gadget.
    pull_to_front():
        Move to end of gadget stack so gadget is drawn last.
    walk_from_root():
        Yield all descendents of the root gadget (preorder traversal).
    walk():
        Yield all descendents of this gadget (preorder traversal).
    walk_reverse():
        Yield all descendents of this gadget (reverse postorder traversal).
    ancestors():
        Yield all ancestors of this gadget.
    subscribe(source, attr, action):
        Subscribe to a gadget property.
    unsubscribe(source, attr):
        Unsubscribe to a gadget property.
    on_key(key_event):
        Handle key press event.
    on_mouse(mouse_event):
        Handle mouse event.
    on_paste(paste_event):
        Handle paste event.
    tween(...):
        Sequentially update gadget properties over time.
    on_add():
        Called after a gadget is added to gadget tree.
    on_remove():
        Called before gadget is removed from gadget tree.
    prolicide():
        Recursively remove all children.
    destroy():
        Destroy this gadget and all descendents.
    """

    def __init__(
        self,
        *,
        indicator_normal_color: Color = DEFAULT_INDICATOR_NORMAL,
        indicator_hover_color: Color = DEFAULT_INDICATOR_HOVER,
        indicator_press_color: Color = DEFAULT_INDICATOR_PRESS,
        scrollbar_color: Color = DEFAULT_SCROLLBAR_COLOR,
        allow_vertical_scroll: bool = True,
        allow_horizontal_scroll: bool = True,
        show_vertical_bar: bool = True,
        show_horizontal_bar: bool = True,
        scrollwheel_enabled: bool = True,
        arrow_keys_enabled: bool = False,
        is_grabbable: bool = True,
        disable_ptf: bool = True,
        mouse_button: MouseButton = MouseButton.LEFT,
        size: Size = Size(10, 10),
        pos: Point = Point(0, 0),
        size_hint: SizeHint | SizeHintDict | None = None,
        pos_hint: PosHint | PosHintDict | None = None,
        is_transparent: bool = False,
        is_visible: bool = True,
        is_enabled: bool = True,
        background_char: str | None = None,
        background_color_pair: ColorPair | None = None,
    ):
        self._last_x = None
        self._selection_start = self._selection_end = None
        self._line_lengths = [0]
        self._undo_stack = []
        self._redo_stack = []
        self._undo_buffer = []
        self._undo_buffer_type = "add"

        self._cursor = Gadget(size=(1, 1), is_enabled=False, is_transparent=True)
        self._pad = Text(size=(1, 1))
        self._pad.add_gadget(self._cursor)

        super().__init__(
            indicator_normal_color=indicator_normal_color,
            indicator_hover_color=indicator_hover_color,
            indicator_press_color=indicator_press_color,
            scrollbar_color=scrollbar_color,
            allow_vertical_scroll=allow_vertical_scroll,
            allow_horizontal_scroll=allow_horizontal_scroll,
            show_vertical_bar=show_vertical_bar,
            show_horizontal_bar=show_horizontal_bar,
            scrollwheel_enabled=scrollwheel_enabled,
            arrow_keys_enabled=arrow_keys_enabled,
            is_grabbable=is_grabbable,
            disable_ptf=disable_ptf,
            mouse_button=mouse_button,
            size=size,
            pos=pos,
            size_hint=size_hint,
            pos_hint=pos_hint,
            is_transparent=is_transparent,
            is_visible=is_visible,
            is_enabled=is_enabled,
            background_char=background_char,
            background_color_pair=background_color_pair,
        )

        self.view = self._pad

    def update_theme(self):
        primary = self.color_theme.primary

        self._cursor.background_color_pair = primary.reversed()
        self._pad.colors[:] = primary
        self._pad.default_color_pair = primary
        self.background_color_pair = primary.bg_color * 2

        self._highlight_selection()

    def on_size(self):
        super().on_size()

        if self.port_width > self._pad.width:
            self._pad.width = self.port_width
        elif self.port_width < self._pad.width:
            self._pad.width = max(self.port_width, max(self._line_lengths) + 1)

        self._highlight_selection()

    def on_focus(self):
        self._cursor.is_enabled = True

    def on_blur(self):
        self._cursor.is_enabled = False

    def _move_undo_buffer_to_stack(self, buffer_type=None):
        self._undo_buffer_type = buffer_type
        if self._undo_buffer:
            self._undo_stack.append(self._undo_buffer)
            self._undo_buffer = []
            self._redo_stack.clear()

    def undo(self):
        self._move_undo_buffer_to_stack()
        if self._undo_stack:
            redo = []
            for func, args, selection_start, selection_end, cursor in reversed(
                self._undo_stack.pop()
            ):
                redo.append(func(*args))
                self._selection_start = selection_start
                self._selection_end = selection_end
                self.cursor = cursor
            self._redo_stack.append(redo)

    def redo(self):
        if self._redo_stack and not self._undo_buffer:
            undo = []
            for func, args, selection_start, selection_end, cursor in reversed(
                self._redo_stack.pop()
            ):
                undo.append(func(*args))
                self._selection_start = selection_start
                self._selection_end = selection_end
                self.cursor = cursor
            self._undo_stack.append(undo)

    @property
    def text(self) -> str:
        return "\n".join(
            "".join(row[:line_length])
            for row, line_length in zip(self._pad.canvas["char"], self._line_lengths)
        )

    @text.setter
    def text(self, text: str):
        self._redo_stack.clear()
        self._undo_stack.clear()
        self._undo_buffer.clear()
        self.unselect()
        lines = text.split("\n")
        self._line_lengths = list(map(wcswidth, lines))

        pad = self._pad
        pad.canvas[:] = style_char(" ")
        pad.height = len(lines)
        pad.width = max(max(self._line_lengths) + 1, self.port_width)

        add_text(pad.canvas, text)
        self.cursor = self.end_text_point

    @property
    def cursor(self) -> Point:
        return self._cursor.pos

    @cursor.setter
    def cursor(self, cursor: Point):
        """
        After setting cursor position, move pad so that cursor is visible.
        """
        y, x = cursor
        self._cursor.pos = Point(y, x)

        max_y = self.height - (self.show_horizontal_bar and 1) - 1
        if (rel_y := y + self._pad.y) > max_y:
            self._scroll_down(rel_y - max_y)
        elif rel_y < 0:
            self._scroll_up(-rel_y)

        max_x = self.port_width - 1
        if (rel_x := x + self._pad.x) > max_x:
            self._scroll_right(rel_x - max_x)
        elif rel_x < 0:
            self._scroll_left(-rel_x)

        if self.is_selecting:
            self._selection_end = self.cursor

        self._highlight_selection()

    def _highlight_selection(self):
        colors = self._pad.colors
        colors[:] = self._pad.default_color_pair

        if self._selection_start != self._selection_end:
            if self._selection_start > self._selection_end:
                sy, sx = self._selection_end
                ey, ex = self._selection_start
            else:
                sy, sx = self._selection_start
                ey, ex = self._selection_end
            highlight = self.color_theme.pad_selection_highlight
            ll = self._line_lengths

            if ey == sy:
                colors[sy, sx:ex] = highlight
            else:
                colors[sy, sx : ll[sy]] = highlight
                colors[ey, :ex] = highlight
                for i in range(sy + 1, ey):
                    colors[i, : ll[i]] = highlight
        else:  # If no selection or selection is empty, add line highlight.
            colors[self.cursor.y, :] = self.color_theme.pad_line_highlight

    @property
    def is_selecting(self) -> bool:
        return self._selection_start is not None and self._selection_end is not None

    @property
    def has_nonempty_selection(self) -> bool:
        return self.is_selecting and self._selection_start != self._selection_end

    @property
    def end_text_point(self) -> Point:
        """
        Point after last character in text.
        """
        ll = self._line_lengths
        return Point(len(ll) - 1, ll[-1])

    @property
    def page_lines(self) -> int:
        return self.height - 2 - self.show_horizontal_bar

    def select(self):
        if not self.is_selecting:
            self._selection_start = self._selection_end = self.cursor

    def unselect(self):
        self._selection_start = self._selection_end = None

    def delete_selection(self):
        if self.has_nonempty_selection:
            return self._del_text(self._selection_start, self._selection_end)

    def _del_text(self, start: Point, end: Point):
        ll = self._line_lengths

        pad = self._pad
        canvas = pad.canvas

        if start > end:
            start, end = end, start

        sy, sx = start
        ey, ex = end

        # ! If one of the following conditions is true, something went wrong.
        if ey >= len(ll):
            ey = len(ll) - 1
        if ex > ll[ey]:
            ex = ll[ey]

        contents = "\n".join(
            "".join(
                canvas["char"][y, sx if y == sy else None : ex if y == ey else ll[y]]
            )
            for y in range(sy, ey + 1)
        )
        selection_start = self._selection_start
        selection_end = self._selection_end
        cursor = self.cursor

        len_end = ll[ey] - ex
        len_start = ll[sy] = sx + len_end
        if len_start >= pad.width:
            pad.width = len_start + 1

        canvas[sy, sx:len_start] = canvas[ey, ex : ex + len_end]
        canvas[sy, len_start:] = style_char(pad.default_char)

        remaining = canvas[ey + 1 :]
        canvas[sy + 1 : sy + 1 + len(remaining)] = remaining
        pad.height -= ey - sy

        del ll[sy + 1 : ey + 1]

        self.unselect()
        self._last_x = None
        self.cursor = start
        return self._add_text, [start, contents], selection_start, selection_end, cursor

    def _add_text(self, pos: Point, text: str):
        y, x = pos
        pad = self._pad
        ll = self._line_lengths
        line_remaining = pad.canvas[y, x : ll[y]].copy()

        selection_start = self._selection_start
        selection_end = self._selection_end
        cursor = self.cursor

        lines = text.split("\n")  # DO NOT USE `splitlines`.
        if len(lines) == 1:
            [line] = lines
            width_line = wcswidth(line)

            ll[y] += width_line
            if ll[y] >= pad.width:
                pad.width = ll[y] + 1

            pad.add_str(line, (y, x))
            pad.canvas[y, x + width_line : ll[y]] = line_remaining

            self.cursor = y, x + width_line
        else:
            first, *lines, last = lines
            newlines = len(lines) + 1
            width_last = wcswidth(last)
            last_y = y + newlines

            pad.height += newlines
            pad.canvas[y + newlines + 1 :] = pad.canvas[y + 1 : -newlines]
            pad.canvas[y, x : ll[y]] = style_char(pad.default_char)

            ll[y] = x + wcswidth(first)
            for i, line in enumerate(lines, start=y + 1):
                ll.insert(i, wcswidth(line))
            ll.insert(last_y, width_last + wcswidth("".join(line_remaining["char"])))

            max_width = max(ll)
            if max_width >= pad.width:
                pad.width = max_width + 1

            pad.add_str(first, (y, x))
            for i, line in enumerate(lines, start=y + 1):
                pad.add_str(line.ljust(pad.width), (i, 0))

            pad.add_str(last, (last_y, 0))
            pad.canvas[last_y, width_last : ll[last_y]] = line_remaining
            pad.canvas[last_y, ll[last_y] :] = style_char(pad.default_char)

            self.cursor = last_y, width_last

        return (
            self._del_text,
            [cursor, self.cursor],
            selection_start,
            selection_end,
            cursor,
        )

    def move_cursor_left(self, n: int = 1):
        self._last_x = None
        y, x = self._cursor.pos

        while n > 0:
            text_before_cursor = "".join(self._pad.canvas["char"][y, :x])
            nchars_before_cursor = len(text_before_cursor)
            if n <= nchars_before_cursor:
                x = wcswidth(text_before_cursor[:-n])
                break

            if y == 0:
                x = 0
                break

            y -= 1
            x = self._line_lengths[y]
            n -= nchars_before_cursor + 1

        self.cursor = y, x

    def move_cursor_right(self, n: int = 1):
        self._last_x = None
        y, x = self._cursor.pos

        while n > 0:
            text_after_cursor = "".join(
                self._pad.canvas["char"][y, x : self._line_lengths[y]]
            )
            nchars_after_cursor = len(text_after_cursor)
            if n <= nchars_after_cursor:
                x += wcswidth(text_after_cursor[:n])
                break

            if y == self.end_text_point.y:
                x = self._line_lengths[y]
                break

            y += 1
            n -= nchars_after_cursor + 1
            x = 0

        self.cursor = y, x

    def move_cursor_up(self, n: int = 1):
        y, x = self._cursor.pos

        if self._last_x is None or y == x == 0:
            self._last_x = x

        if y > 0:
            y = max(0, y - n)
            x = min(self._last_x, self._line_lengths[y])
        else:
            x = 0

        self.cursor = y, x

    def move_cursor_down(self, n: int = 1):
        y, x = self._cursor.pos
        ey, ex = self.end_text_point

        if self._last_x is None or y == ey and x == ex:
            self._last_x = x

        if y < ey:
            y = min(ey, y + n)
            x = min(self._last_x, self._line_lengths[y])
        else:
            x = ex

        self.cursor = y, x

    def move_word_left(self):
        last_x = self.cursor.x
        first_char_found = False
        while True:
            self.move_cursor_left()
            if self.cursor.x == last_x:
                break

            last_x = self.cursor.x

            current_char = self._pad.canvas[self.cursor]["char"]
            if not first_char_found:
                if not current_char.isspace():
                    first_char_found = True
                    is_word_char = current_char in WORD_CHARS
            elif current_char.isspace() or is_word_char != (current_char in WORD_CHARS):
                self.move_cursor_right()
                break

    def move_word_right(self):
        last_x = self.cursor.x
        first_char_found = False
        while True:
            self.move_cursor_right()
            if self.cursor.x == last_x:
                break

            last_x = self.cursor.x

            current_char = self._pad.canvas[self.cursor]["char"]
            if not first_char_found:
                if not current_char.isspace():
                    first_char_found = True
                    is_word_char = current_char in WORD_CHARS
            elif current_char.isspace() or is_word_char != (current_char in WORD_CHARS):
                break

    def _enter(self):
        self._move_undo_buffer_to_stack()
        undos = []
        if undo := self.delete_selection():
            undos.append(undo)
        undos.append(self._add_text(self.cursor, "\n"))
        self._undo_stack.append(undos)
        self._redo_stack.clear()

    def _tab(self):
        self._move_undo_buffer_to_stack()
        undos = []
        if undo := self.delete_selection():
            undos.append(undo)
        undos.append(self._add_text(self.cursor, "    "))
        self._undo_stack.append(undos)
        self._redo_stack.clear()

    def _backspace(self):
        if self.has_nonempty_selection:
            self._move_undo_buffer_to_stack("del")
            self._undo_buffer.append(self.delete_selection())
        else:
            if self._undo_buffer_type != "del":
                self._move_undo_buffer_to_stack("del")

            end = self.cursor
            self.move_cursor_left()
            start = self.cursor
            self.cursor = end
            if start != end:
                self._undo_buffer.append(self._del_text(start, end))

    def _delete(self):
        if self.has_nonempty_selection:
            self._move_undo_buffer_to_stack("del")
            self._undo_buffer.append(self.delete_selection())
        else:
            if self._undo_buffer_type != "del":
                self._move_undo_buffer_to_stack("del")

            start = self.cursor
            self.move_cursor_right()
            end = self.cursor
            self.cursor = start
            if start != end:
                self._undo_buffer.append(self._del_text(start, end))

    def _left(self):
        if self.has_nonempty_selection:
            select_start = min(self._selection_start, self._selection_end)
            self.unselect()
            self.cursor = select_start
        else:
            self.unselect()
            self.move_cursor_left()

    def _right(self):
        if self.has_nonempty_selection:
            select_end = max(self._selection_start, self._selection_end)
            self.unselect()
            self.cursor = select_end
        else:
            self.unselect()
            self.move_cursor_right()

    def _ctrl_left(self):
        self.unselect()
        self.move_word_left()

    def _ctrl_right(self):
        self.unselect()
        self.move_word_right()

    def _ctrl_a(self):
        """Select all."""
        self._selection_start = 0, 0
        self._selection_end = self.end_text_point
        self.cursor = self.end_text_point

    def _ctrl_d(self):
        """Select word."""
        self.unselect()
        last_x = self.cursor.x
        while True:
            self.move_cursor_left()
            if last_x == self.cursor.x:
                break
            if self._pad.canvas[self.cursor]["char"] not in WORD_CHARS:
                self.move_cursor_right()
                break
            last_x = self.cursor.x

        self.select()
        last_x = self.cursor.x
        while True:
            if self._pad.canvas[self.cursor]["char"] not in WORD_CHARS:
                break
            self.move_cursor_right()
            if last_x == self.cursor.x:
                break
            last_x = self.cursor.x

    def _up(self):
        if self.is_selecting:
            select_start = min(self._selection_start, self._selection_end)
            self.unselect()
            self.cursor = select_start
        self.move_cursor_up()

    def _down(self):
        if self.is_selecting:
            select_end = max(self._selection_start, self._selection_end)
            self.unselect()
            self.cursor = select_end
        self.move_cursor_down()

    def _pgup(self):
        if self.is_selecting:
            select_start = min(self._selection_start, self._selection_end)
            self.unselect()
            self.cursor = select_start
        self.move_cursor_up(self.page_lines)

    def _pgdn(self):
        if self.is_selecting:
            select_end = max(self._selection_start, self._selection_end)
            self.unselect()
            self.cursor = select_end
        self.move_cursor_down(self.page_lines)

    def _home(self):
        self.unselect()
        self.cursor = self.cursor.y, 0

    def _end(self):
        self.unselect()
        y = self.cursor.y
        self.cursor = y, self._line_lengths[y]

    def _shift_left(self):
        self.select()
        self.move_cursor_left()

    def _shift_right(self):
        self.select()
        self.move_cursor_right()

    def _shift_ctrl_left(self):
        self.select()
        self.move_word_left()

    def _shift_ctrl_right(self):
        self.select()
        self.move_word_right()

    def _shift_up(self):
        self.select()
        self.move_cursor_up()

    def _shift_down(self):
        self.select()
        self.move_cursor_down()

    def _shift_pgup(self):
        self.select()
        self.move_cursor_up(self.page_lines)

    def _shift_pgdn(self):
        self.select()
        self.move_cursor_down(self.page_lines)

    def _shift_home(self):
        self.select()
        self.cursor = self.cursor.y, 0

    def _shift_end(self):
        self.select()
        y = self.cursor.y
        self.cursor = y, self._line_lengths[y]

    def _escape(self):
        if self.has_nonempty_selection:
            self.unselect()
            self._highlight_selection()
        else:
            self.unselect()
            self.blur()

    def _ascii(self, key):
        if self.has_nonempty_selection:
            self._move_undo_buffer_to_stack("add")
            self._undo_buffer.append(self.delete_selection())
        elif self._undo_buffer_type != "add":
            self._move_undo_buffer_to_stack("add")
        self._undo_buffer.append(self._add_text(self.cursor, key))

    __HANDLERS = {
        (Key.Enter, Mods.NO_MODS): _enter,
        (Key.Tab, Mods.NO_MODS): _tab,
        (Key.Backspace, Mods.NO_MODS): _backspace,
        (Key.Delete, Mods.NO_MODS): _delete,
        (Key.Left, Mods.NO_MODS): _left,
        (Key.Right, Mods.NO_MODS): _right,
        (Key.Left, Mods(False, True, False)): _ctrl_left,
        (Key.Right, Mods(False, True, False)): _ctrl_right,
        (Key.Up, Mods.NO_MODS): _up,
        (Key.Down, Mods.NO_MODS): _down,
        (Key.PageUp, Mods.NO_MODS): _pgup,
        (Key.PageDown, Mods.NO_MODS): _pgdn,
        (Key.Home, Mods.NO_MODS): _home,
        (Key.End, Mods.NO_MODS): _end,
        (Key.Left, Mods(False, False, True)): _shift_left,
        (Key.Right, Mods(False, False, True)): _shift_right,
        (Key.Left, Mods(False, True, True)): _shift_ctrl_left,
        (Key.Right, Mods(False, True, True)): _shift_ctrl_right,
        (Key.Up, Mods(False, False, True)): _shift_up,
        (Key.Down, Mods(False, False, True)): _shift_down,
        (Key.PageUp, Mods(False, False, True)): _shift_pgup,
        (Key.PageDown, Mods(False, False, True)): _shift_pgdn,
        (Key.Home, Mods(False, False, True)): _shift_home,
        (Key.End, Mods(False, False, True)): _shift_end,
        (Key.Escape, Mods.NO_MODS): _escape,
        ("z", Mods(False, True, False)): undo,
        ("z", Mods(False, True, True)): redo,
        ("r", Mods(False, True, False)): redo,
        ("a", Mods(False, True, False)): _ctrl_a,
        ("d", Mods(False, True, False)): _ctrl_d,
    }

    def on_key(self, key_event: KeyEvent) -> bool | None:
        if not self.is_focused:
            return

        if key_event.mods == Mods.NO_MODS and len(key_event.key) == 1:
            self._ascii(key_event.key)
        elif handler := self.__HANDLERS.get(key_event):
            handler(self)
        else:
            return super().on_key(key_event)

        return True

    def on_paste(self, paste_event: PasteEvent) -> bool | None:
        if not self.is_focused:
            return

        self._move_undo_buffer_to_stack()
        undos = []
        if undo := self.delete_selection():
            undos.append(undo)
        undos.append(self._add_text(self.cursor, paste_event.paste))
        self._undo_stack.append(undos)
        self._redo_stack.clear()

        return True

    def grab(self, mouse_event):
        if mouse_event.button is MouseButton.LEFT and self._pad.collides_point(
            mouse_event.position
        ):
            super().grab(mouse_event)

            y, x = self._pad.to_local(mouse_event.position)
            x = min(x, self._line_lengths[y])

            if not mouse_event.mods.shift:
                self.unselect()

            self.cursor = y, x
            self.select()  # Need at least an empty selection for `grab_update`.

    def grab_update(self, mouse_event: MouseEvent):
        if self._pad.collides_point(mouse_event.position):
            y, x = self._pad.to_local(mouse_event.position)
            x = min(x, self._line_lengths[y])
            self.cursor = y, x
        else:
            cy, cx = self.cursor
            y, x = self.to_local(mouse_event.position)
            h, w = self.size

            if y < 0:
                self.move_cursor_up()
            elif y >= h:
                self.move_cursor_down()

            if x < 0:
                if cx > 0:
                    self.move_cursor_left()
            elif x >= w:
                if cx < self._line_lengths[cy]:
                    self.move_cursor_right()

    def ungrab(self, mouse_event):
        super().ungrab(mouse_event)
        if self._selection_start == self._selection_end:
            self.unselect()
