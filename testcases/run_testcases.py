"""Chạy và chấm bộ testcase tường minh cho mcm2.

Nạp ``cases.json``, chạy từng ca qua ``solve`` rồi đối chiếu với giá trị
mong đợi. In bảng PASS/FAIL và trả mã thoát khác 0 nếu có ca sai (tiện cho
việc chấm tự động).

Chạy từ thư mục gốc dự án::

    python testcases/run_testcases.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Thêm src/ vào đường dẫn để chạy được kể cả khi chưa cài gói.
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from mcm2 import solve  # noqa: E402
from mcm2.validation import DimensionError  # noqa: E402

# Windows console mặc định không phải UTF-8: ép lại để in tiếng Việt.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def run_valid(cases: list[dict]) -> tuple[int, int]:
    """Chạy nhóm ca hợp lệ, trả về (số ca đúng, tổng số ca)."""
    passed = 0
    print("=" * 70)
    print("NHÓM HỢP LỆ - kiểm tra chi phí và dấu ngoặc")
    print("=" * 70)
    for c in cases:
        result = solve(c["dims"])
        ok_cost = result.min_cost == c["expected_cost"]
        ok_parens = result.parenthesization == c["expected_parens"]
        ok = ok_cost and ok_parens
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {c['id']}: dims={c['dims']}")
        print(f"        {c['desc']}")
        print(
            f"        chi phí : nhận {result.min_cost} / "
            f"mong đợi {c['expected_cost']} "
            f"{'OK' if ok_cost else 'SAI'}"
        )
        print(
            f"        ngoặc   : nhận {result.parenthesization} / "
            f"mong đợi {c['expected_parens']} "
            f"{'OK' if ok_parens else 'SAI'}"
        )
    return passed, len(cases)


def run_invalid(cases: list[dict]) -> tuple[int, int]:
    """Chạy nhóm ca sai, trả về (số ca đúng, tổng số ca)."""
    passed = 0
    print()
    print("=" * 70)
    print("NHÓM SAI - kiểm tra đúng thông điệp lỗi")
    print("=" * 70)
    for c in cases:
        try:
            solve(c["dims"])
            actual = "(không báo lỗi)"
            ok = False
        except DimensionError as exc:
            actual = str(exc)
            ok = actual == c["expected_error"]
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {c['id']}: dims={c['dims']}")
        print(f"        {c['desc']}")
        print(f"        lỗi nhận    : {actual}")
        print(f"        lỗi mong đợi: {c['expected_error']}")
    return passed, len(cases)


def main() -> int:
    data = json.loads(
        (Path(__file__).resolve().parent / "cases.json").read_text("utf-8")
    )
    pv, nv = run_valid(data["valid"])
    pi, ni = run_invalid(data["invalid"])
    total_pass = pv + pi
    total = nv + ni
    print()
    print("=" * 70)
    print(
        f"TỔNG KẾT: {total_pass}/{total} ca PASS "
        f"(hợp lệ {pv}/{nv}, sai {pi}/{ni})"
    )
    print("=" * 70)
    return 0 if total_pass == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
