from pylox.lox_types import LoxType, Number, String


def get_lox_type_name(value: LoxType) -> str:
    if isinstance(value, String):
        return "String"

    if isinstance(value, Number):
        return "Number"

    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "nil"

    raise NotImplementedError(f"Unknown type for value: {value}")


def is_truthy(value: LoxType) -> bool:
    if value is None:
        return False

    if isinstance(value, (str, float, bool)):
        return bool(value)

    type_name = get_lox_type_name(value)
    raise NotImplementedError(f"Truthiness not implemented for {type_name}")
