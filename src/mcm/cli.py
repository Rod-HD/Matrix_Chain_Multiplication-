"""Entry point CLI cho MCM — đọc argv/stdin, gọi solver, in kết quả ra stdout.

Module này là nơi duy nhất thực hiện I/O (đọc stdin, ghi stdout/stderr).
Mọi logic tính toán và định dạng nằm ở các module khác (solver, formatter).

Sử dụng:
    python -m mcm 30 35 15 5 10 20 25 --mode=full
    echo "30 35 15 5 10 20 25" | python -m mcm --mode=partial --table=m
"""

import argparse
import sys

from mcm.solver import MCMSolver
from mcm.formatter import DisplayMode, format_trace


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Phân tích dòng lệnh theo thiết kế CLI trong design.md.

    Args:
        argv: danh sách argument (không bao gồm tên chương trình).

    Returns:
        Namespace chứa ``dims``, ``mode``, ``table``.
    """
    parser = argparse.ArgumentParser(prog="mcm")
    parser.add_argument(
        "dims",
        nargs="*",
        type=int,
        help="Dimension_Array p (cách nhau bằng khoảng trắng). "
        "Nếu rỗng, đọc từ stdin.",
    )
    parser.add_argument(
        "--mode",
        choices=["none", "partial", "full"],
        default="full",
    )
    parser.add_argument(
        "--table",
        choices=["m", "s"],
        default="m",
        help="Chỉ áp dụng khi --mode=partial",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Hàm chính của CLI. Trả exit code (0 = OK, 1 = lỗi input, 2 = lỗi khác).

    Args:
        argv: danh sách argument. Nếu ``None``, dùng ``sys.argv[1:]``.

    Returns:
        Exit code: 0 thành công, 1 ValueError (lỗi input), 2 RuntimeError
        hoặc exception khác.
    """
    args = parse_args(sys.argv[1:] if argv is None else argv)

    # Đọc dims từ positional args hoặc stdin nếu rỗng.
    dims = args.dims if args.dims else [int(x) for x in sys.stdin.read().split()]

    # Req 3.4: graceful degradation cho n lớn — tăng recursion limit
    # trước khi build parens (print_optimal_parens là đệ quy).
    n_estimate = len(dims) - 1
    if n_estimate > 500:
        sys.setrecursionlimit(max(1000, n_estimate + 100))

    try:
        solver = MCMSolver(dims)
    except ValueError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    except (RuntimeError, Exception) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2

    # Ánh xạ chuỗi mode sang enum DisplayMode.
    mode_map = {
        "none": DisplayMode.NONE,
        "partial": DisplayMode.PARTIAL_TABLES,
        "full": DisplayMode.FULL_TABLES,
    }

    try:
        output = format_trace(
            solver.p,
            solver.m,
            solver.s,
            mode_map[args.mode],
            partial_choice=args.table if args.mode == "partial" else None,
        )
        print(output)
    except (RuntimeError, Exception) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
