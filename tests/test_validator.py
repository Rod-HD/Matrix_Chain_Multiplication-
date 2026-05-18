"""Unit tests cho ``validator.validate_dimension_array``.

Bao phủ các nhánh kiểm tra theo Requirement 1:
    - Req 1.2: độ dài ``p`` < 2.
    - Req 1.3: phần tử ``<= 0``.
    - Req 1.4: phần tử không phải số nguyên (bao gồm ``bool``, ``float``,
      ``str``).
    - Req 1.5: ``p`` hợp lệ → trả về ``n = len(p) - 1``.

Các test dùng ``pytest.raises(ValueError, match=...)`` với chuỗi đã được
``re.escape`` để khớp đoạn nguyên văn của thông điệp (vì ``match`` là
regex và message có chứa ``(``, ``)``).
"""

from __future__ import annotations

import re

import pytest

from mcm.validator import validate_dimension_array


# Thông điệp lỗi nguyên văn theo design.md / Req 1.2/1.3/1.4.
MSG_TOO_SHORT = (
    "Dimension_Array phải có ít nhất 2 phần tử "
    "(tương ứng n ≥ 1 ma trận)"
)
MSG_NOT_INT = "Mọi phần tử của Dimension_Array phải là số nguyên"
MSG_NOT_POSITIVE = (
    "Mọi phần tử của Dimension_Array phải là số nguyên dương"
)


# ---------------------------------------------------------------------------
# Req 1.2: Dimension_Array có ít hơn 2 phần tử.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("p", [[], [5]])
def test_raises_when_length_less_than_two(p):
    """``[]`` và ``[5]`` đều phải bị từ chối với thông điệp Req 1.2."""
    with pytest.raises(ValueError, match=re.escape(MSG_TOO_SHORT)):
        validate_dimension_array(p)


# ---------------------------------------------------------------------------
# Req 1.4: Dimension_Array chứa phần tử không phải số nguyên.
#          Bao gồm ``bool`` vì ``bool`` là subclass của ``int`` nhưng
#          design.md chỉ định loại trừ bằng ``type(x) is int``.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "p",
    [
        [1, 2.5, 3],     # float không phải int.
        [1, "2", 3],     # str không phải int.
        [1, 2.0, 3],     # float dạng "tròn" vẫn không phải int.
        [True, 1, 2],    # bool phải bị từ chối (Req 1.4).
    ],
)
def test_raises_when_element_not_int(p):
    """Mọi phần tử không thuộc ``type(x) is int`` đều phải bị từ chối."""
    with pytest.raises(ValueError, match=re.escape(MSG_NOT_INT)):
        validate_dimension_array(p)


# ---------------------------------------------------------------------------
# Req 1.3: Dimension_Array chứa phần tử <= 0.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "p",
    [
        [0, 1],           # phần tử bằng 0 ở đầu.
        [1, -2, 3],       # phần tử âm ở giữa.
        [1, 2, 0],        # phần tử bằng 0 ở cuối.
    ],
)
def test_raises_when_element_not_positive(p):
    """Phần tử ``<= 0`` (kể cả 0) phải bị từ chối với Req 1.3."""
    with pytest.raises(ValueError, match=re.escape(MSG_NOT_POSITIVE)):
        validate_dimension_array(p)


# ---------------------------------------------------------------------------
# Req 1.5: Dimension_Array hợp lệ → trả về ``n = len(p) - 1``.
# ---------------------------------------------------------------------------
def test_returns_chain_length_for_valid_input():
    """``[3, 10, 7, 2]`` mô tả 3 ma trận → ``n == 3``."""
    assert validate_dimension_array([3, 10, 7, 2]) == 3


