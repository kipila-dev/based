from typing import cast

from forje.core.errors import ForjeError


def get_config[T](
    config: dict[str, object],
    key: str,
    default: T,
    *,
    strip: bool = True,
) -> T:
    """Retrieves a value from a configuration dictionary with type validation."""
    value = config.get(key)
    if value is None:
        return default

    expected_type = type(default)

    if expected_type is bool:
        if not isinstance(value, bool):
            raise _type_error(key, expected_type, value)
    elif expected_type is int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise _type_error(key, expected_type, value)
    elif not isinstance(value, expected_type):
        raise _type_error(key, expected_type, value)

    if isinstance(value, str) and strip:
        value = value.strip()
        if not value:
            return default

    return cast("T", value)


def _type_error(key: str, expected_type: type, value: object) -> ForjeError:
    msg = (
        f"Invalid value for '{key}': "
        f"required '{expected_type.__name__}', got '{type(value).__name__}'"
    )
    return ForjeError(msg)
