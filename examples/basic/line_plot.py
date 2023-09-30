import numpy as np

from nurses_2.app import App
from nurses_2.colors import DEFAULT_COLOR_THEME
from nurses_2.widgets.line_plot import LinePlot
from nurses_2.widgets.toggle_button import ToggleButton
from nurses_2.widgets.widget import Widget

XS = np.arange(20)
YS_1 = np.random.randint(0, 100, 20)
YS_2 = np.random.randint(0, 100, 20)
YS_3 = np.random.randint(0, 100, 20)


class PlotApp(App):
    async def on_start(self):
        BUTTON_WIDTH = 15

        plot = LinePlot(
            xs=[XS, XS, XS],
            ys=[YS_1, YS_2, YS_3],
            x_label="X Values",
            y_label="Y Values",
            legend_labels=["Before", "During", "After"],
            size_hint={"height_hint": 1.0, "width_hint": 1.0},
            background_color_pair=DEFAULT_COLOR_THEME.primary,
        )

        def set_box_mode(toggle_state):
            if toggle_state == "on":
                plot.mode = "box"

        def set_braille_mode(toggle_state):
            if toggle_state == "on":
                plot.mode = "braille"

        box_button = ToggleButton(
            size=(1, BUTTON_WIDTH), label="Box Mode", callback=set_box_mode, group=0
        )
        braille_button = ToggleButton(
            size=(1, BUTTON_WIDTH),
            pos=(1, 0),
            label="Braille Mode",
            callback=set_braille_mode,
            group=0,
        )

        container = Widget(
            size=(2, BUTTON_WIDTH), pos_hint={"x_hint": 1.0, "anchor": "top-right"}
        )
        container.add_widgets(box_button, braille_button)
        self.add_widgets(plot, container)


if __name__ == "__main__":
    PlotApp(title="Line Plot Example").run()
