from functools import partial

import numpy as np

from nurses_2.colors import color_pair, ABLACK
from nurses_2.io import MouseButton
from nurses_2.data_structures import Size
from nurses_2.widgets.text_widget import TextWidget, Anchor
from nurses_2.widgets.graphic_widget import GraphicWidget

from .element_buttons import MENU_BACKGROUND_COLOR, ButtonContainer
from .particles import Air

@partial(np.vectorize, otypes=[np.uint8, np.uint8, np.uint8])
def particles_to_colors(particle):
    """
    Convert array of particles to array of colors.
    """
    return particle.COLOR


class Sandbox(GraphicWidget):
    """
    Sandbox widget.
    """
    def __init__(self, size: Size):
        super().__init__(size=size, anchor=Anchor.CENTER, pos_hint=(.5, .5), default_color=ABLACK)

        # Build array of particles -- Initially all Air
        self.world = world = np.full((2 * self.height, self.width), None, dtype=object)
        for y in range(2 * self.height):
            for x in range(self.width):
                world[y, x] = Air(world, (y, x))

        # Add children widgets
        self.display = TextWidget(
            size=(1, 9),
            pos=(1, 0),
            anchor=Anchor.CENTER,
            pos_hint=(None, 0.5),
            default_color_pair=color_pair(Air.COLOR, MENU_BACKGROUND_COLOR),
        )
        self.add_widgets(self.display, ButtonContainer())

        # Press the Stone button setting particle type.
        self.children[1].children[1].on_release()

    def render(self, canvas_view, colors_view, source_slice: tuple[slice, slice]):
        # Color of each particle in `self.world` is written into color array.
        self.texture[..., :3] = np.dstack(particles_to_colors(self.world))
        super().render(canvas_view, colors_view, source_slice)

    def on_click(self, mouse_event):
        if (
            mouse_event.button != MouseButton.LEFT
            or not self.collides_point(mouse_event.position)
        ):
            return

        world = self.world
        particle_type = self.particle_type
        y, x = self.to_local(mouse_event.position)

        world[2 * y, x].replace(particle_type)
        world[2 * y + 1, x].replace(particle_type)

        return True
