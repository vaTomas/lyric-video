from typing import Any, Iterable, Optional, Tuple, Type, Union


class ValidationError(ValueError):
    """
    Exception raised when validation fails.
    """

    pass


def validate_collection(
    value: Any,
    collection_type: Optional[Union[Type, Tuple[Optional[Type], ...]]] = tuple,
    element_count: Optional[int] = None,
    element_types: Optional[Union[Type, Tuple[Optional[Type], ...]]] = (int, float),
) -> None:
    """
    Validates that `value` is a container (or allowed None) of a certain type,
    with an optional fixed length and element types.

    Args:
        value: The object to validate.
        collection_type: A type or tuple of types (e.g. list, tuple) for the container itself.
                         If None, any container type is allowed. To allow None as a valid value,
                         include `None` in this tuple (e.g. (tuple,None)).
        element_count: Exact length required. If None, any length is allowed.
        element_types: A type or tuple of types for elements inside the container.
                       If None, any element type is allowed. To allow None elements,
                       include `None` in this tuple (e.g. (int,None)).

    Raises:
        ValidationError: if any of the checks fail.
    """
    # -- Handle collection_type check --
    # Canonicalize collection_type into a tuple of types, or None
    if collection_type is not None:
        # Allow passing a single type
        if not isinstance(collection_type, (tuple, list)):
            types_ct = (collection_type,)
        else:
            types_ct = collection_type

        # Map literal None to type(None)
        ct_tuple = tuple(type(None) if t is None else t for t in types_ct)
    else:
        ct_tuple = None

    # If NoneType allowed for the value itself
    if (
        ct_tuple is not None
        and isinstance(value, type(None))
        and type(None) in ct_tuple
    ):
        return  # None is explicitly allowed as the container

    # Check container type if specified
    if ct_tuple is not None:
        if not isinstance(value, ct_tuple):
            allowed = ", ".join(
                t.__name__ if t is not type(None) else "None" for t in ct_tuple
            )
            raise ValidationError(
                f"Value must be one of types ({allowed}), got {type(value).__name__}."
            )
    else:
        # collection_type is None: allow any container type, but ensure it is iterable (except strings)
        if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
            raise ValidationError(
                f"Value must be an iterable container, got {type(value).__name__}."
            )

    # -- Handle element_count check --
    if element_count is not None:
        try:
            length = len(value)
        except Exception:
            raise ValidationError(
                f"Value has no length, cannot enforce element_count={element_count}."
            )
        if length != element_count:
            raise ValidationError(
                f"Container length must be {element_count}, got {length}."
            )

    # -- Handle element_types check --
    if element_types is not None:
        # Canonicalize element_types into tuple
        types_et = (
            (element_types,)
            if not isinstance(element_types, (tuple, list))
            else element_types
        )
        et_tuple = tuple(type(None) if t is None else t for t in types_et)
        for idx, elem in enumerate(value):
            if isinstance(elem, type(None)) and type(None) in et_tuple:
                continue
            if not isinstance(elem, et_tuple):
                allowed = ", ".join(
                    t.__name__ if t is not type(None) else "None" for t in et_tuple
                )
                raise ValidationError(
                    f"Element at index {idx} must be one of ({allowed}), got {type(elem).__name__}."
                )
