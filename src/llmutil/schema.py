def gen_obj(**props):
    """Generate schema for object. Properties are the fields of the object."""
    return {
        "type": "object",
        "properties": props,
        "required": list(props.keys()),
        "additionalProperties": False,
    }


def _wrap_arr(items):
    return {
        "type": "array",
        "items": items,
    }


def gen_arr(**props):
    """Generate schema for array of objects. Properties are the fields of the object."""
    return _wrap_arr(gen_obj(**props))


def gen_str(desc, enum=None, array=False):
    """Generate schema for string. When array is true, generate array of strings. Enum optionally specifies the allowed values."""
    assert isinstance(desc, str)
    assert enum is None or isinstance(enum, list)
    assert isinstance(array, bool)

    ret = {"type": "string", "description": desc}
    if enum is not None:
        ret["enum"] = enum
    if array:
        ret = _wrap_arr(ret)
    return ret


def gen_num(desc, array=False):
    """Generate schema for number. When array is true, generate array of numbers."""
    assert isinstance(desc, str)
    assert isinstance(array, bool)

    ret = {"type": "number", "description": desc}
    if array:
        ret = _wrap_arr(ret)
    return ret


def gen_bool(desc, array=False):
    """Generate schema for boolean. When array is true, generate array of booleans."""
    assert isinstance(desc, str)
    assert isinstance(array, bool)

    ret = {"type": "boolean", "description": desc}
    if array:
        ret = _wrap_arr(ret)
    return ret


def gen_schema(**props):
    """The top level schema which is always an object. Properties are the fields of the object."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "output",
            "strict": True,
            "schema": gen_obj(**props),
        },
    }
