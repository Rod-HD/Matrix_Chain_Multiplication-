"""Định dạng bảng và kết quả thành văn bản dễ đọc.

Module này chỉ lo phần trình bày; mọi tính toán đã nằm ở core.py. Bảng
được in với nhãn hàng/cột theo chỉ số 1-based (A1..An) khớp ký hiệu CLRS.
Bảng cost và split từ core.py đều là (n+1)×(n+1) với padding tại index 0;
formatter đọc từ index 1..n và in nhãn 1..n trực tiếp.
Ô không dùng hiển thị dấu "-" và mọi cột canh phải để thẳng hàng.
"""

from __future__ import annotations

from typing import Sequence

from mcm2.core import ChainResult


def _render_grid(rows: list[list[str]]) -> str:
    """Canh phải mọi ô theo một độ rộng cột thống nhất rồi nối thành chuỗi.

    Tham số:
        rows: lưới chuỗi (đã gồm cả tiêu đề hàng/cột).

    Trả về:
        Chuỗi nhiều dòng, các cột thẳng hàng.
    """
    width = max((len(cell) for row in rows for cell in row), default=1) + 2
    lines = [" ".join(cell.rjust(width) for cell in row) for row in rows]
    return "\n".join(lines)


def format_cost_table(cost: list[list[int]], n: int) -> str:
    """Định dạng bảng chi phí thành văn bản.

    Tham số:
        cost: bảng chi phí (n+1) x (n+1), chỉ số 1-based (CLRS).
        n: số ma trận.

    Trả về:
        Chuỗi bảng, hàng/cột gắn nhãn 1..n; ô i > j (không dùng) là "-".
    """
    header = [""] + [str(j) for j in range(1, n + 1)]
    rows = [header]
    for i in range(1, n + 1):
        row = [str(i)]
        for j in range(1, n + 1):
            row.append("-" if i > j else str(cost[i][j]))
        rows.append(row)
    return _render_grid(rows)


def format_split_table(split: list[list[int]], n: int) -> str:
    """Định dạng bảng vị trí cắt thành văn bản.

    Giá trị cắt đã là 1-based (chỉ số ma trận theo CLRS), hiển thị trực tiếp.
    Ô i >= j không dùng, hiển thị "-".

    Tham số:
        split: bảng vị trí cắt (n+1) x (n+1), chỉ số 1-based (CLRS).
        n: số ma trận.

    Trả về:
        Chuỗi bảng vị trí cắt.
    """
    header = [""] + [str(j) for j in range(1, n + 1)]
    rows = [header]
    for i in range(1, n + 1):
        row = [str(i)]
        for j in range(1, n + 1):
            row.append("-" if i >= j else str(split[i][j]))
        rows.append(row)
    return _render_grid(rows)


def render_result(
    result: ChainResult,
    *,
    show_cost: bool = True,
    show_split: bool = True,
) -> str:
    """Ghép bảng (tuỳ chọn) cùng đáp số thành báo cáo văn bản hoàn chỉnh.

    Tham số:
        result: kết quả từ core.solve.
        show_cost: có in bảng chi phí hay không.
        show_split: có in bảng vị trí cắt hay không.

    Trả về:
        Chuỗi nhiều dòng gồm các bảng đã chọn, dấu ngoặc tối ưu và chi phí.
    """
    parts: list[str] = []
    if show_cost:
        parts.append("Bảng chi phí (số phép nhân tối thiểu của từng đoạn):")
        parts.append(format_cost_table(result.cost, result.n))
    if show_split:
        parts.append("Bảng vị trí cắt tối ưu:")
        parts.append(format_split_table(result.split, result.n))
    parts.append(f"Dấu ngoặc tối ưu: {result.parenthesization}")
    parts.append(f"Số phép nhân vô hướng tối thiểu: {result.min_cost}")
    return "\n".join(parts)
