#include <cstdlib>
#include <ctime>
#include <pybind11/embed.h>
#include <string>
#include <vector>

#include "asyncio.h"
#include "solver.h"

using namespace pybind11::literals;

namespace py = pybind11;

namespace dumbo_octopus_animation {

const int max_grid_size = 20;

// Multiplier for the width of the grid (or number of columns) I found
// to work well to display in full screen with $COLUMNS=127.
const int X = 6;

void add_blank_grid(py::object text_gadget) {
    const py::object gadget_module = py::module::import("batgrl.gadgets.gadget");
    for (int row = 0 + 1; row < max_grid_size + 1; row++)
        text_gadget.attr("add_str")(std::string(X * max_grid_size + 1, ' '),
                                    "pos"_a=gadget_module.attr("Point")(row, 0));
}

// oeps, non-const global
std::vector<std::string> levels;

void add_random_grid(py::object text_gadget, const int grid_size) {
    levels.clear();
    levels.reserve(grid_size);
    const py::object gadget_module = py::module::import("batgrl.gadgets.gadget");
    for (int row = 0 + 1; row < std::min(max_grid_size, grid_size) + 1; row++) {
        levels.push_back("");
        std::string text{""};
        for (int col = 0 + 1; col < grid_size + 1; col++) {
            const char c = char(std::rand() % 10 + '0');
            if (true or c != '0') text.append(1, c);
            else          text += "**0**";
            levels[levels.size() - 1] += std::string(1, c);
        }
        text_gadget.attr("add_str")(text, "pos"_a=gadget_module.attr("Point")(row, 0)/* , "markdown"_a=true */);
    }
}

void add_next_grid_text(py::object text_gadget) {
    step(levels);
    const py::object gadget_module = py::module::import("batgrl.gadgets.gadget");
    for (size_t row = 0 + 1; row < levels.size() + 1; row++) {
        std::string text{" "};
        for (const char c : levels[row - 1]) {
            if (true or c != '0') text.append(1, c);
            else          text += "**0**";
        }
        text_gadget.attr("add_str")(text, "pos"_a=gadget_module.attr("Point")(row, 0)/*, "markdown"_a=true*/);
    }
}

}  // namespace dumbo_octopus_animation


asyncio::py_awaiter_t operator co_await(py::object coro) {
    return asyncio::py_awaiter_t(std::move(coro));
}

PYBIND11_EMBEDDED_MODULE(dumbo_octopus, module) {
    py::dict app_attr;
    app_attr["on_start"] = py::cpp_function(
        [](py::object self) -> asyncio::awaitable_t {
            using namespace dumbo_octopus_animation;
            int grid_size = 14;
            const py::object text_gadget_module = py::module::import("batgrl.gadgets.text");
            const py::object text_gadget_t = text_gadget_module.attr("Text");
            const py::object pos_hint_t = py::module::import("batgrl.gadgets.gadget").attr("PosHint");
            const py::object batgrl_size_t = py::module::import("batgrl.gadgets.pane").attr("Size");
            const py::object text_gadget = 
                text_gadget_t("size"_a=batgrl_size_t(max_grid_size + 2, X * max_grid_size + 2),
                              "pos_hint"_a=pos_hint_t("y_hint"_a=.5, "x_hint"_a=.5));

            const py::object colors = py::module::import("batgrl.colors");
            text_gadget.attr("default_fg_color") = colors.attr("WHITE");
            text_gadget.attr("default_bg_color") = colors.attr("BLACK");
            add_random_grid(text_gadget, grid_size);
            text_gadget.attr("add_border")();
            self.attr("add_gadget")(text_gadget);

            const py::object slider_module = py::module::import("batgrl.gadgets.slider");
            const py::object slider_t = slider_module.attr("Slider");
            auto on_slider_change = [text_gadget, &grid_size](py::object slider_value) {
                                        add_blank_grid(text_gadget);
                                        grid_size = static_cast<int>(std::round(slider_value.cast<float>()));
                                        add_random_grid(text_gadget, grid_size);
                                        text_gadget.attr("add_border")(); };
            const int slider_height{1};
            const int slider_width{120};
            py::object slider = slider_t("size"_a=batgrl_size_t(slider_height, slider_width),
                                         "pos_hint"_a=pos_hint_t("y_hint"_a=.02, "x_hint"_a=0.5),
                                         "min"_a=1., "max"_a=1.*X*max_grid_size,
                                         "start_value"_a=1.*grid_size,
                                         "callback"_a=py::cpp_function(on_slider_change));
            self.attr("add_gadget")(slider);

            py::object asyncio = py::module::import("asyncio");
            for (;;) {
                add_next_grid_text(text_gadget);
                text_gadget.attr("add_border")();
                co_await asyncio.attr("sleep")(0.1);
            }

            co_return;
        },
        py::is_method(py::none()));

    asyncio::enable_async(module);

    py::object app_t = py::module::import("batgrl.app").attr("App");
    py::object metaclass = py::reinterpret_borrow<py::object>((PyObject *) &PyType_Type);
    module.attr("DumboOctopusApp") = metaclass("DumboOctopusApp", py::make_tuple(app_t), app_attr);
}

int main() {
    py::scoped_interpreter guard{};
    py::object dumbo_octopus_app_class = py::module_::import("dumbo_octopus").attr("DumboOctopusApp");
    py::object dumbo_octopus_app = dumbo_octopus_app_class("title"_a="Dumbo Octopus", "render_interval"_a=0.1);
    std::srand(static_cast<unsigned int>(std::time(nullptr)));
    dumbo_octopus_app.attr("run")();
}
