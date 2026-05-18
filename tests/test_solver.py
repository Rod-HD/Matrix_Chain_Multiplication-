"""Unit test cho ``matrix_chain_order`` — 4 ví dụ bắt buộc theo Req 7.

Test này kiểm tra ``Scalar_Multiplication_Count`` (giá trị ``m[1][n]``) cho 4
``Dimension_Array`` mẫu trong tài liệu môn học:

- Req 7.1: ``[3, 10, 7, 2]`` → ``m[1][3] = 200``
- Req 7.2: ``[10, 20, 50, 1, 100]`` → ``m[1][4] = 2200``
- Req 7.3: ``[30, 35, 15, 5, 10, 20, 25]`` → ``m[1][6] = 15125`` (ví dụ CLRS kinh điển)
- Req 7.4: ``[5, 7]`` (n = 1) → ``m[1][1] = 0``

Test gọi ``matrix_chain_order(p)`` trực tiếp và assert giá trị tại ``m[1][n]``.
Khi sai, message lỗi nêu rõ tên test, giá trị thực tế và giá trị mong đợi
(Req 7.5).
"""

import pytest

from mcm.solver import (
    matrix_chain_order,
    print_optimal_parens,
    MCMSolver,
    _recompute_cost_from_parens,
    _assert_consistent,
)


@pytest.mark.parametrize(
    ("p", "expected_cost"),
    [
        pytest.param([3, 10, 7, 2], 200, id="req-7.1-p=[3,10,7,2]"),
        pytest.param([10, 20, 50, 1, 100], 2200, id="req-7.2-p=[10,20,50,1,100]"),
        pytest.param(
            [30, 35, 15, 5, 10, 20, 25],
            15125,
            id="req-7.3-p=[30,35,15,5,10,20,25]",
        ),
        pytest.param([5, 7], 0, id="req-7.4-p=[5,7]-n=1"),
    ],
)
def test_matrix_chain_order_cost_matches_required_examples(
    p: list[int], expected_cost: int
) -> None:
    """``m[1][n]`` khớp ``Scalar_Multiplication_Count`` mong đợi cho 4 ví dụ bắt buộc."""
    m, _s = matrix_chain_order(p)
    n = len(p) - 1

    assert m[1][n] == expected_cost, (
        f"Sai m[1][{n}] cho p={p}: "
        f"thực tế={m[1][n]}, mong đợi={expected_cost}"
    )


@pytest.mark.parametrize(
    ("p", "expected_parens"),
    [
        pytest.param([3, 10, 7, 2], "(A1(A2A3))", id="req-7.1-parens"),
        pytest.param([10, 20, 50, 1, 100], "((A1(A2A3))A4)", id="req-7.2-parens"),
        pytest.param(
            [30, 35, 15, 5, 10, 20, 25],
            "((A1(A2A3))((A4A5)A6))",
            id="req-7.3-parens",
        ),
        pytest.param([5, 7], "A1", id="req-7.4-parens-n=1"),
    ],
)
def test_print_optimal_parens_matches_required_examples(
    p: list[int], expected_parens: str
) -> None:
    """``print_optimal_parens(s, 1, n)`` khớp Optimal_Parenthesization mong đợi cho 4 ví dụ bắt buộc."""
    _m, s = matrix_chain_order(p)
    n = len(p) - 1

    result = print_optimal_parens(s, 1, n)

    assert result == expected_parens, (
        f"Sai Optimal_Parenthesization cho p={p}: "
        f"thực tế={result!r}, mong đợi={expected_parens!r}"
    )


# ===========================================================================
# Property-Based Test 3: Đường chéo m[i][i] = 0
#
# Validates: Requirements 2.1
#
# Mô tả: Với mọi Dimension_Array p hợp lệ, sau khi chạy matrix_chain_order(p),
# mọi ô trên đường chéo phải bằng 0:
#     ∀ i ∈ [1, n] : m[i][i] == 0
#
# Framework: chỉ thư viện chuẩn (Req 8.3) — dùng random.Random(SEED) cố định
# thay vì hypothesis. Seed cơ sở 20251128 + offset 3 (Property 3) → reproducible.
# ===========================================================================
import random


