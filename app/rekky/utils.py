from typing import Union, List


def uuid_or_int(id: Union[str, int]) -> Union[str, int]:
    if isinstance(id, str) and id.isdigit():
        return int(id)
    return id


def listify(value: Union[object, List[object]]) -> List[object]:
    if isinstance(value, str):
        return [value]
    return value
