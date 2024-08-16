#pragma once

#include <coroutine>
#include <future>
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace asyncio {

class awaitable_t {
  public:
    awaitable_t() = default;
    awaitable_t(std::future<void>&& _future) : future(std::move(_future)) {};

    awaitable_t* await() { return this; }
    void next() {
        using namespace std::chrono_literals;
        auto status = this->future.wait_for(3ms);

        if (status == std::future_status::ready) {
            throw py::stop_iteration{};
        }
    }

    struct promise_type {
        awaitable_t get_return_object() {
            return awaitable_t(promise.get_future());
        }

        std::suspend_never initial_suspend() const noexcept { return {}; }
        std::suspend_never final_suspend()   const noexcept { return {}; }

        void return_void() const noexcept {}

        void unhandled_exception() {
            promise.set_exception(std::current_exception());
        }

      private:
        std::promise<void> promise;
    };

  private:
    std::future<void> future;
};

class py_awaiter_t {
  public:
    explicit py_awaiter_t(py::object a) : awaitable(std::move(a)) {
        if (awaitable.attr("__class__").attr("__name__").cast<std::string>() == "coroutine") {
            py::object asyncio = py::module_::import("asyncio");
            awaitable = asyncio.attr("create_task")(awaitable);
        }
    }

    bool await_ready() const {
        return awaitable.attr("done")().cast<bool>();
    }

    void await_suspend(std::coroutine_handle<> handle) const {
        awaitable.attr("add_done_callback")(py::cpp_function(
            [handle](py::object /* future */) {
                handle.resume();
            }
        ));
    }

    py::object await_resume() const {
        if (PyErr_Occurred()) {
            throw py::error_already_set();
        }
        return awaitable.attr("result")();
    }

  private:
    py::object awaitable;
};

inline py::class_<awaitable_t> enable_async(py::module m) {
    return py::class_<awaitable_t>(m, "awaitable_t")
        .def(py::init<>())
        .def("__await__", &awaitable_t::await)
        .def("__next__", &awaitable_t::next);
};

}  // asyncio namespace
