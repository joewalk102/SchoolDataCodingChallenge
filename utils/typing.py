def convert_type(target_type: type, value, raise_on_error: bool = False):
    """Attempt to convert to designated `target_type`

    Args:
        - target_type: Desired type that the value should be converted to.
        - value: Value that is going to be type-casted.
        - raise_on_error: When typecasting fails and raises ValueError, if false,
            the same value that is passed in gets returned. If True, ValueError gets
            re-raised.
    Returns:
        Typecasted value is returned upon success, otherwise, value with original type
        is returned (if `raise_on_error` is False).
    """
    try:
        return target_type(value)
    except ValueError:
        if raise_on_error:
            raise
    return value
