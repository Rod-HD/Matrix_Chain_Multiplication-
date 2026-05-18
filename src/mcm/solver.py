"""Solver lõi cho bài toán Matrix Chain Multiplication (MCM).

Module này triển khai hai thủ tục theo mã giả CLRS chương 15.2 (cũng là mã giả
trong slide bài giảng môn "Phân tích và Thiết kế Thuật toán"):

- ``MATRIX-CHAIN-ORDER(p)``: tính bảng chi phí ``m`` và bảng vị trí tách ``s``.
- ``PRINT-OPTIMAL-PARENS(s, i, j)``: truy vết bảng ``s`` để dựng chuỗi đóng mở
  ngoặc tối ưu.

Quy ước chỉ số: dùng **1-based padding** — các bảng ``m`` và ``s`` có kích thước
``(n+1) × (n+1)``, ô tại index ``0`` không sử dụng. Cách padding này giúp code
Python truy cập ``m[i][j]``, ``s[i][j]`` mirror **đúng từng dòng** mã giả CLRS,
không phải dịch ``[i-1]`` ở mọi nơi.
"""

import math
from io import StringIO

from mcm.validator import validate_dimension_array


def matrix_chain_order(
    p: list[int],
) -> tuple[list[list[int]], list[list[int]]]:
    """Cài đặt 1-1 mã giả MATRIX-CHAIN-ORDER (CLRS 15.2).

    Sử dụng 1-based indexing thông qua padding: ``m`` và ``s`` là
    ``(n+1) × (n+1)``, ô index 0 không dùng. Truy cập ``m[i][j]`` với
    ``1 <= i, j <= n`` mirror đúng mã giả CLRS.

    Args:
        p: Dimension_Array đã hợp lệ (validator gọi trước). Ma trận ``A_i``
            có kích thước ``p[i-1] x p[i]``, với ``1 <= i <= n``.

    Returns:
        Cặp ``(m, s)``:

        - ``m[i][j]``: Scalar_Multiplication_Count tối thiểu để nhân chuỗi
          ``A_i .. A_j``. ``m[i][i] = 0``; ô ``i > j`` không sử dụng (giữ
          giá trị khởi tạo ``0``).
        - ``s[i][j]``: Split_Position tối ưu, thỏa ``i <= s[i][j] < j``;
          ô ``i >= j`` không sử dụng (giữ giá trị khởi tạo ``0``).
    """
    # Dòng 1: n = p.length - 1
    n = len(p) - 1

    # Dòng 2: cấp phát hai bảng kích thước (n+1) × (n+1).
    # Index 0 là padding (không dùng) để truy cập 1-based mirror mã giả CLRS.
    m: list[list[int | float]] = [[0] * (n + 1) for _ in range(n + 1)]
    s: list[list[int]] = [[0] * (n + 1) for _ in range(n + 1)]

    # Dòng 3-4: khởi tạo đường chéo m[i][i] = 0.
    # (List comprehension đã khởi tạo 0, vòng lặp giữ tường minh để mirror mã giả.)
    for i in range(1, n + 1):
        m[i][i] = 0  # dòng 4

    # Dòng 5: vòng ngoài theo độ dài chuỗi con l = 2..n.
    # (Đặt tên biến `length` thay vì `l` để tránh nhầm chữ `l` với chữ số `1`;
    #  comment vẫn giữ ký hiệu `l` theo mã giả.)
    for length in range(2, n + 1):  # l = 2 to n
        # Dòng 6: vòng giữa theo chỉ số bắt đầu i = 1..n - l + 1.
        # range exclusive cuối, nên giới hạn trên là (n - length + 2).
        for i in range(1, n - length + 2):
            # Dòng 7: chỉ số kết thúc của chuỗi con A_i..A_j.
            j = i + length - 1
            # Dòng 8: khởi tạo m[i][j] = +∞ trước khi tìm Split_Position.
            # Sử dụng math.inf thay vì magic number để code đọc gần mã giả;
            # `q` đầu tiên ở dòng 10 luôn nhỏ hơn inf, nên m[i][j] sau vòng
            # `k` luôn là một số nguyên (int).
            m[i][j] = math.inf
            # Dòng 9: vòng trong duyệt mọi Split_Position k = i..j - 1.
            for k in range(i, j):
                # Dòng 10: công thức truy hồi (Recurrence_Equation):
                #     q = m[i][k] + m[k+1][j] + p_{i-1} * p_k * p_j
                q = m[i][k] + m[k + 1][j] + p[i - 1] * p[k] * p[j]
                # Dòng 11-13: nếu q tốt hơn, cập nhật cả cost và split position.
                if q < m[i][j]:
                    m[i][j] = q  # dòng 12
                    s[i][j] = k  # dòng 13

    # Dòng 14: trả về cặp (m, s).
    return m, s


