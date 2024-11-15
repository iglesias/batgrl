# Dependencies

- C++ compiler. I've developed this app using gcc 14, and used clang for another App one time too. It must be at least C++20 for including `<coroutine>`.
- `make` to build using the simple Makefile. The visibility-hidden and copy-dt... flags are related to pybind11.
- pybind11 and python dev files (the Makefile uses pkg-config to query their location).

Summarizing the compilation command, which can be used instead of the Makefile, should look like

```
$ g++ -std=c++20 -fvisibility=hidden -I/usr/include/python3.12 -Wl,--copy-dt-needed-entries -lpython3 main.cpp solver.cpp
```

and to run it, assuming after `make` for the executable's name

```
$ PYTHONPATH=../../../src bin/dumbo_octopus_animation
```
