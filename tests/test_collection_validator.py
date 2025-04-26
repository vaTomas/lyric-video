import pytest
from collection_validator import validate_collection, ValidationError

@pytest.mark.parametrize(
    "value,collection_type,element_count,element_types",
    [
        ([1.0, 2.0], list, 2, float),
        ([1.0, 2.0], [list], 2, [float]),
        ({1, 2, 3}, None, None, None),
        (None, (tuple, None), 2, int),
        ([None, 4], [list], 2, [int, None]),
        (4, int, None, None),
        ("hello", str, None, None),
        ("hi", [str, int], 2, None),
        ("four", [str, int], 4, str),
        ([1, 2, 3, 4], [list, tuple], 4, int),
        ([-1.33341, -1e-11, 2012, 0], [list, tuple], 4, (float, int)),
    ],
)
def test_validate_collection_valid(
    value, collection_type, element_count, element_types
):
    # Should not raise an exception
    assert (
        validate_collection(
            value,
            collection_type=collection_type,
            element_count=element_count,
            element_types=element_types,
        )
        is None
    )


@pytest.mark.parametrize(
    "value,collection_type,element_count,element_types",
    [
        ([None], [tuple, None], 2, int),
        ([1.5], [tuple, None], 2, int),
        ((1, 2.5, 6, None), [tuple, list], 4, (int, float)),
    ],
)
def test_validate_collection_invalid(
    value, collection_type, element_count, element_types
):
    with pytest.raises(ValidationError):
        validate_collection(
            value,
            collection_type=collection_type,
            element_count=element_count,
            element_types=element_types,
        )