def print_optimal_parens(
    s: list[list[int]],
    i: int,
    j: int,
) -> str:
    """Cài đặt 1-1 mã giả PRINT-OPTIMAL-PARENS (CLRS 15.2).

    Trả về chuỗi (str) thay vì in trực tiếp ra stdout, để dễ unit-test
    (Req 4.4) và tách trách nhiệm I/O sang tầng CLI.

    Args:
        s: bảng ``s_table`` do :func:`matrix_chain_order` trả về.
        i: chỉ số bắt đầu (1-based), thỏa ``1 <= i <= j``.
        j: chỉ số kết thúc (1-based), thỏa ``i <= j <= n``.

    Returns:
        Optimal_Parenthesization của chuỗi con ``A_i .. A_j``. Ví dụ:
        ``"((A1(A2A3))A4)"``. Khi ``i == j`` trả về ``f"A{i}"`` (Req 4.5).
    """
    # Wrapper public: tạo accumulator StringIO, gọi hàm đệ quy ghi vào buffer,
    # rồi trả về chuỗi kết quả. Cấu trúc accumulator giúp giữ nguyên thứ tự
    # `print "("`, gọi đệ quy, `print ")"` như mã giả CLRS.
    buf = StringIO()
    _print_optimal_parens_into(s, i, j, buf)
    return buf.getvalue()


def _print_optimal_parens_into(
    s: list[list[int]],
    i: int,
    j: int,
    buf: StringIO,
) -> None:
    """Hàm đệ quy nội bộ ghi parens vào ``buf`` theo mã giả CLRS.

    Mỗi dòng ``print`` trong mã giả tương ứng một ``buf.write`` ở đây, để
    cấu trúc đệ quy không-trả-về bám sát slide (thay vì dồn return string).
    """
    if i == j:                                                # dòng 1
        # Dòng 2: in "A_i" cho ma trận đơn lẻ.
        buf.write(f"A{i}")
    else:                                                     # dòng 3
        # Dòng 4: mở ngoặc cho chuỗi con A_i..A_j.
        buf.write("(")
        # Dòng 5: đệ quy nửa trái A_i..A_{s[i][j]}.
        _print_optimal_parens_into(s, i, s[i][j], buf)
        # Dòng 6: đệ quy nửa phải A_{s[i][j]+1}..A_j.
        _print_optimal_parens_into(s, s[i][j] + 1, j, buf)
        # Dòng 7: đóng ngoặc.
        buf.write(")")


