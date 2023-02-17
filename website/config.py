import configparser
import json
from abc import abstractmethod
from pathlib import Path
from typing import Union


def _parse(inp: str):
    if not inp:  # empty, so treat as string
        return inp

    if inp[0] == '?':  # boolean
        return inp[1:].lower() in ('true', 't', '1')
    elif inp[0] == '@':  # json (list / dict)
        return json.loads(inp[1:])

    # default to regular string
    return inp


class ConfigLike:
    def get(self, name, default=None):
        try:
            return self.__getitem__(name)
        except KeyError:
            return default

    @abstractmethod
    def __getitem__(self, item):
        ...


class ConfigView(ConfigLike):
    def __init__(self, parent: ConfigLike, prefix: str):
        self._parent = parent
        self._prefix = prefix

    def __getitem__(self, item):
        return self._parent[f'{self._prefix}.{item}']

    def __repr__(self):
        return f'ConfigView(prefix="{self._prefix}")'


class Config(ConfigLike):
    def __init__(self, path: Union[str, Path]):
        self._path = path

        self._conf = configparser.ConfigParser()
        self._conf.read(path)

    def __getitem__(self, item):
        if item in self._conf:  # is a section
            return ConfigView(self, item)

        section, key = item.rsplit('.', 1)
        if section not in self._conf:
            raise KeyError(f'Unknown section: "{section}"')

        return _parse(self._conf[section][key])

    def __repr__(self):
        return f'Config(path="{self._path}")'
