"""Đo thời gian chạy của lời giải bottom-up theo kích thước n.

Sinh mảng kích thước ngẫu nhiên với seed cố định để tái lập, đo thời gian
chạy bottom_up bằng time.perf_counter (lấy giá trị nhỏ nhất qua nhiều lần
lặp), và đối chiếu tỉ lệ tăng với dự đoán lý thuyết Theta(n^3).

Chạy từ thư mục gốc dự án:
    python benchmark.py
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mcm2.core import bottom_up  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def measure(n: int, repeats: int = 5) -> float:
    """Trả về thời gian chạy nhỏ nhất (giây) của bottom_up cho chuỗi n ma trận."""
    rng = random.Random(20260601 + n)
    dims = [rng.randint(1, 100) for _ in range(n + 1)]
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        bottom_up(dims)
        best = min(best, time.perf_counter() - start)
    return best


def main() -> int:
    sizes = [50, 100, 150, 200, 300, 400]
    print(f"{'n':>5} | {'thời gian (ms)':>16} | {'tỉ lệ so với n/2':>18}")
    print("-" * 48)
    prev_n = None
    prev_t = None
    for n in sizes:
        t = measure(n)
        ratio = ""
        if prev_t is not None and prev_n is not None and n == prev_n * 2:
            ratio = f"{t / prev_t:6.2f}x (lý thuyết 8x)"
        print(f"{n:>5} | {t * 1000:>16.2f} | {ratio:>18}")
        prev_n, prev_t = n, t
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
