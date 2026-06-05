"""Gói mcm2 - lời giải bài toán Matrix Chain Multiplication.

Cài đặt bài toán theo hướng quy hoạch động trên đoạn (interval dynamic
programming) với chỉ số gốc 0, và cung cấp ba cách giải để đối chiếu:

    - giải đệ quy thuần (mũ) - dùng để minh hoạ vì sao cần quy hoạch động;
    - giải đệ quy có ghi nhớ (top-down memoization) - O(n^3);
    - giải lấp bảng từ dưới lên (bottom-up) - O(n^3), kèm truy vết dấu ngoặc.

Các tên được gom về đây để import ngắn gọn::

    from mcm2 import solve, bottom_up, optimal_parenthesization
"""

from mcm2.validation import validate_dimensions
from mcm2.core import (
    naive_min_cost,
    memoized_min_cost,
    bottom_up,
    optimal_parenthesization,
    count_parenthesizations,
    ChainResult,
    solve,
)
from mcm2.display import format_cost_table, format_split_table, render_result

__all__ = [
    "validate_dimensions",
    "naive_min_cost",
    "memoized_min_cost",
    "bottom_up",
    "optimal_parenthesization",
    "count_parenthesizations",
    "ChainResult",
    "solve",
    "format_cost_table",
    "format_split_table",
    "render_result",
]
