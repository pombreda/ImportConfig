"""Base ``ImportConfig`` class.

ImportConfig can be subclassed for use with parsers that has a function called
``load`` to load file-like objects and parse them into python objects.
"""

from __future__ import print_function, unicode_literals

import collections
import os

from .exceptions import InvalidFilePathError


class ImportConfig(object):

    """Base class for YamlConfig and JsonConfig."""

    def __init__(self, loader, file_path, lazy=False):
        """ImportConfig constructor."""
        self.loader = loader
        self.file_path = os.path.abspath(file_path)
        self._file_root, _ = os.path.split(self.file_path)
        self.object = {}
        self.config = {}
        if not lazy:
            self.object = self._get_file_path(self.loader, self.file_path)
            self.config = self._expand(self.object)

    @staticmethod
    def _get_file_path(loader, file_path, file_root=None):
        """Check the file path and return the JSON loaded as a dict.

        Arguments:
            file_path (``str``): Path to the file to load
            file_root (``str``): If provided the method will use ``file_root``
                as a fallback before raising an ``InvalidFilePathError``

        Returns:
            ``dict``

        Raises:
            ``InvalidFilePathError``
        """
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                return loader.load(f)
        elif file_root:
            with open(os.path.join(file_root, file_path), 'r') as f:
                return loader.load(f)
        raise InvalidFilePathError('{} is not a file!'.format(file_path))

    def _expand(self, d):
        """Iterate on the config object and find @file keys.

        Returns:
            ``dict``
        """
        result = {}
        for k, v in d.items():
            if k == '@file':
                contents = self._get_file_path(self.loader, v,
                                               file_root=self._file_root)
                result.update(contents)
            elif isinstance(v, collections.MutableMapping):
                # v and the result of _expand should be merged
                # with results' values taking precedence :*
                result[k] = self._expand(v)
            else:
                result[k] = v
        return result

    def load(self):
        """Loads up the expanded configuration.

        Returns:
            ``dict``
        """
        if not self.object:
            self.object = self._get_file_path(self.loader, self.file_path)
            self.config = self._expand(self.object)
            return self.config
        return self.config
