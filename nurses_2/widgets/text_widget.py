"""
A text widget.
"""
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from wcwidth import wcswidth

from ..colors import WHITE_ON_BLACK, Color, ColorPair
from .text_tools import add_text
from .widget import (
    Anchor,
    Char,
    Easing,
    Point,
    PosHint,
    PosHintDict,
    Rect,
    Size,
    SizeHint,
    SizeHintDict,
    Widget,
    clamp,
    intersection,
    lerp,
    style_char,
    subscribable,
)

__all__ = [
    "Anchor",
    "Border",
    "Char",
    "Easing",
    "Point",
    "PosHint",
    "PosHintDict",
    "Rect",
    "Size",
    "SizeHint",
    "SizeHintDict",
    "TextWidget",
    "add_text",
    "clamp",
    "intersection",
    "lerp",
    "style_char",
    "subscribable",
]

Border = Literal[
    "light", "heavy", "double", "curved", "ascii", "outer", "inner", "thick"
]
"""Border styles for :meth:`nurses_2.text_widget.TextWidget.add_border`."""


class TextWidget(Widget):
    """
    A text widget. Displays arbitrary text data.

    Parameters
    ----------
    default_char : str, default: " "
        Default background character. This should be a single unicode half-width
        grapheme.
    default_color_pair : ColorPair, default: WHITE_ON_BLACK
        Default color of widget.
    size : Size, default: Size(10, 10)
        Size of widget.
    pos : Point, default: Point(0, 0)
        Position of upper-left corner in parent.
    size_hint : SizeHint | SizeHintDict | None, default: None
        Size as a proportion of parent's height and width.
    pos_hint : PosHint | PosHintDict | None , default: None
        Position as a proportion of parent's height and width.
    is_transparent : bool, default: False
        Whether :attr:`background_char` and :attr:`background_color_pair` are painted.
    is_visible : bool, default: True
        Whether widget is visible. Widget will still receive input events if not
        visible.
    is_enabled : bool, default: True
        Whether widget is enabled. A disabled widget is not painted and doesn't receive
        input events.
    background_char : str | None, default: None
        The background character of the widget if the widget is not transparent.
        Character must be single unicode half-width grapheme.
    background_color_pair : ColorPair | None, default: None
        The background color pair of the widget if the widget is not transparent.

    Attributes
    ----------
    canvas : NDArray[Char]
        The array of characters for the widget.
    colors : NDArray[np.uint8]
        The array of color pairs for each character in :attr:`canvas`.
    default_char : str
        Default background character.
    default_color_pair : ColorPair
        Default color pair of widget.
    default_fg_color : Color
        The default foreground color.
    default_bg_color : Color
        The default background color.
    size : Size
        Size of widget.
    height : int
        Height of widget.
    rows : int
        Alias for :attr:`height`.
    width : int
        Width of widget.
    columns : int
        Alias for :attr:`width`.
    pos : Point
        Position of upper-left corner.
    top : int
        Y-coordinate of top of widget.
    y : int
        Y-coordinate of top of widget.
    left : int
        X-coordinate of left side of widget.
    x : int
        X-coordinate of left side of widget.
    bottom : int
        Y-coordinate of bottom of widget.
    right : int
        X-coordinate of right side of widget.
    center : Point
        Position of center of widget.
    absolute_pos : Point
        Absolute position on screen.
    size_hint : SizeHint
        Size as a proportion of parent's height and width.
    pos_hint : PosHint
        Position as a proportion of parent's height and width.
    background_char : str | None
        The background character of the widget if the widget is not transparent.
    background_color_pair : ColorPair | None
        Background color pair.
    parent : Widget | None
        Parent widget.
    children : list[Widget]
        Children widgets.
    is_transparent : bool
        True if widget is transparent.
    is_visible : bool
        True if widget is visible.
    is_enabled : bool
        True if widget is enabled.
    root : Widget | None
        If widget is in widget tree, return the root widget.
    app : App
        The running app.

    Methods
    -------
    add_border:
        Add a border to the widget.
    add_str:
        Add a single line of text to the canvas.
    set_text:
        Resize widget to fit text, erase canvas, then fill canvas with text.
    on_size:
        Called when widget is resized.
    apply_hints:
        Apply size and pos hints.
    to_local:
        Convert point in absolute coordinates to local coordinates.
    collides_point:
        True if point collides with an uncovered portion of widget.
    collides_widget:
        True if other is within widget's bounding box.
    add_widget:
        Add a child widget.
    add_widgets:
        Add multiple child widgets.
    remove_widget:
        Remove a child widget.
    pull_to_front:
        Move to end of widget stack so widget is drawn last.
    walk_from_root:
        Yield all descendents of root widget.
    walk:
        Yield all descendents (or ancestors if `reverse` is true).
    subscribe:
        Subscribe to a widget property.
    unsubscribe:
        Unsubscribe to a widget property.
    on_key:
        Handle key press event.
    on_mouse:
        Handle mouse event.
    on_paste:
        Handle paste event.
    tween:
        Sequentially update a widget property over time.
    on_add:
        Called after a widget is added to widget tree.
    on_remove:
        Called before widget is removed from widget tree.
    prolicide:
        Recursively remove all children.
    destroy:
        Destroy this widget and all descendents.
    """

    def __init__(
        self,
        *,
        default_char: str = " ",
        default_color_pair: ColorPair = WHITE_ON_BLACK,
        size=Size(10, 10),
        pos=Point(0, 0),
        size_hint: SizeHint | SizeHintDict | None = None,
        pos_hint: PosHint | PosHintDict | None = None,
        is_transparent: bool = False,
        is_visible: bool = True,
        is_enabled: bool = True,
        background_char: str | None = None,
        background_color_pair: ColorPair | None = None,
    ):
        super().__init__(
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

        size = self.size

        self.canvas = np.full(size, style_char(default_char))
        self.colors = np.full((*size, 6), default_color_pair, dtype=np.uint8)

        self.default_char = default_char
        self.default_color_pair = default_color_pair

    def on_size(self):
        # Preserve content as much as possible.
        old_h, old_w = self.canvas.shape

        h, w = self._size

        old_canvas = self.canvas
        old_colors = self.colors

        copy_h = min(old_h, h)
        copy_w = min(old_w, w)

        self.canvas = np.full((h, w), style_char(self.default_char))
        self.colors = np.full((h, w, 6), self.default_color_pair, dtype=np.uint8)

        self.canvas[:copy_h, :copy_w] = old_canvas[:copy_h, :copy_w]
        self.colors[:copy_h, :copy_w] = old_colors[:copy_h, :copy_w]

    @property
    def default_fg_color(self) -> Color:
        """
        The default foreground color.
        """
        return self.default_color_pair.fg_color

    @property
    def default_bg_color(self) -> Color:
        return self.default_color_pair.bg_color

    def add_border(
        self,
        style: Border = "light",
        bold: bool = False,
        color_pair: ColorPair | None = None,
    ):
        """
        Add a text border.

        Parameters
        ----------
        style : Border, default: "light"
            Style of border. Default style uses light box-drawing characters.
        bold : bool, default: False
            Whether the border is bold.
        color_pair : ColorPair | None, default: None
            Border color pair if not None.
        """
        BORDER_STYLES = dict(
            light="┌┐││──└┘",
            heavy="┏┓┃┃━━┗┛",
            double="╔╗║║══╚╝",
            curved="╭╮││──╰╯",
            ascii="++||--++",
            outer="▛▜▌▐▀▄▙▟",
            inner="▗▖▐▌▄▀▝▘",
            thick="████▀▄██",
        )
        tl, tr, lv, rv, th, bh, bl, br = BORDER_STYLES[style]

        canvas = self.canvas
        canvas[0, 0] = style_char(tl, bold=bold)
        canvas[0, -1] = style_char(tr, bold=bold)
        canvas[1:-1, 0] = style_char(lv, bold=bold)
        canvas[1:-1, -1] = style_char(rv, bold=bold)
        canvas[0, 1:-1] = style_char(th, bold=bold)
        canvas[-1, 1:-1] = style_char(bh, bold=bold)
        canvas[-1, 0] = style_char(bl, bold=bold)
        canvas[-1, -1] = style_char(br, bold=bold)

        if color_pair is not None:
            self.colors[[0, -1]] = color_pair
            self.colors[:, [0, -1]] = color_pair

    def add_str(
        self,
        str: str,
        pos: Point = Point(0, 0),
        *,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strikethrough: bool = False,
        overline: bool = False,
        truncate_str: bool = False,
    ):
        """
        Add a single line of text to the canvas at position `pos`.

        Parameters
        ----------
        str : str
            A single line of text to add to canvas.
        pos : Point, default: Point(0, 0)
            Position of first character of string. Negative coordinates position
            from the right or bottom of canvas (like negative indices).
        bold : bool, default: False
            Whether text is bold.
        italic : bool, default: False
            Whether text is italic.
        underline : bool, default: False
            Whether text is underlined.
        strikethrough : bool, default: False
            Whether text is strikethrough.
        overline : bool, default: False
            Whether text is overlined.
        truncate_str : bool, default: False
            If false, an `IndexError` is raised if the text would not fit on canvas.

        See Also
        --------
        text_widget.add_text : Add multiple lines of text to a view of a canvas.
        """
        y, x = pos
        add_text(
            self.canvas[y, x:],
            str,
            bold=bold,
            italic=italic,
            underline=underline,
            strikethrough=strikethrough,
            overline=overline,
            truncate_text=truncate_str,
        )

    def set_text(
        self,
        text: str,
        *,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strikethrough: bool = False,
        overline: bool = False,
    ):
        """
        Resize widget to fit text, erase canvas, then fill canvas with text.

        Parameters
        ----------
        text : str
            Text to add to canvas.
        bold : bool, default: False
            Whether text is bold.
        italic : bool, default: False
            Whether text is italic.
        underline : bool, default: False
            Whether text is underlined.
        strikethrough : bool, default: False
            Whether text is strikethrough.
        overline : bool, default: False
            Whether text is overlined.

        See Also
        --------
        text_widget.add_text : Add multiple lines of text to a view of a canvas.
        """
        lines = text.splitlines()
        height = len(lines)
        width = max(map(wcswidth, lines), default=0)
        self.size = height, width
        self.canvas[:] = style_char(self.default_char)
        add_text(
            self.canvas,
            text,
            bold=bold,
            italic=italic,
            underline=underline,
            strikethrough=strikethrough,
            overline=overline,
        )

    def render(
        self,
        canvas_view: NDArray[Char],
        colors_view: NDArray[np.uint8],
        source: tuple[slice, slice],
    ):
        """
        Paint region given by source into canvas_view and colors_view.
        """
        if self.is_transparent:
            source_view = self.canvas[source]
            visible = np.isin(source_view["char"], (" ", "⠀"), invert=True)

            canvas_view[visible] = source_view[visible]
            colors_view[..., :3][visible] = self.colors[..., :3][source][visible]
        else:
            canvas_view[:] = self.canvas[source]
            colors_view[:] = self.colors[source]

        self.render_children(source, canvas_view, colors_view)
