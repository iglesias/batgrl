"""A scrollable view gadget."""

from ..colors import Color
from ..terminal.events import KeyEvent, MouseButton, MouseEvent
from ..text_tools import smooth_horizontal_bar, smooth_vertical_bar
from .behaviors.grabbable import Grabbable
from .behaviors.themable import Themable
from .gadget import (
    Gadget,
    Point,
    PosHint,
    Size,
    SizeHint,
    bindable,
    clamp,
)
from .pane import Pane
from .text import Text

__all__ = ["ScrollView", "Point", "Size"]


class _ScrollbarBase(Grabbable, Text):
    length: int

    def __init__(self):
        super().__init__(size=(1, 2))
        self.indicator_proportion: float = 1.0
        self.indicator_progress: float = 0.0
        self.is_hovered = False

    @property
    def indicator_proportion(self) -> float:
        return self._indicator_proportion

    @indicator_proportion.setter
    def indicator_proportion(self, indicator_porportion: float):
        self._indicator_proportion = indicator_porportion
        self._set_indicator_length()

    @property
    def fill_length(self) -> float:
        """The length the indicator can travel."""
        return self.length - self.indicator_length

    def paint_indicator(self) -> tuple[Color, int, float]:
        sv: ScrollView = self.parent

        if self.is_grabbed:
            indicator_color = sv.color_theme.scroll_view_indicator_press
        elif self.is_hovered:
            indicator_color = sv.color_theme.scroll_view_indicator_hover
        else:
            indicator_color = sv.color_theme.scroll_view_indicator_normal

        self.canvas["char"] = " "

        self.canvas["fg_color"] = indicator_color
        self.canvas["bg_color"] = sv.color_theme.scroll_view_scrollbar

        start, offset = divmod(self.indicator_progress * self.fill_length, 1)
        start = int(start)
        # Round offset to the nearest 1/8th.
        offset = round(offset * 8) / 8
        if offset == 1:
            offset -= 1
            start += 1

        return indicator_color, start, offset

    def ungrab(self, mouse_event):
        super().ungrab(mouse_event)
        self.paint_indicator()


class _VerticalScrollbar(_ScrollbarBase):
    @property
    def length(self) -> int:
        return self.height

    def _set_indicator_length(self):
        self.indicator_length = clamp(
            2, round(self.indicator_proportion * self.length), self.length
        )

    def paint_indicator(self):
        indicator_color, start, offset = super().paint_indicator()

        sv: ScrollView = self.parent
        smooth_bar = smooth_vertical_bar(
            self.indicator_length, 1, offset, reversed=True
        )
        stop = start + len(smooth_bar)
        self.canvas["char"][start:stop].T[:] = smooth_bar

        y_offset = offset != 0
        self.canvas["fg_color"][start + y_offset : stop] = (
            sv.color_theme.scroll_view_scrollbar
        )
        self.canvas["bg_color"][start + y_offset : stop] = indicator_color

    def on_mouse(self, mouse_event):
        old_hovered = self.is_hovered

        y, x = self.to_local(mouse_event.pos)
        start = round(self.indicator_progress * self.fill_length)
        self.is_hovered = 0 <= x < 2 and start <= y < start + self.indicator_length

        if super().on_mouse(mouse_event):
            return True

        if old_hovered != self.is_hovered:
            self.paint_indicator()

    def grab(self, mouse_event):
        super().grab(mouse_event)

        if self.is_hovered:
            self.paint_indicator()
        else:
            self.is_hovered = True

            sv: ScrollView = self.parent
            if self.fill_length == 0:
                sv.vertical_proportion = 0
            else:
                sv.vertical_proportion = self.to_local(mouse_event.pos).y / self.length

    def grab_update(self, mouse_event):
        sv: ScrollView = self.parent
        if self.fill_length == 0:
            sv.vertical_proportion = 0
        else:
            sv.vertical_proportion += mouse_event.dy / self.fill_length


