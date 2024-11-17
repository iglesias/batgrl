#include <array>
#include <future>

#include <pybind11/embed.h>
#include <pybind11/numpy.h>  // for py::array when creating cubes

#include "../Advent-of-Code-2021-day_11/asyncio.h"

using namespace pybind11::literals;

namespace py = pybind11;

constexpr std::array colors{"c9842a", "f50707", "0040ff"};

py::list get_cubes() {
    constexpr std::array cubes_xyz{0, 0, 0, 1, 1, 1, 2, 2, 2, -1, -1, 1};
    py::list cubes;
    py::object Cube = py::module::import("cube").attr("Cube");
    for (size_t i = 0; i < cubes_xyz.size() / 3; ++i)
        cubes.append(Cube(py::array(3, cubes_xyz.data() + 3 * i),
                          colors[i % colors.size()]));
    return cubes;
}

PYBIND11_EMBEDDED_MODULE(cubes, module)
{
    py::dict attributes;
    attributes["on_start"] = py::cpp_function(
        [](py::object self) -> asyncio::awaitable_t {
            py::object cube_renderer_t = py::module::import("cube_renderer").attr("CubeRenderer");
            py::object size_hint_t = py::module::import("batgrl.gadgets.gadget").attr("SizeHint");
            py::object renderer = cube_renderer_t("size_hint"_a=size_hint_t("height_hint"_a=1., "width_hint"_a=1.));
            renderer.attr("cubes") = get_cubes();
            self.attr("add_gadget")(renderer);
            std::future future = std::async(std::launch::async, [](){});
            return asyncio::awaitable_t(std::move(future));
        },
        py::is_method(py::none()));

    asyncio::enable_async(module);

    py::object app_t = py::module::import("batgrl.app").attr("App");
    py::object metaclass = py::reinterpret_borrow<py::object>((PyObject *) &PyType_Type);
    module.attr("CubesApp") = metaclass("CubesApp", py::make_tuple(app_t), attributes);
}

int main()
{
    py::scoped_interpreter guard{};
    py::object cubes_app_class = py::module_::import("cubes").attr("CubesApp");
    py::object cubes_app = cubes_app_class("title"_a="Cubes", "render_interval"_a=0.03);
    cubes_app.attr("run")();
}
