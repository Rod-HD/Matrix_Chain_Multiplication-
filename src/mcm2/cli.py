"""Giao diện dòng lệnh cho mcm2.

Đây là nơi duy nhất đụng tới vào/ra (đọc tham số / stdin, ghi stdout /
stderr). Mọi tính toán nằm ở core.py, mọi định dạng nằm ở display.py.

Ví dụ::

    python -m mcm2 30 35 15 5 10 20 25
    python -m mcm2 30 35 15 5 10 20 25 --tables=cost
    echo 30 35 15 5 10 20 25 | python -m mcm2 --tables=none
"""

from __future__ import annotations

import argparse
import sys

from mcm2.core import solve
from mcm2.display import render_result
from mcm2.validation import DimensionError


def build_parser() -> argparse.ArgumentParser:
    """Tạo bộ phân tích tham số dòng lệnh."""
    parser = argparse.ArgumentParser(
        prog="mcm2",
        description="Giải bài toán Matrix Chain Multiplication.",
    )
    parser.add_argument(
        "dims",
        nargs="*",
        type=int,
        help="Mảng kích thước p, cách nhau bằng khoảng trắng. "
        "Bỏ trống thì đọc từ stdin.",
    )
    parser.add_argument(
        "--tables",
        choices=["both", "cost", "split", "none"],
        default="both",
        help="Chọn bảng để in: cả hai (both), chỉ chi phí (cost), "
        "chỉ vị trí cắt (split), hoặc không in bảng (none).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Điểm vào CLI. Trả mã thoát: 0 thành công, 1 lỗi dữ liệu, 2 lỗi khác.

    Tham số:
        argv: danh sách tham số (không gồm tên chương trình). Nếu None thì
            lấy từ sys.argv[1:].

    Trả về:
        Mã thoát tiến trình.
    """
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)

    # Lấy mảng kích thước từ tham số, hoặc từ stdin nếu không truyền.
    if args.dims:
        dims = args.dims
    else:
        dims = [int(token) for token in sys.stdin.read().split()]

    # Nâng giới hạn đệ quy cho chuỗi rất dài (truy vết dấu ngoặc là đệ quy).
    n_estimate = len(dims) - 1
    if n_estimate > 500:
        sys.setrecursionlimit(max(1000, n_estimate + 100))

    try:
        result = solve(dims)
    except DimensionError as exc:
        print(f"Lỗi dữ liệu: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2

    show_cost = args.tables in ("both", "cost")
    show_split = args.tables in ("both", "split")
    print(render_result(result, show_cost=show_cost, show_split=show_split))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
