"""A toggle button gadget."""
from collections.abc import Callable, Hashable

from .behaviors.themable import Themable
from .behaviors.toggle_button_behavior import (
    ButtonState,
    ToggleButtonBehavior,
    ToggleState,
)
from .gadget import (
    Gadget,
    Point,
    PosHint,
    PosHintDict,
    Size,
    SizeHint,
    SizeHintDict,
)
from .pane import Pane
from .text import Text

__all__ = [
    "ButtonState",
    "Point",
    "PosHint",
    "PosHintDict",
    "Size",
    "SizeHint",
    "SizeHintDict",
    "ToggleButton",
    "ToggleState",
]

CHECK_OFF = "□ "
CHECK_ON = "▣ "
TOGGLE_OFF = "◯ "
TOGGLE_ON = "◉ "


class ToggleButton(Themable, ToggleButtonBehavior, Gadget):
    r"""
    A toggle button gadget.

    Without a group, a toggle button acts like a checkbox. With a group, it behaves like
    a radio button (only a single button in a group is allowed to be in the "on" state).

    Parameters
    ----------
    label : str, default: ""
        Toggle button label.
    callback : Callable[[ToggleState], None], default: lambda: None
        Called when toggle state changes. The new state is provided as first argument.
    group : None | Hashable, default: None
        If a group is provided, only one button in a group can be in the "on" state.
    allow_no_selection : bool, default: False
        If a group is provided, setting this to true allows no selection, i.e.,
        every button can be in the "off" state.
    toggle_state : ToggleState, default: ToggleState.OFF
        Initial toggle state of button.
    always_release : bool, default: False
        Whether a mouse up event outside the button will trigger it.
    alpha : float, default: 1.0
        Transparency of gadget.
    size : Size, default: Size(10, 10)
        Size of gadget.
    pos : Point, default: Point(0, 0)
        Position of upper-left corner in parent.
    size_hint : SizeHint | SizeHintDict | None, default: None
        Size as a proportion of parent's height and width.
    pos_hint : PosHint | PosHintDict | None , default: None
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
    label : str
        Toggle button label.
    callback : Callable[[ToggleState], None]
        Button callback when toggled.
    group : None | Hashable
        If a group is provided, only one button in a group can be in the "on" state.
    allow_no_selection : bool
        If true and button is in a group, every button can be in the "off" state.
    toggle_state : ToggleState
        Toggle state of button.
    always_release : bool
        Whether a mouse up event outside the button will trigger it.
    state : ButtonState
        Current button state. One of `NORMAL`, `HOVER`, `DOWN`.
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
    update_theme()
        Paint the gadget with current theme.
    update_off()
        Paint the "off" state.
    update_on()
        Paint the "on" state.
    on_toggle()
        Update gadget on toggle state change.
    update_normal()
        Paint the normal state.
    update_hover()
        Paint the hover state.
    update_down()
        Paint the down state.
    on_release()
        Triggered when a button is released.
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
        Handle key press event.
    on_mouse(mouse_event)
        Handle mouse event.
    on_paste(paste_event)
        Handle paste event.
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
        label: str = "",
        callback: Callable[[ToggleState], None] = lambda state: None,
        group: None | Hashable = None,
        allow_no_selection: bool = False,
        toggle_state: ToggleState = ToggleState.OFF,
        always_release: bool = False,
        alpha: float = 1.0,
        size=Size(10, 10),
        pos=Point(0, 0),
        size_hint: SizeHint | SizeHintDict | None = None,
        pos_hint: PosHint | PosHintDict | None = None,
        is_transparent: bool = False,
        is_visible: bool = True,
        is_enabled: bool = True,
    ):
        self._pane = Pane(size_hint={"height_hint": 1.0, "width_hint": 1.0})
        self._label = Text(
            pos_hint={"y_hint": 0.5, "anchor": "left"}, is_transparent=True
        )
        super().__init__(
            group=group,
            allow_no_selection=allow_no_selection,
            toggle_state=toggle_state,
            always_release=always_release,
            size=size,
            pos=pos,
            size_hint=size_hint,
            pos_hint=pos_hint,
            is_transparent=is_transparent,
            is_visible=is_visible,
            is_enabled=is_enabled,
        )
        self.add_gadgets(self._pane, self._label)
        self.label = label
        self.callback = callback
        self.alpha = alpha

    @property
    def is_transparent(self) -> bool:
        """Whether gadget is transparent."""
        return self._pane.is_transparent

    @is_transparent.setter
    def is_transparent(self, is_transparent: bool):
        self._pane.is_transparent = is_transparent

    @property
    def alpha(self) -> float:
        """Transparency of gadget."""
        return self._pane.alpha

    @alpha.setter
    def alpha(self, alpha: float):
        self._pane.alpha = alpha

    @property
    def label(self) -> str:
        """Toggle button label."""
        return self._label_text

    @label.setter
    def label(self, label: str):
        self._label_text = label

        if self.group is None:
            on, off = CHECK_ON, CHECK_OFF
        else:
            on, off = TOGGLE_ON, TOGGLE_OFF

        if self.toggle_state is ToggleState.ON:
            prefix = on
        else:
            prefix = off

        self._label.set_text(prefix + label)

    def update_theme(self):
        """Paint the gadget with current theme."""
        match self.state:
            case ButtonState.NORMAL:
                self.update_normal()
            case ButtonState.HOVER:
                self.update_hover()
            case ButtonState.DOWN:
                self.update_down()

    def update_normal(self):
        """Paint the normal state."""
        self._pane.bg_color = self.color_theme.button_normal.bg

    def update_hover(self):
        """Paint the hover state."""
        self._pane.bg_color = self.color_theme.button_hover.bg

    def update_down(self):
        """Paint the down state."""
        self._pane.bg_color = self.color_theme.button_press.bg

    def on_toggle(self):
        """Call callback on toggle state change."""
        if self.root:
            self.label = self.label  # Update radio button/checkbox
            self.callback(self.toggle_state)