def _recompute_cost_from_parens(
    s: list[list[int]],
    p: list[int],
    i: int,
    j: int,
) -> int:
    """Tính lại Scalar_Multiplication_Count từ ``s_table`` (không dùng ``m_table``).

    Đệ quy theo bảng ``s`` theo đúng cấu trúc Optimal_Parenthesization để
    tính lại tổng số phép nhân vô hướng. Mục đích: cross-check kết quả
    ``m[1][n]`` (Req 7.6) — nếu hai con số khác nhau, có sai sót cài đặt.

    Đồng thời chặn trường hợp ``s[i][j]`` nằm ngoài khoảng cho phép
    ``[i, j - 1]`` — đây là một dạng bất nhất quán nội bộ phải báo lỗi.

    Args:
        s: bảng ``s_table`` do :func:`matrix_chain_order` trả về.
        p: Dimension_Array gốc.
        i: chỉ số bắt đầu (1-based), thỏa ``1 <= i <= j``.
        j: chỉ số kết thúc (1-based), thỏa ``i <= j <= n``.

    Returns:
        Tổng số phép nhân vô hướng tính lại từ ``s`` cho chuỗi con
        ``A_i .. A_j``.

    Raises:
        ValueError: với message tiếng Việt nguyên văn nếu
            ``s[i][j]`` nằm ngoài khoảng ``[i, j - 1]``.
    """
    # Trường hợp cơ sở: chuỗi gồm một ma trận không cần phép nhân nào.
    if i == j:
        return 0

    # Lấy Split_Position tối ưu cho chuỗi con A_i..A_j.
    k = s[i][j]

    # Bảo vệ: split position phải thỏa i <= k < j (xem Req 7.6).
    # Nếu sai khoảng, bảng s đã bị hỏng (bug cài đặt hoặc dữ liệu bị mutate).
    if not (i <= k < j):
        raise ValueError(
            f"Bất nhất quán: s[{i}][{j}] = {k} nằm ngoài khoảng [{i}, {j - 1}]"
        )

    # Đệ quy hai nửa: A_i..A_k và A_{k+1}..A_j.
    left = _recompute_cost_from_parens(s, p, i, k)
    right = _recompute_cost_from_parens(s, p, k + 1, j)

    # Cộng thêm chi phí phép nhân ma trận kết hợp hai nửa: p[i-1] * p[k] * p[j].
    return left + right + p[i - 1] * p[k] * p[j]


def _assert_consistent(
    m: list[list[int]],
    s: list[list[int]],
    p: list[int],
    n: int,
) -> None:
    """Cross-check ``m[1][n]`` với chi phí suy ra từ ``s_table`` (Req 7.6).

    Tính lại tổng số phép nhân vô hướng bằng cách đệ quy theo bảng ``s``
    (không dùng ``m_table``) qua :func:`_recompute_cost_from_parens`, rồi
    so sánh với ``m[1][n]``. Nếu hai giá trị khác nhau thì kết quả thuật
    toán bất nhất quán — báo lỗi ngay để chặn output sai.

    Args:
        m: bảng ``m_table`` do :func:`matrix_chain_order` trả về.
        s: bảng ``s_table`` do :func:`matrix_chain_order` trả về.
        p: Dimension_Array gốc.
        n: Matrix_Chain_Length (``len(p) - 1``).

    Raises:
        ValueError: nếu ``s_table`` chứa Split_Position nằm ngoài khoảng
            (propagate từ :func:`_recompute_cost_from_parens`).
        RuntimeError: với message tiếng Việt nguyên văn nếu chi phí tính
            lại từ ``s`` khác với ``m[1][n]``.
    """
    # Tính lại chi phí thuần từ s_table (không tham chiếu m_table).
    recomputed = _recompute_cost_from_parens(s, p, 1, n)

    # So khớp với m[1][n]; sai khác là dấu hiệu bất nhất quán nội bộ.
    if recomputed != m[1][n]:
        raise RuntimeError(
            f"Bất nhất quán: m[1][{n}] = {m[1][n]} "
            f"nhưng chi phí suy ra từ Optimal_Parenthesization là {recomputed}"
        )


class MCMSolver:
    """Facade gói validator + matrix_chain_order + print_optimal_parens
    + consistency check trong một call duy nhất, tiện cho cli và test.

    Sử dụng khi cần giữ kết quả lại để format theo nhiều mode khác nhau.
    """

    def __init__(self, p: list[int]) -> None:
        self.n: int = validate_dimension_array(p)
        self.p: list[int] = list(p)
        self.m, self.s = matrix_chain_order(self.p)
        self.parens: str = print_optimal_parens(self.s, 1, self.n)
        self.cost: int = self.m[1][self.n]
        _assert_consistent(self.m, self.s, self.p, self.n)  # Req 7.6

    @property
    def trace(self) -> dict:
        """Trả dict chứa toàn bộ kết quả tính toán."""
        return {
            "n": self.n,
            "p": self.p,
            "m": self.m,
            "s": self.s,
            "parens": self.parens,
            "cost": self.cost,
        }
