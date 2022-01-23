def get_lox_type_name(value: object) -> str:
    if isinstance(value, str):
        return "String"

    if isinstance(value, float):
        return "Number"

    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "nil"

    raise NotImplementedError(f"Unknown type for value: {value}")


def is_truthy(value: object) -> bool:
    if value is None:
        return False

    if isinstance(value, (str, float, bool)):
        return bool(value)

    type_name = get_lox_type_name(value)
    raise NotImplementedError(f"Truthiness not implemented for {type_name}")