class _HorizontalScrollbar(_ScrollbarBase):
    @property
    def length(self):
        return self.width

    def _set_indicator_length(self):
        self.indicator_length = clamp(
            4, round(self.indicator_proportion * self.length), self.length
        )

    def paint_indicator(self):
        indicator_color, start, offset = super().paint_indicator()

        sv: ScrollView = self.parent
        smooth_bar = smooth_horizontal_bar(self.indicator_length, 1, offset)
        self.canvas["char"][:, start : start + len(smooth_bar)] = smooth_bar
        if offset != 0:
            self.canvas["fg_color"][:, start] = sv.color_theme.scroll_view_scrollbar
            self.canvas["bg_color"][:, start] = indicator_color

    def on_mouse(self, mouse_event):
        old_hovered = self.is_hovered

        y, x = self.to_local(mouse_event.pos)
        start = round(self.indicator_progress * self.fill_length)
        self.is_hovered = y == 0 and start <= x < start + self.indicator_length

        if super().on_mouse(mouse_event):
            return True

        if old_hovered != self.is_hovered:
            self.paint_indicator()

    def grab(self, mouse_event):
        super().grab(mouse_event)
        if self.is_hovered:
            self.paint_indicator()
        else:
            self.is_hovered = True

            sv: ScrollView = self.parent
            if self.fill_length == 0:
                sv.horizontal_proportion = 0
            else:
                sv.horizontal_proportion = (
                    self.to_local(mouse_event.pos).x / self.length
                )

    def grab_update(self, mouse_event):
        sv: ScrollView = self.parent
        if self.fill_length == 0:
            sv.horizontal_proportion = 0
        else:
            sv.horizontal_proportion += mouse_event.dx / self.fill_length


