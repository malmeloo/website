import configparser
import json
from pathlib import Path
from typing import Union, Optional, Any


def _parse(inp: str) -> Any:
    if not inp:  # empty, so treat as string
        return inp

    if inp[0] == '?':  # boolean
        return inp[1:].lower() in ('true', 't', '1')
    elif inp[0] == '@':  # json (list / dict)
        return json.loads(inp[1:])

    # default to regular string
    return inp


class Config:
    def __init__(self, path: Union[str, Path]):
        self._path = path

        self._conf = configparser.ConfigParser()
        self._conf.read(path)

    def get(self, name: str, default: Optional[Any] = None) -> Any:
        try:
            return self.__getitem__(name)
        except KeyError:
            return default

    def __getitem__(self, item: str) -> Any:
        section, key = item.rsplit('.', 1)
        if section not in self._conf:
            raise KeyError(f'Unknown section: "{section}"')

        return _parse(self._conf[section][key])

    def __repr__(self) -> str:
        return f'Config(path="{self._path}")'
