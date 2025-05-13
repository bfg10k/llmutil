from openai.types.responses import ResponseTextConfigParam


def _to_arr(items):
    return {
        "type": "array",
        "items": items,
    }


def gen_obj(**props):
    """
    gen_obj(**props) -> dict

    Create a JSON schema for an object.
    Each keyword argument is a property of the object.

    Args:
        **props: Fields of the object as key-value pairs.

    Returns:
        dict: JSON schema for the object.
    """
    return {
        "type": "object",
        "properties": props,
        "required": list(props.keys()),
        "additionalProperties": False,
    }


def gen_arr(**props):
    """
    gen_arr(**props) -> dict

    Create a JSON schema for an array of objects.
    Each keyword argument is a property of the object.

    Args:
        **props: Fields of each object in the array.

    Returns:
        dict: JSON schema for array of objects.
    """
    return _to_arr(gen_obj(**props))


def gen_str(desc: str, enum: list[str] | None = None, array: bool = False):
    """
    gen_str(desc, enum=None, array=False) -> dict

    Create a JSON schema for a string field.

    Args:
        desc (str): Description of the field.
        enum (list, optional): Allowed values. Defaults to None.
        array (bool, optional): If True, make it an array of strings. Defaults to False.

    Returns:
        dict: JSON schema for the string or array of strings.
    """
    assert isinstance(desc, str)
    assert enum is None or isinstance(enum, list)
    assert isinstance(array, bool)

    ret = {"type": "string", "description": desc}
    if enum is not None:
        ret["enum"] = enum
    if array:
        ret = _to_arr(ret)
    return ret


def gen_num(desc: str, array: bool = False):
    """
    gen_num(desc, array=False) -> dict

    Create a JSON schema for a number field.

    Args:
        desc (str): Description of the field.
        array (bool, optional): If True, make it an array of numbers. Defaults to False.

    Returns:
        dict: JSON schema for the number or array of numbers.
    """
    assert isinstance(desc, str)
    assert isinstance(array, bool)

    ret = {"type": "number", "description": desc}
    if array:
        ret = _to_arr(ret)
    return ret


def gen_bool(desc: str, array: bool = False):
    """
    gen_bool(desc, array=False) -> dict

    Create a JSON schema for a boolean field.

    Args:
        desc (str): Description of the field.
        array (bool, optional): If True, make it an array of booleans. Defaults to False.

    Returns:
        dict: JSON schema for the boolean or array of booleans.
    """
    assert isinstance(desc, str)
    assert isinstance(array, bool)

    ret = {"type": "boolean", "description": desc}
    if array:
        ret = _to_arr(ret)
    return ret


def gen_schema(**props) -> ResponseTextConfigParam:
    """
    gen_schema(**props) -> dict

    Create a top-level JSON schema for an object.
    Each keyword argument is a property of the object.

    Args:
        **props: Fields of the top-level object.

    Returns:
        dict: JSON schema in OpenAI format.
    """
    return {
        "format": {
            "type": "json_schema",
            "name": "output",
            "strict": True,
            "schema": gen_obj(**props),
        },
    }
