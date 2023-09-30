"""
A progress bar widget.
"""
import asyncio
from itertools import chain, cycle

from ..colors import WHITE_ON_BLACK, ColorPair
from .behaviors.themable import Themable
from .text_tools import smooth_horizontal_bar, smooth_vertical_bar
from .text_widget import (
    Point,
    PosHint,
    PosHintDict,
    Size,
    SizeHint,
    SizeHintDict,
    TextWidget,
    style_char,
)
from .widget import clamp, subscribable

__all__ = [
    "ProgressBar",
    "Point",
    "PosHint",
    "PosHintDict",
    "Size",
    "SizeHint",
    "SizeHintDict",
]


class ProgressBar(Themable, TextWidget):
    """
    A progress bar widget.

    Setting :attr:`progress` to `None` will start a "loading" animation; otherwise
    setting to a value between `0.0` and `1.0` will update the bar.

    Parameters
    ----------
    animation_delay : float, default: 1/60
        Time between loading animation updates.
    is_horizontal : bool, default: True
        If true, the bar will progress to the right, else the bar will progress upwards.
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
    progress : float | None
        Current progress as a value between `0.0` and `1.0` or `None. If `None`, then
        progress bar will start a "loading" animation.
    animation_delay : float
        Time between loading animation updates.
    is_horizontal : bool
        If true, the bar will progress to the right, else
        the bar will progress upwards.
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
    update_theme:
        Paint the widget with current theme.
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
        is_horizontal: bool = True,
        animation_delay: float = 1 / 60,
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
            default_char=default_char,
            default_color_pair=default_color_pair,
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
        self.animation_delay = animation_delay
        self._is_horizontal = is_horizontal
        self._progress = None

    @property
    def progress(self) -> float:
        return self._progress

    @progress.setter
    @subscribable
    def progress(self, progress: float):
        if getattr(self, "_loading_task", False):
            self._loading_task.cancel()

        if progress is None:
            self._progress = progress
            self._loading_task = asyncio.create_task(self._loading_animation())
        else:
            self._progress = clamp(progress, 0.0, 1.0)
            self._repaint_progress_bar()

    @property
    def is_horizontal(self) -> bool:
        return self._is_horizontal

    @is_horizontal.setter
    def is_horizontal(self, is_horizontal: bool):
        self._is_horizontal = is_horizontal
        self.progress = self.progress  # Trigger a repaint by setting property.

    def _paint_small_horizontal_bar(self, progress):
        bar_width = max(1, (self.width - 1) // 2)
        x, offset = divmod(progress * (self.width - bar_width), 1)
        x = int(x)
        smooth_bar = smooth_horizontal_bar(bar_width, 1, offset)

        self.canvas[:] = style_char(self.default_char)
        self.canvas["char"][:, x : x + len(smooth_bar)] = smooth_bar
        self.colors[:] = self.color_theme.progress_bar
        if offset != 0:
            self.colors[:, x] = self.color_theme.progress_bar.reversed()

    def _paint_small_vertical_bar(self, progress):
        bar_height = max(1, (self.height - 1) // 2)
        y, offset = divmod(progress * (self.height - bar_height), 1)
        y = int(y)
        smooth_bar = smooth_vertical_bar(bar_height, 1, offset)

        self.canvas[:] = style_char(self.default_char)
        try:
            self.canvas["char"][::-1][y : y + len(smooth_bar)].T[:] = smooth_bar
        except Exception as e:
            raise SystemExit(bar_height, progress, offset, smooth_bar) from e
        self.colors[:] = self.color_theme.progress_bar
        if offset != 0:
            self.colors[::-1][y] = self.color_theme.progress_bar.reversed()

    async def _loading_animation(self):
        if (
            self.is_horizontal
            and self.width < 3
            or not self.is_horizontal
            and self.height < 3
        ):
            return

        self.canvas[:] = style_char(self.default_char)

        if self._is_horizontal:
            HSTEPS = 8 * self.width
            for i in cycle(chain(range(HSTEPS + 1), range(HSTEPS)[::-1])):
                self._paint_small_horizontal_bar(i / HSTEPS)
                await asyncio.sleep(self.animation_delay)
        else:
            VSTEPS = 8 * self.height
            for i in cycle(chain(range(VSTEPS + 1), range(VSTEPS)[::-1])):
                self._paint_small_vertical_bar(i / VSTEPS)
                await asyncio.sleep(self.animation_delay)

    def on_add(self):
        super().on_add()
        self.progress = self.progress  # Trigger a repaint by setting property.

    def on_remove(self):
        super().on_remove()
        if task := getattr(self, "_loading_task", False):
            task.cancel()

    def on_size(self):
        super().on_size()
        self.progress = self.progress  # Trigger a repaint by setting property.

    def update_theme(self):
        self.colors[:] = self.color_theme.progress_bar
        self.default_color_pair = self.color_theme.progress_bar

    def _repaint_progress_bar(self):
        self.canvas[:] = style_char(self.default_char)
        if self.is_horizontal:
            smooth_bar = smooth_horizontal_bar(self.width, self.progress)
            self.canvas["char"][:, : len(smooth_bar)] = smooth_bar
        else:
            smooth_bar = smooth_vertical_bar(self.height, self.progress)
            self.canvas["char"][::-1][: len(smooth_bar)].T[:] = smooth_bar
