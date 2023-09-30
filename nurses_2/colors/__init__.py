"""
Color-related functions and data structures.
"""
from .color_types import AColor, Color, ColorPair, ColorTheme
from .colors import (
    ABLACK,
    ABLUE,
    ACYAN,
    AGREEN,
    AMAGENTA,
    ARED,
    AWHITE,
    AYELLOW,
    BLACK,
    BLACK_ON_BLACK,
    BLUE,
    CYAN,
    DEFAULT_COLOR_THEME,
    GREEN,
    MAGENTA,
    RED,
    TRANSPARENT,
    WHITE,
    WHITE_ON_BLACK,
    YELLOW,
)
from .gradients import gradient, lerp_colors, rainbow_gradient

__all__ = [
    "AColor",
    "Color",
    "ColorPair",
    "ColorTheme",
    "WHITE",
    "BLACK",
    "RED",
    "GREEN",
    "BLUE",
    "YELLOW",
    "CYAN",
    "MAGENTA",
    "AWHITE",
    "ABLACK",
    "ARED",
    "AGREEN",
    "ABLUE",
    "AYELLOW",
    "ACYAN",
    "AMAGENTA",
    "TRANSPARENT",
    "WHITE_ON_BLACK",
    "BLACK_ON_BLACK",
    "DEFAULT_COLOR_THEME",
    "rainbow_gradient",
    "lerp_colors",
    "gradient",
]
