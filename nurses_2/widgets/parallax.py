"""
A parallax widget.
"""
from collections.abc import Iterable, Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ..colors import ColorPair
from .image import Image, Interpolation
from .widget import (
    Char,
    Point,
    PosHint,
    PosHintDict,
    Size,
    SizeHint,
    SizeHintDict,
    Widget,
    clamp,
    subscribable,
)

__all__ = [
    "Interpolation",
    "Parallax",
    "Point",
    "PosHint",
    "PosHintDict",
    "Size",
    "SizeHint",
    "SizeHintDict",
]


def _check_layer_speeds(layers, speeds):
    """
    Raise `ValueError` if `layers` and `speeds` are incompatible,
    else return a sequence of layer speeds.
    """
    nlayers = len(layers)
    if speeds is None:
        return [1 / (nlayers - i) for i in range(nlayers)]

    if len(speeds) != nlayers:
        raise ValueError("number of layers doesn't match number of layer speeds")

    return speeds


class Parallax(Widget):
    """
    A parallax widget.

    Parameters
    ----------
    path : Path | None, default: None
        Path to directory of images for layers of the parallax (loaded
        in lexographical order of filenames) layered from background to foreground.
    speeds : Sequence[float] | None, default: None
        The scrolling speed of each layer. Default speeds are `1/(N - i)`
        where `N` is the number of layers and `i` is the index of a layer.
    alpha : float, default: 1.0
        Transparency of the parallax.
    interpolation : Interpolation, default: "linear"
        Interpolation used when widget is resized.
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
    offset : tuple[float, float]
        Vertical and horizontal offset of first layer of the parallax. Other layers will
        be adjusted automatically.
    vertical_offset : float
        Vertical offset of first layer of the parallax.
    horizontal_offset : float
        Horizontal offset of first layer of the parallax
    alpha : float
        Transparency of the parallax.
    interpolation : Interpolation
        Interpolation used when widget is resized.
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
    from_textures:
        Create a :class:`Parallax` from an iterable of uint8 RGBA numpy array.
    from_images:
        Create a :class:`Parallax` from an iterable of :class:`Image`.
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
        path: Path | None = None,
        speeds: Sequence[float] | None = None,
        alpha: float = 1.0,
        interpolation: Interpolation = "linear",
        is_transparent: bool = True,
        size=Size(10, 10),
        pos=Point(0, 0),
        size_hint: SizeHint | SizeHintDict | None = None,
        pos_hint: PosHint | PosHintDict | None = None,
        is_visible: bool = True,
        is_enabled: bool = True,
        background_char: str | None = None,
        background_color_pair: ColorPair | None = None,
    ):
        if path is None:
            self.layers = []
        else:
            paths = sorted(path.iterdir(), key=lambda file: file.name)
            self.layers = [Image(path=path) for path in paths]

        super().__init__(
            is_transparent=is_transparent,
            size=size,
            pos=pos,
            size_hint=size_hint,
            pos_hint=pos_hint,
            is_visible=is_visible,
            is_enabled=is_enabled,
            background_char=background_char,
            background_color_pair=background_color_pair,
        )

        self.speeds = _check_layer_speeds(self.layers, speeds)
        self.alpha = alpha
        self.interpolation = interpolation

        self._vertical_offset = self._horizontal_offset = 0.0

    def on_size(self):
        for layer in self.layers:
            layer.size = self._size
        self._otextures = [layer.texture for layer in self.layers]

    @property
    def is_transparent(self) -> bool:
        """
        If false, `alpha` and alpha channels are ignored.
        """
        return self._is_transparent

    @is_transparent.setter
    def is_transparent(self, transparent: bool):
        self._is_transparent = transparent
        for layer in self.layers:
            layer.is_transparent = True

    @property
    def alpha(self) -> float:
        """
        Transparency of widget if :attr:`is_transparent` is true.
        """
        return self._alpha

    @alpha.setter
    @subscribable
    def alpha(self, alpha: float):
        self._alpha = clamp(float(alpha), 0.0, 1.0)
        for layer in self.layers:
            layer.alpha = alpha

    @property
    def interpolation(self) -> Interpolation:
        """
        Interpolation used when widget is resized.
        """
        return self._interpolation

    @interpolation.setter
    def interpolation(self, interpolation: Interpolation):
        if interpolation not in {"nearest", "linear", "cubic", "area", "lanczos"}:
            raise ValueError(f"{interpolation} is not a valid interpolation type.")
        for layer in self.layers:
            layer.interpolation = interpolation

    @property
    def vertical_offset(self) -> float:
        return self._vertical_offset

    @vertical_offset.setter
    def vertical_offset(self, offset: float):
        self._vertical_offset = offset
        self._adjust()

    @property
    def horizontal_offset(self) -> float:
        return self._horizontal_offset

    @horizontal_offset.setter
    def horizontal_offset(self, offset: float):
        self._horizontal_offset = offset
        self._adjust()

    @property
    def offset(self) -> tuple[float, float]:
        return self._vertical_offset, self._horizontal_offset

    @offset.setter
    def offset(self, offset: tuple[float, float]):
        self._vertical_offset, self._horizontal_offset = offset
        self._adjust()

    def _adjust(self):
        for speed, texture, layer in zip(
            self.speeds,
            self._otextures,
            self.layers,
        ):
            rolls = -round(speed * self._vertical_offset), -round(
                speed * self._horizontal_offset
            )
            layer.texture = np.roll(texture, rolls, axis=(0, 1))

    def render(
        self,
        canvas_view: NDArray[Char],
        colors_view: NDArray[np.uint8],
        source: tuple[slice, slice],
    ):
        for layer in self.layers:
            layer.render(canvas_view, colors_view, source)

        self.render_children(source, canvas_view, colors_view)

    @classmethod
    def from_textures(
        cls,
        textures: Iterable[NDArray[np.uint8]],
        *,
        speeds: Sequence[float] | None = None,
        alpha: float = 1.0,
        interpolation: Interpolation = "linear",
        is_transparent: bool = True,
        size=Size(10, 10),
        pos=Point(0, 0),
        size_hint: SizeHint | SizeHintDict | None = None,
        pos_hint: PosHint | PosHintDict | None = None,
        is_visible: bool = True,
        is_enabled: bool = True,
        background_char: str | None = None,
        background_color_pair: ColorPair | None = None,
    ) -> "Parallax":
        """
        Create an :class:`Parallax` from an iterable of uint8 RGBA numpy array.
        """
        parallax = cls(
            speeds=speeds,
            alpha=alpha,
            interpolation=interpolation,
            is_transparent=is_transparent,
            size=size,
            pos=pos,
            size_hint=size_hint,
            pos_hint=pos_hint,
            is_visible=is_visible,
            is_enabled=is_enabled,
            background_char=background_char,
            background_color_pair=background_color_pair,
        )
        parallax.layers = [
            Image.from_texture(
                texture,
                size=parallax.size,
                alpha=parallax.alpha,
                interpolation=parallax.interpolation,
            )
            for texture in textures
        ]
        parallax.speeds = _check_layer_speeds(parallax.layers, speeds)
        return parallax

    @classmethod
    def from_images(
        cls,
        images: Iterable[Image],
        *,
        speeds: Sequence[float] | None = None,
        alpha: float = 1.0,
        interpolation: Interpolation = "linear",
        is_transparent: bool = True,
        size=Size(10, 10),
        pos=Point(0, 0),
        size_hint: SizeHint | SizeHintDict | None = None,
        pos_hint: PosHint | PosHintDict | None = None,
        is_visible: bool = True,
        is_enabled: bool = True,
        background_char: str | None = None,
        background_color_pair: ColorPair | None = None,
    ) -> "Parallax":
        """
        Create an :class:`Parallax` from an iterable of :class:`Image`.
        """
        parallax = cls(
            speeds=speeds,
            alpha=alpha,
            interpolation=interpolation,
            is_transparent=is_transparent,
            size=size,
            pos=pos,
            size_hint=size_hint,
            pos_hint=pos_hint,
            is_visible=is_visible,
            is_enabled=is_enabled,
            background_char=background_char,
            background_color_pair=background_color_pair,
        )
        parallax.layers = list(images)
        for image in parallax.layers:
            image.interpolation = parallax.interpolation
            image.size = parallax.size
            image.alpha = parallax.alpha
        parallax.speeds = _check_layer_speeds(parallax.layers, speeds)
        return parallax
