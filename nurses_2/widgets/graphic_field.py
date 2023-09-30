"""
A graphic particle field.

A particle field specializes in handling many single "pixel" children.
"""
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ..colors import ColorPair
from .widget import (
    Char,
    Point,
    PosHint,
    PosHintDict,
    Size,
    SizeHint,
    SizeHintDict,
    Widget,
    style_char,
)

__all__ = [
    "GraphicParticleField",
    "Point",
    "PosHint",
    "PosHintDict",
    "Size",
    "SizeHint",
    "SizeHintDict",
]


class GraphicParticleField(Widget):
    """
    A graphic particle field.

    A particle field specializes in rendering many single "pixel" children by
    setting particle positions, colors, and alphas. (Note that alpha channel
    of particle colors and particle alphas are independent and both control
    particle transparency.) This is more efficient than rendering many 1x1 widgets.

    Parameters
    ----------
    particle_positions : NDArray[np.int32] | None, default: None
        Positions of particles. Expect int array with shape `N, 2`.
    particle_colors : NDArray[np.uint8] | None, default: None
        Colors of particles. Expect uint8 array with shape `N, 4`.
    particle_alphas : NDArray[np.float64] | None, default: None
        Alphas of particles. Expect float array of values between
        0 and 1 with shape `N,`.
    particle_properties : dict[str, NDArray[Any]] | None, default: None
        Additional particle properties.
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
    nparticles : int
        Number of particles in particle field.
    particle_positions : NDArray[np.int32]
        Positions of particles.
    particle_colors : NDArray[np.uint8]
        Colors of particles.
    particle_alphas : NDArray[np.float64]
        Alphas of particles.
    particle_properties : dict[str, NDArray[Any]]
        Additional particle properties.
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
        particle_positions: NDArray[np.int32] | None = None,
        particle_colors: NDArray[np.uint8] | None = None,
        particle_alphas: NDArray[np.float64] | None = None,
        particle_properties: dict[str, NDArray[Any]] = None,
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

        if particle_positions is None:
            self.particle_positions = np.zeros((0, 2), dtype=int)
        else:
            self.particle_positions = particle_positions

        if particle_colors is None:
            self.particle_colors = np.zeros(
                (len(self.particle_positions), 4), dtype=np.uint8
            )
        else:
            self.particle_colors = particle_colors

        if particle_alphas is None:
            self.particle_alphas = np.ones(len(self.particle_positions), dtype=np.float)
        else:
            self.particle_alphas = particle_alphas

        if particle_properties is None:
            self.particle_properties = {}
        else:
            self.particle_properties = particle_properties

    @property
    def nparticles(self) -> int:
        """
        Number of particles in particle field.
        """
        return len(self.particle_positions)

    def render(
        self,
        canvas_view: NDArray[Char],
        colors_view: NDArray[np.uint8],
        source: tuple[slice, slice],
    ):
        """
        Paint region given by `source` into `canvas_view` and `colors_view`.
        """
        vert_slice, hori_slice = source
        top = vert_slice.start
        height = vert_slice.stop - top
        left = hori_slice.start
        width = hori_slice.stop - left

        pos = self.particle_positions - (2 * top, left)
        where_inbounds = np.nonzero(
            (((0, 0) <= pos) & (pos < (2 * height, width))).all(axis=1)
        )
        local_ys, local_xs = pos[where_inbounds].T

        ch, cw, _ = colors_view.shape
        texture_view = (
            colors_view.reshape(ch, cw, 2, 3).swapaxes(1, 2).reshape(2 * ch, width, 3)
        )
        colors = self.particle_colors[where_inbounds]
        if not self.is_transparent:
            texture_view[local_ys, local_xs] = colors[..., :3]
        else:
            mask = canvas_view != style_char("▀")
            colors_view[..., :3][mask] = colors_view[..., 3:][mask]

            buffer = np.subtract(
                colors[:, :3], texture_view[local_ys, local_xs], dtype=float
            )
            buffer *= colors[:, 3, None]
            buffer *= self.particle_alphas[where_inbounds][:, None]
            buffer /= 255
            texture_view[local_ys, local_xs] = (
                buffer + texture_view[local_ys, local_xs]
            ).astype(np.uint8)

        colors_view[:] = (
            texture_view.reshape(height, 2, width, 3)
            .swapaxes(1, 2)
            .reshape(height, width, 6)
        )
        canvas_view[:] = style_char("▀")
        self.render_children(source, canvas_view, colors_view)