def test_property_3_diagonal_m_ii_is_zero() -> None:
    """Property 3: m[i][i] == 0 cho mọi i ∈ [1, n].

    100 iteration với generator constrained:
      - n ∈ [1, n_max] với n_max = 8 (chuỗi đủ ngắn để đường chéo có ý nghĩa
        ở mọi kích thước, vẫn đủ đa dạng để bắt regression);
      - mỗi phần tử p[k] ∈ [1, 50] (số nguyên dương, đồng nhất với các PBT khác).

    Khi failure: in seed cố định, n, p, và (i, m[i][i]) đầu tiên vi phạm để
    reproduce trực tiếp bằng random.Random(SEED) → list(...).
    """
    SEED = 20251128 + 3  # offset 3 cho Property 3
    rng = random.Random(SEED)
    n_max = 8
    iterations = 100

    for iteration in range(iterations):
        # Sinh n ∈ [1, n_max] và p có (n + 1) phần tử thuộc [1, 50].
        n = rng.randint(1, n_max)
        p = [rng.randint(1, 50) for _ in range(n + 1)]

        m, _s = matrix_chain_order(p)

        # Mọi ô đường chéo m[i][i] với i ∈ [1, n] phải bằng 0 (Req 2.1).
        for i in range(1, n + 1):
            assert m[i][i] == 0, (
                f"Property 3 FAILED tại iteration={iteration}, "
                f"seed={SEED}, n={n}, p={p}: "
                f"m[{i}][{i}]={m[i][i]} (mong đợi 0)"
            )


# ===========================================================================
# Property-Based Test 7: Cấu trúc Optimal_Parenthesization hợp lệ
#
# Validates: Requirements 4.2, 4.3, 4.5, 9.2
#
# Mô tả: Với mọi Dimension_Array p hợp lệ, chuỗi parens trả về từ
# print_optimal_parens(s, 1, n) phải thỏa đồng thời:
#   1. Chỉ chứa ký tự từ tập ()A0123456789
#   2. Cân bằng ngoặc: tại mọi tiền tố count('(') >= count(')')
#      và tổng count('(') == count(')')
#   3. Token A_k xuất hiện đúng thứ tự A1, A2, ..., An
#   4. n == 1 ⇒ parens == "A1"
#   5. n >= 2 ⇒ parens chứa ít nhất một '(' và một ')'
#
# Framework: random.Random(SEED) cố định, 100 iteration (Req 8.3).
# Seed cơ sở 20251128 + offset 7 (Property 7) = 20251135.
# ===========================================================================
import re


def test_property_7_parens_well_formed() -> None:
    """Property 7: Cấu trúc Optimal_Parenthesization hợp lệ.

    **Validates: Requirements 4.2, 4.3, 4.5, 9.2**

    100 iteration với generator constrained:
      - n ∈ [1, 8] (len(p) ∈ [2, 9]), mỗi phần tử p[k] ∈ [1, 50].

    Kiểm tra 5 điều kiện:
      1. Tập ký tự con của ()A0123456789
      2. Cân bằng ngoặc ở mọi tiền tố
      3. Thứ tự token A_k đúng 1..n
      4. n == 1 ⇒ parens == "A1"
      5. n >= 2 ⇒ có ít nhất một cặp (...)
    """
    SEED = 20251128 + 7  # offset 7 cho Property 7 → 20251135
    rng = random.Random(SEED)
    n_max = 8
    iterations = 100
    allowed_chars = set("()A0123456789")

    for iteration in range(iterations):
        # Sinh n ∈ [1, n_max] và p có (n + 1) phần tử thuộc [1, 50].
        n = rng.randint(1, n_max)
        p = [rng.randint(1, 50) for _ in range(n + 1)]

        _m, s = matrix_chain_order(p)
        parens = print_optimal_parens(s, 1, n)

        # --- Điều kiện 1: Tập ký tự hợp lệ ---
        invalid_chars = set(parens) - allowed_chars
        assert not invalid_chars, (
            f"Property 7 FAILED (ký tự không hợp lệ) tại iteration={iteration}, "
            f"seed={SEED}, n={n}, p={p}: "
            f"parens={parens!r}, ký tự lạ={invalid_chars}"
        )

        # --- Điều kiện 2: Cân bằng ngoặc ở mọi tiền tố ---
        open_count = 0
        close_count = 0
        for idx, ch in enumerate(parens):
            if ch == "(":
                open_count += 1
            elif ch == ")":
                close_count += 1
            assert open_count >= close_count, (
                f"Property 7 FAILED (ngoặc mất cân bằng tại prefix) "
                f"iteration={iteration}, seed={SEED}, n={n}, p={p}: "
                f"parens={parens!r}, vị trí={idx}, "
                f"count('(')={open_count}, count(')')={close_count}"
            )
        assert open_count == close_count, (
            f"Property 7 FAILED (tổng ngoặc không cân bằng) "
            f"iteration={iteration}, seed={SEED}, n={n}, p={p}: "
            f"parens={parens!r}, "
            f"count('(')={open_count}, count(')')={close_count}"
        )

        # --- Điều kiện 3: Token A_k xuất hiện đúng thứ tự 1..n ---
        tokens = re.findall(r"A\d+", parens)
        expected_tokens = [f"A{k}" for k in range(1, n + 1)]
        assert tokens == expected_tokens, (
            f"Property 7 FAILED (thứ tự token sai) "
            f"iteration={iteration}, seed={SEED}, n={n}, p={p}: "
            f"parens={parens!r}, tokens={tokens}, mong đợi={expected_tokens}"
        )

        # --- Điều kiện 4: n == 1 ⇒ parens == "A1" ---
        if n == 1:
            assert parens == "A1", (
                f"Property 7 FAILED (n=1 nhưng parens != 'A1') "
                f"iteration={iteration}, seed={SEED}, p={p}: "
                f"parens={parens!r}"
            )

        # --- Điều kiện 5: n >= 2 ⇒ có ít nhất một '(' và ')' ---
        if n >= 2:
            assert "(" in parens and ")" in parens, (
                f"Property 7 FAILED (n>=2 nhưng thiếu ngoặc) "
                f"iteration={iteration}, seed={SEED}, n={n}, p={p}: "
                f"parens={parens!r}"
            )


