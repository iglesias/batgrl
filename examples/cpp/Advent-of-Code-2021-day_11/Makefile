CXXFLAGS += -std=c++20 -fvisibility=hidden $(shell pkg-config --cflags python3) -Wall -Wextra -pedantic -Wconversion -Wfatal-errors -Wstrict-overflow -O2 # -fsanitize=address -ggdb

.PHONY: all clean

all: bin/solver.o bin/dumbo_octopus_animation

bin/solver.o: solver.cpp
	g++ $(CXXFLAGS) -c solver.cpp -o bin/solver.o

bin/dumbo_octopus_animation: main.cpp bin/solver.o
	g++ $(CXXFLAGS) -Wl,--copy-dt-needed-entries -lpython3 main.cpp -o bin/dumbo_octopus_animation bin/solver.o

clean:
	rm -rf bin/*.o bin/dumbo_octopus_animation
