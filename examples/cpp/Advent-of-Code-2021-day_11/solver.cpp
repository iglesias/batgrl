#include "solver.h"

#include <array>
#include <queue>

int step(std::vector<std::string>& levels) {
    const int R = static_cast<int>(levels.size());
    const int C = static_cast<int>(levels.at(0).length());
    std::queue<std::pair<int, int>> Q;
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++)
        Q.emplace(r, c);
    int num_flashes = 0;
    while (!Q.empty()) {
        const auto [r, c] = Q.front();
        Q.pop();
        if (levels[r][c] == '9') {
            num_flashes++;
            for (int dr : std::array{-1, 0, 1})
                for (int dc : std::array{-1, 0, 1}) {
                    if (!dr and !dc) continue;
                    if (0 <= r + dr and r + dr < R and
                        0 <= c + dc and c + dc < C)
                        Q.emplace(r + dr, c + dc);
                }
        }
        levels[r][c]++;
    }
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++)
        if (levels[r][c] > '9') levels[r][c] = '0';
    return num_flashes;
}