# ---------------------------------------------------------------------------
# Property test 1: Validator trả về Matrix_Chain_Length đúng.
#
# Feature: matrix-chain-multiplication
# Property 1: For all valid Dimension_Array p (mọi phần tử là int dương,
#             len(p) >= 2), validate_dimension_array(p) == len(p) - 1.
#
# **Validates: Requirements 1.5**
#
# Framework: chỉ dùng thư viện chuẩn (Req 8.3) — không dùng `hypothesis`.
# Sinh dữ liệu bằng `random.Random(SEED)` cố định để reproducible. Mỗi
# property dùng một offset trên `SEED` gốc; property này dùng offset 1.
# ---------------------------------------------------------------------------

import random

# Seed gốc theo design.md ("Testing Strategy / PBT thủ công").
_SEED = 20251128
# Số iteration tối thiểu cho mỗi property test (theo task 2.3).
_ITERATIONS = 100
# Trần kích thước chuỗi ma trận theo task 2.3.
_N_MAX = 8
# Khoảng giá trị của mỗi phần tử Dimension_Array theo task 2.3.
_VALUE_MIN = 1
_VALUE_MAX = 50


def _gen_valid_dimension_array(rng: random.Random) -> list[int]:
    """Sinh ngẫu nhiên một Dimension_Array hợp lệ.

    - ``n = len(p) - 1`` được chọn ngẫu nhiên trong ``[1, _N_MAX]``
      (đảm bảo ``len(p) >= 2`` theo Req 1.2).
    - Mỗi phần tử là ``int`` ngẫu nhiên trong ``[_VALUE_MIN, _VALUE_MAX]``
      (đảm bảo ``> 0`` theo Req 1.3 và là ``int`` theo Req 1.4).
    """
    n = rng.randint(1, _N_MAX)
    return [rng.randint(_VALUE_MIN, _VALUE_MAX) for _ in range(n + 1)]


def test_property_1_validator_returns_matrix_chain_length():
    """Property 1: validator trả về ``len(p) - 1`` cho mọi p hợp lệ.

    **Validates: Requirements 1.5**
    """
    # Offset 1 cho property này (mỗi property một offset trên _SEED).
    rng = random.Random(_SEED + 1)
    for iteration in range(_ITERATIONS):
        p = _gen_valid_dimension_array(rng)
        result = validate_dimension_array(p)
        assert result == len(p) - 1, (
            f"iteration={iteration}, seed={_SEED + 1}, "
            f"p={p}, expected={len(p) - 1}, got={result}"
        )


# ---------------------------------------------------------------------------
# Property test 2: Validator từ chối phần tử không dương.
#
# Feature: matrix-chain-multiplication
# Property 2: For all Dimension_Array p hợp lệ, nếu chèn 1 phần tử <= 0
#             ở vị trí ngẫu nhiên thì validate_dimension_array(p) SHALL
#             raise ValueError với message khớp
#             "Mọi phần tử của Dimension_Array phải là số nguyên dương".
#
# **Validates: Requirements 1.3**
#
# Framework: chỉ dùng thư viện chuẩn (Req 8.3) — không dùng `hypothesis`.
# Sinh dữ liệu bằng `random.Random(SEED)` cố định để reproducible.
# Property này dùng offset 2 trên SEED gốc → seed = 20251130.
# ---------------------------------------------------------------------------


def test_property_2_validator_rejects_non_positive_element():
    """Property 2: validator từ chối phần tử không dương.

    **Validates: Requirements 1.3**
    """
    # Offset 2 cho property này → seed = 20251128 + 2 = 20251130.
    rng = random.Random(_SEED + 2)
    for iteration in range(_ITERATIONS):
        # 1) Sinh một Dimension_Array hợp lệ.
        p = _gen_valid_dimension_array(rng)

        # 2) Chọn vị trí ngẫu nhiên và thay bằng giá trị <= 0.
        idx = rng.randint(0, len(p) - 1)
        bad_value = rng.randint(-50, 0)
        p[idx] = bad_value

        # 3) Xác nhận ValueError với message đúng nguyên văn Req 1.3.
        with pytest.raises(ValueError, match=re.escape(MSG_NOT_POSITIVE)):
            validate_dimension_array(p)