# ===========================================================================
# Task 5.3: Injection tests cho consistency check (Req 7.6)
#
# Kiểm tra rằng _recompute_cost_from_parens và _assert_consistent phát hiện
# đúng bất nhất quán khi dữ liệu nội bộ bị mutate sau khi solver chạy xong.
# ===========================================================================


class TestConsistencyCheckInjection:
    """Injection tests: mutate solver internals rồi gọi lại consistency check."""

    def test_invalid_split_raises_valueerror(self) -> None:
        """Mutate s[1][n] = 99 (split ngoài khoảng) → _recompute_cost_from_parens raise ValueError.

        _Requirements: 7.6_
        """
        solver = MCMSolver([30, 35, 15, 5, 10, 20, 25])

        # Mutate bảng s: gán split position không hợp lệ (ngoài khoảng [1, n-1]).
        solver.s[1][solver.n] = 99

        with pytest.raises(ValueError, match="Bất nhất quán"):
            _recompute_cost_from_parens(solver.s, solver.p, 1, solver.n)

    def test_wrong_cost_raises_runtimeerror(self) -> None:
        """Mutate m[1][n] = 9999 (cost sai) → _assert_consistent raise RuntimeError.

        _Requirements: 7.6_
        """
        solver = MCMSolver([30, 35, 15, 5, 10, 20, 25])

        # Mutate bảng m: gán cost sai khác với chi phí suy ra từ s_table.
        solver.m[1][solver.n] = 9999

        with pytest.raises(RuntimeError, match="Bất nhất quán"):
            _assert_consistent(solver.m, solver.s, solver.p, solver.n)


# ===========================================================================
# Property-Based Test 4: Tự nhất quán nội bộ của m, s, và parens
#
# Validates: Requirements 2.4, 2.5, 7.6
#
# Mô tả: Với mọi Dimension_Array p hợp lệ và mọi (i, j) với 1 <= i < j <= n:
#   a. s[i][j] ∈ [i, j-1] (split position trong khoảng hợp lệ)
#   b. m[i][j] == m[i][s[i][j]] + m[s[i][j]+1][j] + p[i-1]*p[s[i][j]]*p[j]
#      (recurrence đạt cực tiểu đúng tại s[i][j])
#   c. m[i][j] <= m[i][k] + m[k+1][j] + p[i-1]*p[k]*p[j] cho mọi k ∈ [i, j-1]
#      (m[i][j] là minimum trên mọi candidate)
#
# Framework: random.Random(SEED) cố định, 100 iteration (Req 8.3).
# Seed cơ sở 20251128 + offset 4 (Property 4) = 20251132.
# ===========================================================================


