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
