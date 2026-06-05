"""Test cho lõi thuật toán: ba lời giải và truy vết dấu ngoặc."""

import random

import pytest

from mcm2.core import (
    naive_min_cost,
    memoized_min_cost,
    bottom_up,
    optimal_parenthesization,
    count_parenthesizations,
    solve,
    _recompute_from_split,
)


# --- Bốn ví dụ bắt buộc theo tài liệu / Cormen --------------------------------

REQUIRED = [
    pytest.param([3, 10, 7, 2], 200, "(A1(A2A3))", id="3-matrices"),
    pytest.param([10, 20, 50, 1, 100], 2200, "((A1(A2A3))A4)", id="4-matrices"),
    pytest.param(
        [30, 35, 15, 5, 10, 20, 25],
        15125,
        "((A1(A2A3))((A4A5)A6))",
        id="6-matrices-CLRS",
    ),
    pytest.param([5, 7], 0, "A1", id="single-matrix"),
]


@pytest.mark.parametrize(("dims", "cost", "parens"), REQUIRED)
def test_bottom_up_cost_and_parens(dims, cost, parens):
    """Bottom-up cho đúng chi phí và dấu ngoặc trên các ví dụ bắt buộc."""
    result = solve(dims)
    assert result.min_cost == cost
    assert result.parenthesization == parens


@pytest.mark.parametrize(("dims", "cost", "parens"), REQUIRED)
def test_three_solvers_agree(dims, cost, parens):
    """Ba lời giải (đệ quy thuần, ghi nhớ, bottom-up) cùng một chi phí."""
    table_cost, _ = bottom_up(dims)
    n = len(dims) - 1
    assert naive_min_cost(dims) == cost
    assert memoized_min_cost(dims) == cost
    assert table_cost[1][n] == cost


def test_diagonal_is_zero():
    """Đường chéo bảng chi phí luôn bằng 0 (đoạn một ma trận)."""
    cost, _ = bottom_up([4, 10, 3, 12, 20, 7])
    n = 5
    for i in range(1, n + 1):
        assert cost[i][i] == 0


def test_split_in_range():
    """Mọi vị trí cắt nằm trong khoảng hợp lệ [i, j-1]."""
    n_dims = [4, 10, 3, 12, 20, 7, 5, 8]
    cost, split = bottom_up(n_dims)
    n = len(n_dims) - 1
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            assert i <= split[i][j] < j


@pytest.mark.parametrize(
    ("n", "expected"),
    [(1, 1), (2, 1), (3, 2), (4, 5), (5, 14), (6, 42), (7, 132)],
)
def test_catalan(n, expected):
    """count_parenthesizations trả về số Catalan C_{n-1}."""
    assert count_parenthesizations(n) == expected


def test_consistency_check_detects_corruption():
    """Làm hỏng bảng split khiến kiểm tra chéo phát hiện bất nhất quán."""
    result = solve([30, 35, 15, 5, 10, 20, 25])
    result.split[1][result.n] = 99  # vị trí cắt ngoài khoảng
    with pytest.raises(RuntimeError, match="Bất nhất quán"):
        _recompute_from_split(result.split, result.dims, 1, result.n)


# --- Tính chất: đối chiếu với liệt kê toàn bộ (brute-force) -------------------


def test_property_matches_brute_force():
    """Với mọi mảng (n <= 6), bottom-up khớp chi phí liệt kê toàn bộ.

    Đây là kiểm chứng mạnh nhất: xác nhận lời giải đạt cực tiểu toàn cục,
    không chỉ tự nhất quán. Dùng seed cố định để tái lập.
    """
    rng = random.Random(20260601)
    for _ in range(150):
        n = rng.randint(1, 6)
        dims = [rng.randint(1, 50) for _ in range(n + 1)]
        result = solve(dims)
        assert result.min_cost == naive_min_cost(dims)
        assert result.min_cost == memoized_min_cost(dims)


def test_property_parens_well_formed():
    """Dấu ngoặc tối ưu luôn cân bằng và liệt kê A1..An đúng thứ tự."""
    import re

    rng = random.Random(777)
    for _ in range(150):
        n = rng.randint(1, 9)
        dims = [rng.randint(1, 50) for _ in range(n + 1)]
        _, split = bottom_up(dims)
        parens = optimal_parenthesization(split, 1, n)

        # Cân bằng ngoặc tại mọi tiền tố.
        depth = 0
        for ch in parens:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            assert depth >= 0
        assert depth == 0

        # Thứ tự token A_k đúng 1..n.
        tokens = re.findall(r"A\d+", parens)
        assert tokens == [f"A{k}" for k in range(1, n + 1)]


def test_property_split_recompute_matches_cost():
    """Chi phí suy ra từ bảng split luôn bằng cost[1][n]."""
    rng = random.Random(31337)
    for _ in range(150):
        n = rng.randint(1, 9)
        dims = [rng.randint(1, 50) for _ in range(n + 1)]
        cost, split = bottom_up(dims)
        recomputed = _recompute_from_split(split, dims, 1, n)
        assert recomputed == cost[1][n]