def test_property_4_internal_consistency() -> None:
    """Property 4: Tự nhất quán nội bộ của m, s, và parens.

    **Validates: Requirements 2.4, 2.5, 7.6**

    100 iteration với generator constrained:
      - n ∈ [1, 8] (len(p) ∈ [2, 9]), mỗi phần tử p[k] ∈ [1, 50].

    Với mỗi (i, j) thỏa 1 <= i < j <= n:
      a. Assert s[i][j] ∈ [i, j-1]
      b. Assert recurrence đạt cực tiểu đúng tại s[i][j]
      c. Assert m[i][j] <= mọi candidate q_k
    """
    SEED = 20251128 + 4  # offset 4 cho Property 4 → 20251132
    rng = random.Random(SEED)
    n_max = 8
    iterations = 100

    for iteration in range(iterations):
        # Sinh n ∈ [1, n_max] và p có (n + 1) phần tử thuộc [1, 50].
        n = rng.randint(1, n_max)
        p = [rng.randint(1, 50) for _ in range(n + 1)]

        m, s = matrix_chain_order(p)

        # Kiểm tra mọi cặp (i, j) với 1 <= i < j <= n.
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                # --- (a) Split position trong khoảng hợp lệ ---
                assert i <= s[i][j] < j, (
                    f"Property 4 FAILED (split ngoài khoảng) "
                    f"iteration={iteration}, seed={SEED}, n={n}, p={p}: "
                    f"s[{i}][{j}]={s[i][j]}, khoảng hợp lệ=[{i}, {j - 1}]"
                )

                # --- (b) Recurrence đạt cực tiểu đúng tại s[i][j] ---
                k_opt = s[i][j]
                q_at_s = (
                    m[i][k_opt] + m[k_opt + 1][j] + p[i - 1] * p[k_opt] * p[j]
                )
                assert m[i][j] == q_at_s, (
                    f"Property 4 FAILED (recurrence không khớp tại split tối ưu) "
                    f"iteration={iteration}, seed={SEED}, n={n}, p={p}: "
                    f"m[{i}][{j}]={m[i][j]}, "
                    f"q tại s[{i}][{j}]={k_opt} là {q_at_s}"
                )

                # --- (c) m[i][j] <= mọi candidate q_k ---
                for k in range(i, j):
                    q_k = m[i][k] + m[k + 1][j] + p[i - 1] * p[k] * p[j]
                    assert m[i][j] <= q_k, (
                        f"Property 4 FAILED (m[i][j] không phải minimum) "
                        f"iteration={iteration}, seed={SEED}, n={n}, p={p}: "
                        f"m[{i}][{j}]={m[i][j]} > q tại k={k} là {q_k}"
                    )


# ===========================================================================
# Property-Based Test 6: cost API khớp m[1][n]
#
# Validates: Requirements 6.1
#
# Mô tả: Với mọi Dimension_Array p hợp lệ, trường cost trả về từ
# MCMSolver(p).cost SHALL bằng MCMSolver(p).m[1][n].
#
# Framework: random.Random(SEED) cố định, 100 iteration (Req 8.3).
# Seed cơ sở 20251128 + offset 6 (Property 6) = 20251134.
# ===========================================================================


def test_property_6_cost_api_matches_m1n() -> None:
    """Property 6: cost API khớp m[1][n].

    **Validates: Requirements 6.1**

    100 iteration với generator constrained:
      - n ∈ [1, 8] (len(p) ∈ [2, 9]), mỗi phần tử p[k] ∈ [1, 50].

    Assert: MCMSolver(p).cost == MCMSolver(p).m[1][n]
    """
    SEED = 20251128 + 6  # offset 6 cho Property 6 → 20251134
    rng = random.Random(SEED)
    n_max = 8
    iterations = 100

    for iteration in range(iterations):
        # Sinh n ∈ [1, n_max] và p có (n + 1) phần tử thuộc [1, 50].
        n = rng.randint(1, n_max)
        p = [rng.randint(1, 50) for _ in range(n + 1)]

        solver = MCMSolver(p)

        # Property 6: cost API phải khớp m[1][n] (Req 6.1).
        assert solver.cost == solver.m[1][solver.n], (
            f"Property 6 FAILED tại iteration={iteration}, "
            f"seed={SEED}, n={n}, p={p}: "
            f"solver.cost={solver.cost}, solver.m[1][{solver.n}]={solver.m[1][solver.n]}"
        )


# ===========================================================================
# Property-Based Test 5: Tối ưu thực sự (cross-check brute-force)
#
# Validates: Requirements 2.4, 2.5, 6.1
#
# Mô tả: Với mọi Dimension_Array p hợp lệ với n <= 6, chi phí tính bởi
# MCMSolver(p).cost phải bằng chi phí tối thiểu khi enumerate MỌI cách
# đóng ngoặc (brute-force). Điều này chứng minh thuật toán DP thực sự
# tìm được cực tiểu toàn cục Bellman, không chỉ tự nhất quán nội bộ.
#
# Helper _brute_force_min_cost(p) đệ quy enumerate mọi parenthesization
# của A_1..A_n (số cách = Catalan(n-1), với n=6 → Catalan(5) = 42 cách).
#
# Framework: random.Random(SEED) cố định, 100 iteration (Req 8.3).
# Seed cơ sở 20251128 + offset 5 (Property 5) = 20251133.
# ===========================================================================