class ScrollView(Themable, Grabbable, Gadget):
    r"""
    A scrollable view gadget.

    The view can be set with the :attr:`view` property, e.g.,
    ``my_scrollview.view = some_gadget``.

    Parameters
    ----------
    allow_vertical_scroll : bool, default: True
        Allow vertical scrolling.
    allow_horizontal_scroll : bool, default: True
        Allow horizontal scrolling.
    show_vertical_bar : bool, default: True
        Whether the vertical scrollbar is shown.
    show_horizontal_bar : bool, default: True
        Whether the horizontal scrollbar is shown.
    scrollwheel_enabled : bool, default: True
        Allow vertical scrolling with scrollwheel.
    arrow_keys_enabled : bool, default: True
        Allow scrolling with arrow keys.
    is_grabbable : bool, default: True
        If false, grabbable behavior is disabled.
    ptf_on_grab : bool, default: False
        If true, gadget will be pulled to front when grabbed.
    mouse_button : MouseButton, default: "left"
        Mouse button used for grabbing.
    alpha : float, default: 1.0
        Transparency of gadget.
    size : Size, default: Size(10, 10)
        Size of gadget.
    pos : Point, default: Point(0, 0)
        Position of upper-left corner in parent.
    size_hint : SizeHint | None, default: None
        Size as a proportion of parent's height and width.
    pos_hint : PosHint | None, default: None
        Position as a proportion of parent's height and width.
    is_transparent : bool, default: False
        Whether gadget is transparent.
    is_visible : bool, default: True
        Whether gadget is visible. Gadget will still receive input events if not
        visible.
    is_enabled : bool, default: True
        Whether gadget is enabled. A disabled gadget is not painted and doesn't receive
        input events.

    Attributes
    ----------
    view : Gadget | None
        The scrolled gadget.
    allow_vertical_scroll : bool
        Allow vertical scrolling.
    allow_horizontal_scroll : bool
        Allow horizontal scrolling.
    show_vertical_bar : bool
        Whether the vertical scrollbar is shown.
    show_horizontal_bar : bool
        Whether the horizontal scrollbar is shown.
    scrollwheel_enabled : bool
        Allow vertical scrolling with scrollwheel.
    arrow_keys_enabled : bool
        Allow scrolling with arrow keys.
    vertical_proportion : float
        Vertical scroll position as a proportion of total height.
    horizontal_proportion : float
        Horizontal scroll position as a proportion of total width.
    port_height : int
        Height of view.
    port_width : int
        Width of view.
    is_grabbable : bool
        If false, grabbable behavior is disabled.
    ptf_on_grab : bool
        If true, gadget will be pulled to front when grabbed.
    mouse_button : MouseButton
        Mouse button used for grabbing.
    is_grabbed : bool
        Whether gadget is grabbed.
    alpha : float
        Transparency of gadget.
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
    parent: Gadget | None
        Parent gadget.
    children : list[Gadget]
        Children gadgets.
    is_transparent : bool
        Whether gadget is transparent.
    is_visible : bool
        Whether gadget is visible.
    is_enabled : bool
        Whether gadget is enabled.
    root : Gadget | None
        If gadget is in gadget tree, return the root gadget.
    app : App
        The running app.

    Methods
    -------
    scroll_left(n=1)
        Scroll the view left `n` characters.
    scroll_right(n=1)
        Scroll the view right `n` characters.
    scroll_up(n=1)
        Scroll the view up `n` lines.
    scroll_down(n=1)
        Scroll the view down `n` lines.
    scroll_to_rect(pos, size=(1, 1))
        Scroll the view so that a given rect is visible.
    update_theme()
        Paint the gadget with current theme.
    grab(mouse_event)
        Grab the gadget.
    ungrab(mouse_event)
        Ungrab the gadget.
    grab_update(mouse_event)
        Update gadget with incoming mouse events while grabbed.
    on_size()
        Update gadget after a resize.
    apply_hints()
        Apply size and pos hints.
    to_local(point)
        Convert point in absolute coordinates to local coordinates.
    collides_point(point)
        Return true if point collides with visible portion of gadget.
    collides_gadget(other)
        Return true if other is within gadget's bounding box.
    add_gadget(gadget)
        Add a child gadget.
    add_gadgets(\*gadgets)
        Add multiple child gadgets.
    remove_gadget(gadget)
        Remove a child gadget.
    pull_to_front()
        Move to end of gadget stack so gadget is drawn last.
    walk_from_root()
        Yield all descendents of the root gadget (preorder traversal).
    walk()
        Yield all descendents of this gadget (preorder traversal).
    walk_reverse()
        Yield all descendents of this gadget (reverse postorder traversal).
    ancestors()
        Yield all ancestors of this gadget.
    bind(prop, callback)
        Bind `callback` to a gadget property.
    unbind(uid)
        Unbind a callback from a gadget property.
    on_key(key_event)
        Handle a key press event.
    on_mouse(mouse_event)
        Handle a mouse event.
    on_paste(paste_event)
        Handle a paste event.
    on_terminal_focus(focus_event)
        Handle a focus event.
    tween(...)
        Sequentially update gadget properties over time.
    on_add()
        Apply size hints and call children's `on_add`.
    on_remove()
        Call children's `on_remove`.
    prolicide()
        Recursively remove all children.
    destroy()
        Remove this gadget and recursively remove all its children.
    """

    def __init__(
        self,
        *,
        allow_vertical_scroll: bool = True,
        allow_horizontal_scroll: bool = True,
        show_vertical_bar: bool = True,
        show_horizontal_bar: bool = True,
        scrollwheel_enabled: bool = True,
        arrow_keys_enabled: bool = True,
        is_grabbable: bool = True,
        ptf_on_grab: bool = False,
        mouse_button: MouseButton = "left",
        alpha: float = 1.0,
        size: Size = Size(10, 10),
        pos: Point = Point(0, 0),
        size_hint: SizeHint | None = None,
        pos_hint: PosHint | None = None,
        is_transparent: bool = False,
        is_visible: bool = True,
        is_enabled: bool = True,
    ):
        self._corner = Pane(
            size=(1, 2),
            pos_hint={"y_hint": 1.0, "x_hint": 1.0, "anchor": "bottom-right"},
            is_enabled=show_horizontal_bar or show_vertical_bar,
            is_transparent=False,
        )
        self._background = Pane(size_hint={"height_hint": 1.0, "width_hint": 1.0})

        super().__init__(
            is_grabbable=is_grabbable,
            ptf_on_grab=ptf_on_grab,
            mouse_button=mouse_button,
            size=size,
            pos=pos,
            size_hint=size_hint,
            pos_hint=pos_hint,
            is_transparent=is_transparent,
            is_visible=is_visible,
            is_enabled=is_enabled,
        )
        self.allow_vertical_scroll = allow_vertical_scroll
        """Allow vertical scrolling."""
        self.allow_horizontal_scroll = allow_horizontal_scroll
        """Allow horizontal scrolling."""
        self.scrollwheel_enabled = scrollwheel_enabled
        """Allow vertical scrolling with scrollwheel."""
        self.arrow_keys_enabled = arrow_keys_enabled
        """Allow scrolling with arrow keys."""

        self._vertical_proportion = 0
        self._horizontal_proportion = 0

        self._vertical_bar = _VerticalScrollbar()
        self._horizontal_bar = _HorizontalScrollbar()
        self._view = None

        self.add_gadgets(
            self._background, self._corner, self._vertical_bar, self._horizontal_bar
        )

        self.show_horizontal_bar = show_horizontal_bar
        self.show_vertical_bar = show_vertical_bar
        self.alpha = alpha

    def update_theme(self):
        """Paint the gadget with current theme."""
        self._background.bg_color = self.color_theme.primary.bg
        self._corner.bg_color = self.color_theme.scroll_view_scrollbar
        self._update_port_and_scrollbar()

    @property
    def alpha(self) -> float:
        """Transparency of gadget."""
        return self._background.alpha

    @alpha.setter
    def alpha(self, alpha: float):
        self._background.alpha = alpha

    @property
    def is_transparent(self) -> bool:
        """Whether gadget is transparent."""
        return self._background.is_transparent

    @is_transparent.setter
    def is_transparent(self, is_transparent: bool):
        self._background.is_transparent = is_transparent

    @property
    def show_vertical_bar(self) -> bool:
        """Whether the vertical scrollbar is shown."""
        return self._vertical_bar.is_enabled

    @show_vertical_bar.setter
    @bindable
    def show_vertical_bar(self, show: bool):
        self._vertical_bar.is_enabled = show
        self._corner.is_enabled = show or self._horizontal_bar.is_enabled
        self.on_size()

    @property
    def show_horizontal_bar(self) -> bool:
        """Whether the horizontal scrollbar is shown."""
        return self._horizontal_bar.is_enabled

    @show_horizontal_bar.setter
    @bindable
    def show_horizontal_bar(self, show: bool):
        self._horizontal_bar.is_enabled = show
        self._corner.is_enabled = show or self._vertical_bar.is_enabled
        self.on_size()

    @property
    def vertical_proportion(self) -> float:
        """Vertical scroll position as a proportion of total height."""
        return self._vertical_proportion

    @vertical_proportion.setter
    @bindable
    def vertical_proportion(self, vertical_proportion: float):
        if self.allow_vertical_scroll:
            if self._view is None or self.total_vertical_distance <= 0:
                self._vertical_proportion = 0
            else:
                self._vertical_proportion = clamp(vertical_proportion, 0, 1)
            self._update_port_and_scrollbar()

    @property
    def horizontal_proportion(self) -> float:
        """Horizontal scroll position as a proportion of total width."""
        return self._horizontal_proportion

    @horizontal_proportion.setter
    @bindable
    def horizontal_proportion(self, horizontal_proportion: float):
        if self.allow_horizontal_scroll:
            if self._view is None or self.total_horizontal_distance <= 0:
                self._horizontal_proportion = 0
            else:
                self._horizontal_proportion = clamp(horizontal_proportion, 0, 1)
            self._update_port_and_scrollbar()

    @property
    def port_height(self) -> int:
        """Height of view."""
        return max(0, self.height - self.show_horizontal_bar)

    @property
    def port_width(self) -> int:
        """Width of view."""
        return max(0, self.width - self.show_vertical_bar * 2)

    @property
    def total_vertical_distance(self) -> int:
        """The distance the view can scroll vertically."""
        return 0 if self._view is None else max(0, self._view.height - self.port_height)

    @property
    def total_horizontal_distance(self) -> int:
        """The distance the view can scroll horizontally."""
        return 0 if self._view is None else max(0, self._view.width - self.port_width)

    def _update_port_and_scrollbar(self):
        """Move port and repaint scrollbar."""
        if self._view is None:
            self._vertical_bar.indicator_proportion = 1.0
            self._vertical_bar.indicator_progress = 0
            self._vertical_bar.paint_indicator()
            self._horizontal_bar.indicator_proportion = 1.0
            self._horizontal_bar.indicator_progress = 0
            self._horizontal_bar.paint_indicator()
        else:
            self._view.top = -round(
                self.vertical_proportion * self.total_vertical_distance
            )
            self._view.left = -round(
                self.horizontal_proportion * self.total_horizontal_distance
            )

            self._vertical_bar.indicator_proportion = clamp(
                self.port_height / self._view.height, 0, 1
            )
            self._vertical_bar.indicator_progress = self.vertical_proportion
            self._vertical_bar.paint_indicator()

            self._horizontal_bar.indicator_proportion = clamp(
                self.port_width / self._view.width, 0, 1
            )
            self._horizontal_bar.indicator_progress = self.horizontal_proportion
            self._horizontal_bar.paint_indicator()

    @property
    def view(self) -> Gadget | None:
        """The scrolled gadget."""
        return self._view

    @view.setter
    def view(self, view: Gadget | None):
        if self._view is not None:
            self.remove_gadget(self._view)

        self._view = view

        if view is not None:
            self.add_gadget(view)
            self.children.insert(1, self.children.pop())  # Move view below scrollbars.

            def update_proportion():
                y, x = self._view.pos
                h = self.total_vertical_distance
                w = self.total_horizontal_distance
                self.vertical_proportion = 0 if h == 0 else -y / h
                self.horizontal_proportion = 0 if w == 0 else -x / w

            self._view_uid = view.bind("size", update_proportion)
            self._update_port_and_scrollbar()

    def remove_gadget(self, gadget: Gadget):
        """Unbind from the view on its removal."""
        if gadget is self._view:
            self._view.unbind(self._view_uid)
            self._view = None
            del self._view_uid

        super().remove_gadget(gadget)

    def on_size(self):
        """Resize and reposition scrollbars on resize."""
        self._vertical_bar.height = self.height - self.show_horizontal_bar
        self._vertical_bar.left = self.width - 2
        self._horizontal_bar.width = self.width - 2 * self.show_vertical_bar
        self._horizontal_bar.top = self.height - 1
        self._update_port_and_scrollbar()

    def on_key(self, key_event: KeyEvent) -> bool | None:
        """Scroll on arrows keys."""
        if not self.arrow_keys_enabled:
            return False

        if key_event.key == "up":
            self.scroll_up()
        elif key_event.key == "down":
            self.scroll_down()
        elif key_event.key == "left":
            self.scroll_left()
        elif key_event.key == "right":
            self.scroll_right()
        else:
            return super().on_key(key_event)

        return True

    def grab_update(self, mouse_event: MouseEvent):
        """Scroll on grab update."""
        self.scroll_up(mouse_event.dy)
        self.scroll_left(mouse_event.dx)

    def on_mouse(self, mouse_event: MouseEvent) -> bool | None:
        """Scroll on mouse wheel."""
        if self.scrollwheel_enabled and self.collides_point(mouse_event.pos):
            if mouse_event.event_type == "scroll_up":
                self.scroll_up()
                return True
            elif mouse_event.event_type == "scroll_down":
                self.scroll_down()
                return True

        return super().on_mouse(mouse_event)

    def scroll_left(self, n=1):
        """Scroll the view left `n` characters."""
        if self._view is not None:
            if self.total_horizontal_distance == 0:
                self.horizontal_proportion = 0
            else:
                self.horizontal_proportion = clamp(
                    (-self.view.left - n) / self.total_horizontal_distance, 0, 1
                )

    def scroll_right(self, n=1):
        """Scroll the view right `n` characters."""
        self.scroll_left(-n)

    def scroll_up(self, n=1):
        """Scroll the view up `n` lines."""
        if self._view is not None:
            if self.total_vertical_distance == 0:
                self.vertical_proportion = 0
            else:
                self.vertical_proportion = clamp(
                    (-self.view.top - n) / self.total_vertical_distance, 0, 1
                )

    def scroll_down(self, n=1):
        """Scroll the view down `n` lines."""
        self.scroll_up(-n)

    def scroll_to_rect(self, pos: Point, size: Size = Size(1, 1)):
        """
        Scroll the view so that a given rect is visible.

        The rect is assumed to be within the view's bounding box.

        Parameters
        ----------
        pos : Point
            Position of rect.

        size : Size, default: Size(1, 1)
            Size of rect.
        """
        if self.view is None:
            return

        y, x = pos
        h, w = size
        gy, gx = self.view.pos
        ay, ax = gy + y, gx + x
        if ay < 0:
            self.scroll_up(-ay)
        elif ay + h >= self.port_height:
            self.scroll_down(ay + h - self.port_height)

        if ax < 0:
            self.scroll_left(-ax)
        elif ax + w >= self.port_width:
            self.scroll_right(ax + w - self.port_width)
