from pathlib import Path

import cv2
import numpy as np

from .widget import Widget
from ..colors import BLACK_ON_BLACK


class ReloadTextureProperty:
    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return getattr(instance, self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        instance._load_texture()


class Image(Widget):
    """
    An Image widget.

    Notes
    -----
    Changing the path to an Image (or updating `is_grayscale` or `alpha_threshold`)
    will immediately reload the image.

    Parameters
    ----------
    path : pathlib.Path
        Path to image.
    is_grayscale : bool, default: False
        If true, convert image to grayscale.
    alpha_threshold : int, default: 0
        If Image is transparent and its texture has an alpha channel, alpha
        values less than or equal to alpha_threshold will be considered
        fully transparent. (0 <= alpha_threshold <= 255)
    """
    is_grayscale = ReloadTextureProperty()
    alpha_threshold = ReloadTextureProperty()
    path = ReloadTextureProperty()

    def __init__(self, *args, path: Path, is_grayscale=False, alpha_threshold=0, **kwargs):
        kwargs.pop('default_char', None)
        kwargs.pop('default_color', None)

        super().__init__(*args, default_char="▀", default_color=BLACK_ON_BLACK, **kwargs)

        self._is_grayscale = is_grayscale
        self._alpha_threshold = alpha_threshold
        self._path = path

        self._load_texture()

    def _load_texture(self):
        path = str(self.path)

        # Load unchanged to determine if there is an alpha channel.
        unchanged_texture = cv2.imread(path, cv2.IMREAD_UNCHANGED)

        if unchanged_texture.shape[-1] == 4:
            # `copy` because we want `unchanged_texture` to be garbage collected.
            self.alpha = unchanged_texture[:, :, -1].copy()
        else:
            self.alpha = None

        # Reload in BGR format.
        bgr_texture = cv2.imread(path, cv2.IMREAD_COLOR)
        if self.is_grayscale:
            grayscale = cv2.cvtColor(bgr_texture, cv2.COLOR_BGR2GRAY)
            self.texture = cv2.cvtColor(grayscale, cv2.COLOR_GRAY2RGB)
        else:
            self.texture = cv2.cvtColor(bgr_texture, cv2.COLOR_BGR2RGB)

        self.resize(self.dim)

    def resize(self, dim):
        """
        Resize image.
        """
        h, w = dim
        TEXTURE_DIM = w, 2 * h
        self.canvas = np.full(dim, self.default_char, dtype=object)
        self.colors = np.zeros((h, w, 6), dtype=np.uint8)

        if self.alpha is not None and self.is_transparent:
            self.where_visible = cv2.resize(self.alpha, TEXTURE_DIM) > self.alpha_threshold
        else:
            self.where_visible = None

        texture =  cv2.resize(self.texture, TEXTURE_DIM)
        self.colors[:, :, :3] = texture[::2]
        self.colors[:, :, 3:] = texture[1::2]

        for child in self.children:
            child.update_geometry()
