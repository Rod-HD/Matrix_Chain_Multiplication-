"""Ứng dụng web demo cho Matrix Chain Multiplication.

Một endpoint trang chủ và một endpoint API. API nhận mảng kích thước, giải
bằng bottom-up, trả về bảng chi phí, bảng vị trí cắt, dấu ngoặc tối ưu và
toàn bộ các bước lấp bảng để giao diện minh hoạ trực quan.

Chạy:
    pip install flask
    python web_app.py        # mở http://127.0.0.1:5001
"""

from __future__ import annotations

import sys
from pathlib import Path

# Cho phép chạy trực tiếp mà chưa cài gói: thêm src/ vào sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from flask import Flask, jsonify, render_template, request  # noqa: E402

from mcm2.core import bottom_up, optimal_parenthesization, count_parenthesizations  # noqa: E402
from mcm2.validation import validate_dimensions, DimensionError  # noqa: E402

app = Flask(__name__)


@app.route("/")
def index():
    """Trả trang chủ."""
    return render_template("index.html")


@app.route("/api/solve", methods=["POST"])
def api_solve():
    """Giải bài toán và trả kết quả dạng JSON cho giao diện."""
    data = request.get_json(force=True, silent=True) or {}
    raw = data.get("dims", [])

    # Nhận mảng từ JSON. Không ép int ở đây — giữ nguyên giá trị để
    # validate_dimensions có thể phát hiện float, âm, ... và báo lỗi đúng.
    try:
        raw_vals = list(raw)
    except TypeError:
        return jsonify({"error": "dims phải là một mảng"}), 400

    # Chuyển về int nếu là số nguyên (kể cả float dạng 3.0), giữ nguyên float thật
    dims_raw = []
    for x in raw_vals:
        try:
            f = float(x)
        except (ValueError, TypeError):
            return jsonify({"error": "Mọi phần tử kích thước phải là số"}), 400
        # Giữ nguyên kiểu: float thật (2.5) truyền vào để validator báo lỗi
        if f == int(f) and isinstance(x, (int, float)) and not isinstance(x, bool):
            dims_raw.append(int(f))
        else:
            dims_raw.append(f)

    try:
        n = validate_dimensions(dims_raw)
    except DimensionError as exc:
        return jsonify({"error": str(exc)}), 400

    dims = [int(x) for x in dims_raw]  # đã hợp lệ, an toàn ép int

    cost, split = bottom_up(dims)
    parens = optimal_parenthesization(split, 1, n)
    steps = _build_steps(dims, n)

    # Đưa bảng về dạng list 2 chiều có None ở ô không dùng, tiện cho front-end.
    # Bỏ row/col index 0 (padding), trả về ma trận n x n theo thứ tự A1..An.
    cost_view = [
        [None if i > j else cost[i][j] for j in range(1, n + 1)]
        for i in range(1, n + 1)
    ]
    split_view = [
        [None if i >= j else split[i][j] for j in range(1, n + 1)]
        for i in range(1, n + 1)
    ]

    return jsonify(
        {
            "n": n,
            "dims": dims,
            "min_cost": cost[1][n],
            "parenthesization": parens,
            "num_parenthesizations": count_parenthesizations(n),
            "cost_table": cost_view,
            "split_table": split_view,
            "steps": steps,
        }
    )


def _build_steps(p: list[int], n: int) -> list[dict]:
    """Tái dựng từng bước lấp bảng để giao diện chiếu lại.

    Mỗi bước ứng với một ô (i, j) và liệt kê mọi vị trí cắt k đã thử cùng
    công thức chi tiết, đánh dấu lựa chọn tối ưu.
    Dùng chỉ số 1-based cho cả ma trận lẫn bảng (theo CLRS).
    """
    cost = [[0] * (n + 1) for _ in range(n + 1)]
    split = [[0] * (n + 1) for _ in range(n + 1)]
    steps: list[dict] = []

    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            best = float("inf")
            best_k = i
            candidates = []
            for k in range(i, j):
                # Công thức CLRS: p[i-1] * p[k] * p[j]
                q = cost[i][k] + cost[k + 1][j] + p[i - 1] * p[k] * p[j]
                candidates.append(
                    {
                        "k": k,
                        "value": q,
                        "formula": (
                            f"cost[{i}][{k}] + cost[{k + 1}][{j}] "
                            f"+ p[{i - 1}]*p[{k}]*p[{j}] = "
                            f"{cost[i][k]} + {cost[k + 1][j]} + "
                            f"{p[i - 1] * p[k] * p[j]} = {q}"
                        ),
                    }
                )
                if q < best:
                    best = q
                    best_k = k
            cost[i][j] = best
            split[i][j] = best_k
            steps.append(
                {
                    "length": length,
                    "i": i,
                    "j": j,
                    "candidates": candidates,
                    "best_k": best_k,
                    "best_cost": int(best),
                }
            )
    return steps


if __name__ == "__main__":
    # Cổng 5001 để không đụng cổng 5000 nếu có service khác.
    app.run(debug=True, port=5001)