def _brute_force_min_cost(p: list[int]) -> int:
    """Enumerate mọi cách đóng ngoặc, trả về chi phí tối thiểu.

    Thuật toán đệ quy thử mọi Split_Position k ∈ [i, j-1] cho chuỗi con
    A_i..A_j, tính chi phí = cost(trái) + cost(phải) + p[i-1]*p[k]*p[j],
    và trả về minimum trên toàn bộ không gian parenthesization.

    Đây là brute-force thuần (không memoize) — chỉ dùng cho n nhỏ (n <= 6)
    để cross-check kết quả DP.
    """
    n = len(p) - 1

    def _min_cost(i: int, j: int) -> int:
        if i == j:
            return 0
        min_val = float("inf")
        for k in range(i, j):
            cost = _min_cost(i, k) + _min_cost(k + 1, j) + p[i - 1] * p[k] * p[j]
            if cost < min_val:
                min_val = cost
        return min_val

    return _min_cost(1, n)


def test_property_5_brute_force_cross_check() -> None:
    """Property 5: Tối ưu thực sự (cross-check brute-force).

    **Validates: Requirements 2.4, 2.5, 6.1**

    100 iteration với generator constrained:
      - n ∈ [1, 6] (len(p) ∈ [2, 7]), n_max = 6 để brute-force tractable
        (Catalan(5) = 42 cách đóng ngoặc);
      - mỗi phần tử p[k] ∈ [1, 50] (số nguyên dương).

    Assert: MCMSolver(p).cost == _brute_force_min_cost(p)
    """
    SEED = 20251128 + 5  # offset 5 cho Property 5 → 20251133
    rng = random.Random(SEED)
    n_max = 6
    iterations = 100

    for iteration in range(iterations):
        # Sinh n ∈ [1, n_max] và p có (n + 1) phần tử thuộc [1, 50].
        n = rng.randint(1, n_max)
        p = [rng.randint(1, 50) for _ in range(n + 1)]

        solver = MCMSolver(p)
        brute_force_cost = _brute_force_min_cost(p)

        # Property 5: DP cost phải khớp brute-force cost (Req 2.4, 2.5, 6.1).
        assert solver.cost == brute_force_cost, (
            f"Property 5 FAILED tại iteration={iteration}, "
            f"seed={SEED}, n={n}, p={p}: "
            f"MCMSolver(p).cost={solver.cost}, "
            f"_brute_force_min_cost(p)={brute_force_cost}"
        )


# ===========================================================================
# Task 11.1: Performance smoke tests (n=100, n=150)
#
# _Requirements: 3.3, 3.4_
#
# - test_n_100_under_one_second: p có 101 phần tử, đo time.perf_counter,
#   assert < 2.0 giây (margin cho CI yếu; Req 3.3 yêu cầu < 1s trên môi
#   trường tham chiếu).
# - test_n_150_does_not_reject: p có 151 phần tử, assert MCMSolver(p).cost >= 0
#   (chỉ cần không reject input hợp lệ — Req 3.4 graceful degradation).
# ===========================================================================
import time


def test_n_100_under_one_second() -> None:
    """Performance: n=100 hoàn tất trong < 2.0 giây.

    Req 3.3 yêu cầu < 1s trên môi trường tham chiếu. Dùng margin 2.0s
    để tránh flaky trên CI yếu hoặc máy chậm.

    Dùng random.Random(42) cố định để reproducible.
    """
    rng = random.Random(42)
    p = [rng.randint(1, 100) for _ in range(101)]  # 101 phần tử → n = 100

    start = time.perf_counter()
    solver = MCMSolver(p)
    elapsed = time.perf_counter() - start

    assert solver.cost == solver.m[1][solver.n], (
        f"Kết quả không nhất quán: cost={solver.cost}, m[1][n]={solver.m[1][solver.n]}"
    )
    assert elapsed < 2.0, (
        f"Performance FAILED: n=100 mất {elapsed:.3f}s (giới hạn 2.0s)"
    )


def test_n_150_does_not_reject() -> None:
    """Graceful degradation: n=150 không bị reject, trả kết quả hợp lệ.

    Req 3.4: MCM_Solver SHALL tiếp tục tính đúng theo Recurrence_Equation
    và trả về kết quả mà không bị giới hạn cứng về thời gian.

    Dùng random.Random(42) cố định để reproducible.
    """
    rng = random.Random(42)
    p = [rng.randint(1, 100) for _ in range(151)]  # 151 phần tử → n = 150

    solver = MCMSolver(p)

    assert solver.cost >= 0, (
        f"Cost không hợp lệ: MCMSolver(p).cost={solver.cost} (mong đợi >= 0)"
    )
