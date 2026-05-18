"""Định dạng bảng `m`, bảng `s` và `Trace_Output` cho MCM_Solver.

Module này cung cấp:
- :class:`DisplayMode`: enum 3 chế độ in bảng (Req 5.1).
- :func:`format_table`: định dạng bảng `m` hoặc `s` thành chuỗi đa dòng,
  với chỉ số gốc 1, ô không dùng hiển thị "-", các cột canh lề phải
  đồng đều (Req 5.2, 5.3, 5.5, 5.6).

Hàm ``format_trace`` (gộp các thành phần thành ``Trace_Output`` đầy đủ)
sẽ được bổ sung trong task 9.1.
"""

from __future__ import annotations

from enum import Enum
from typing import Sequence


class DisplayMode(Enum):
    """Chế độ in bảng minh họa (Req 5.1).

    Ba giá trị tương ứng với ba mức độ chi tiết của ``Trace_Output``:

    - :attr:`NONE`: không in ``m_table`` lẫn ``s_table`` (Req 5.4).
    - :attr:`PARTIAL_TABLES`: in đúng MỘT trong hai bảng theo lựa chọn
      của người dùng (Req 5.3).
    - :attr:`FULL_TABLES`: in cả ``m_table`` và ``s_table`` (Req 5.2).
    """

    NONE = "none"
    PARTIAL_TABLES = "partial"
    FULL_TABLES = "full"


def _column_width(grid: Sequence[Sequence[str]]) -> int:
    """Tính độ rộng cột thống nhất cho toàn bảng.

    Theo "Display & Formatting" trong design.md:
    ``width = max(len(str(value)) for cells in use) + 2``.

    Ở đây ``grid`` đã được dựng sẵn dưới dạng ma trận chuỗi
    (gồm cả tiêu đề ``j=k``, tiêu đề hàng ``i=k``, và các ô dữ liệu),
    nên ta chỉ cần lấy độ dài tối đa của mọi ô và cộng 2 ký tự padding.
    """
    return max(len(cell) for row in grid for cell in row) + 2


def format_table(
    table: Sequence[Sequence[int]],
    label: str,
    n: int,
    *,
    kind: str,
) -> str:
    """Định dạng bảng ``m`` hoặc ``s`` thành chuỗi đa dòng.

    Tham số:
        table: bảng 2 chiều ``(n+1) x (n+1)`` với chỉ số gốc 1
            (ô index 0 là padding, không dùng).
        label: nhãn tiếng Việt in ở dòng đầu (ví dụ ``"Bảng m:"``).
        n: ``Matrix_Chain_Length``.
        kind: ``"m"`` hoặc ``"s"``. Quyết định phạm vi hàng/cột và
            tập ô không dùng.

    Trả về:
        Chuỗi đa dòng gồm: dòng nhãn, dòng tiêu đề cột ``j=k``,
        và các dòng dữ liệu mở đầu bằng ``i=k``. Các ô không dùng
        (``i > j`` cho ``m``, ``i >= j`` cho ``s``) hiển thị ``"-"``.
        Mọi cột canh lề phải với cùng một độ rộng (Req 5.6).

    Ngoại lệ:
        ValueError: nếu ``kind`` không phải ``"m"`` hoặc ``"s"``.
    """
    if kind == "m":
        # Bảng m: hàng i = 1..n, cột j = 1..n; ô không dùng khi i > j.
        i_range = range(1, n + 1)
        j_range = range(1, n + 1)

        def is_unused(i: int, j: int) -> bool:
            return i > j

    elif kind == "s":
        # Bảng s: hàng i = 1..n-1, cột j = 2..n; ô không dùng khi i >= j
        # (đường chéo + tam giác dưới đều không có ý nghĩa cho s_table).
        i_range = range(1, n)
        j_range = range(2, n + 1)

        def is_unused(i: int, j: int) -> bool:
            return i >= j

    else:
        raise ValueError("kind phải là 'm' hoặc 's'")

    # Dựng "grid" gồm tiêu đề và dữ liệu dưới dạng ma trận chuỗi.
    # Ô đầu tiên của hàng tiêu đề (tương ứng cột nhãn hàng) bỏ trống.
    header_row: list[str] = [""] + [f"j={j}" for j in j_range]
    grid: list[list[str]] = [header_row]
    for i in i_range:
        row: list[str] = [f"i={i}"]
        for j in j_range:
            if is_unused(i, j):
                row.append("-")
            else:
                row.append(str(table[i][j]))
        grid.append(row)

    # Tính độ rộng cột thống nhất rồi canh lề phải mọi ô.
    width = _column_width(grid)
    lines: list[str] = [label]
    for row in grid:
        lines.append(" ".join(cell.rjust(width) for cell in row))
    return "\n".join(lines)


def format_trace(
    p: list[int],
    m: list[list[int]],
    s: list[list[int]],
    display_mode: DisplayMode,
    partial_choice: str | None = None,
) -> str:
    """Sinh Trace_Output theo Req 5 và Req 9.

    Gộp bảng ``m``/``s`` (tùy ``display_mode``), chuỗi đóng ngoặc tối ưu,
    và số phép nhân vô hướng tối thiểu thành một chuỗi đa dòng.

    Args:
        p: Dimension_Array gốc (dùng để suy ``n`` và gọi
            :func:`~mcm.solver.print_optimal_parens`).
        m: bảng ``m_table`` do :func:`~mcm.solver.matrix_chain_order` trả về.
        s: bảng ``s_table`` do :func:`~mcm.solver.matrix_chain_order` trả về.
        display_mode: chế độ in bảng (Req 5.1).
        partial_choice: bắt buộc khi ``display_mode == PARTIAL_TABLES``;
            phải là ``"m"`` hoặc ``"s"``. Bị bỏ qua ở các mode khác.

    Returns:
        Chuỗi đa dòng. Cấu trúc::

            [Bảng m: ...]      (nếu mode in m)
            [Bảng s: ...]      (nếu mode in s)
            Cách đóng mở ngoặc tối ưu: <parens>
            Số phép nhân vô hướng tối thiểu: <cost>

    Raises:
        ValueError: với message tiếng Việt nếu ``display_mode`` là
            ``PARTIAL_TABLES`` mà ``partial_choice`` không phải ``'m'``
            hoặc ``'s'``.
    """
    from mcm.solver import print_optimal_parens

    n = len(p) - 1
    parens = print_optimal_parens(s, 1, n)
    cost = m[1][n]
    parts: list[str] = []

    if display_mode is DisplayMode.FULL_TABLES:  # Req 5.2
        parts.append(format_table(m, "Bảng m:", n, kind="m"))
        parts.append(format_table(s, "Bảng s:", n, kind="s"))
    elif display_mode is DisplayMode.PARTIAL_TABLES:  # Req 5.3
        if partial_choice == "m":
            parts.append(format_table(m, "Bảng m:", n, kind="m"))
        elif partial_choice == "s":
            parts.append(format_table(s, "Bảng s:", n, kind="s"))
        else:
            raise ValueError(
                "Khi display_mode = PARTIAL_TABLES, partial_choice phải là 'm' hoặc 's'"
            )
    # display_mode == NONE: không append bảng (Req 5.4, 5.7)

    # Hai dòng cuối luôn có (Req 5.7, 5.8, 9.1):
    parts.append(f"Cách đóng mở ngoặc tối ưu: {parens}")
    parts.append(f"Số phép nhân vô hướng tối thiểu: {cost}")
    return "\n".join(parts)


__all__ = ["DisplayMode", "format_table", "format_trace"]
