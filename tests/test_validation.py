"""Test cho module validation."""

import random

import pytest

from mcm2.validation import validate_dimensions, DimensionError


@pytest.mark.parametrize(
    ("dims", "expected_n"),
    [
        ([5, 7], 1),
        ([3, 10, 7, 2], 3),
        ([30, 35, 15, 5, 10, 20, 25], 6),
    ],
)
def test_returns_matrix_count(dims, expected_n):
    """Mảng hợp lệ trả về n = len(dims) - 1."""
    assert validate_dimensions(dims) == expected_n


@pytest.mark.parametrize("dims", [[], [5]])
def test_too_short(dims):
    """Mảng dưới 2 phần tử bị từ chối."""
    with pytest.raises(DimensionError, match="tối thiểu 2 phần tử"):
        validate_dimensions(dims)


@pytest.mark.parametrize("dims", [[10, 0, 5], [10, -3, 5], [1, 2, 0]])
def test_non_positive(dims):
    """Phần tử <= 0 bị từ chối với thông điệp 'không nhận'."""
    with pytest.raises(DimensionError, match="không nhận"):
        validate_dimensions(dims)


@pytest.mark.parametrize("dims", [[10, 2.5, 5], [1, "2", 3], [1, 2.0, 3]])
def test_not_integer(dims):
    """Phần tử không phải int dương bị từ chối với thông điệp 'không nhận'."""
    with pytest.raises(DimensionError, match="không nhận"):
        validate_dimensions(dims)


def test_bool_rejected():
    """bool là lớp con của int nhưng không được coi là kích thước hợp lệ."""
    with pytest.raises(DimensionError, match="không nhận"):
        validate_dimensions([True, 2, 3])


def test_property_returns_n_random():
    """Tính chất: với mọi mảng hợp lệ, kết quả luôn bằng len(dims) - 1.

    Dùng random.Random với seed cố định (không cần thư viện ngoài) để
    sinh 200 mảng hợp lệ ngẫu nhiên và kiểm tra.
    """
    rng = random.Random(2026)
    for _ in range(200):
        n = rng.randint(1, 12)
        dims = [rng.randint(1, 100) for _ in range(n + 1)]
        assert validate_dimensions(dims) == n
