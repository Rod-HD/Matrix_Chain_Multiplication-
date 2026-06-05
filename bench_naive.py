"""So sánh số lần gọi đệ quy giữa lời giải thuần và bản có ghi nhớ.

Đếm số lần hàm cost(i, j) được gọi trong bản đệ quy thuần (không ghi nhớ)
so với bản top-down memoization, để minh hoạ vì sao cần quy hoạch động.

Chạy từ thư mục gốc dự án:
    python bench_naive.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mcm2.core import count_parenthesizations  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def naive_calls(n: int) -> int:
    """Đếm số lần gọi cost(i, j) của bản đệ quy thuần cho chuỗi n ma trận."""
    counter = 0

    def cost(i: int, j: int) -> None:
        nonlocal counter
        counter += 1
        if i == j:
            return
        for k in range(i, j):
            cost(i, k)
            cost(k + 1, j)

    cost(0, n - 1)
    return counter


def memo_calls(n: int) -> int:
    """Đếm số lần tính thực sự (không tính lần trúng cache) của bản ghi nhớ."""
    computed = 0
    seen: set[tuple[int, int]] = set()

    def cost(i: int, j: int) -> None:
        nonlocal computed
        if (i, j) in seen:
            return
        seen.add((i, j))
        computed += 1
        if i == j:
            return
        for k in range(i, j):
            cost(i, k)
            cost(k + 1, j)

    cost(0, n - 1)
    return computed


def main() -> int:
    print(f"{'n':>4} | {'gọi (thuần)':>14} | {'tính (ghi nhớ)':>16} | {'số Catalan':>14}")
    print("-" * 60)
    for n in range(2, 16):
        nc = naive_calls(n)
        mc = memo_calls(n)
        cat = count_parenthesizations(n)
        print(f"{n:>4} | {nc:>14,} | {mc:>16,} | {cat:>14,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
