"""Flask web app cho Matrix Chain Multiplication — UI Demo."""

from flask import Flask, jsonify, render_template, request

from mcm.solver import matrix_chain_order, print_optimal_parens, MCMSolver
from mcm.formatter import DisplayMode, format_table

app = Flask(__name__)


@app.route("/")
def index():
    """Trả về trang chủ."""
    return render_template("index.html")


@app.route("/api/solve", methods=["POST"])
def solve():
    """Nhận Dimension_Array và trả về kết quả MCM.

    Body JSON:
        dims (list[int]): Dimension_Array p.

    Returns:
        JSON kết quả hoặc {"error": "..."}.
    """
    try:
        data = request.get_json(force=True)
        dims = data.get("dims", [])

        # Validate input type
        if not isinstance(dims, list):
            return jsonify({"error": "dims phải là một mảng"}), 400

        # Convert to int
        try:
            dims = [int(x) for x in dims]
        except (ValueError, TypeError):
            return jsonify({"error": "Mọi phần tử của Dimension_Array phải là số nguyên"}), 400

        # Solve
        solver = MCMSolver(dims)

        # Build m_table and s_table as 2D arrays (1-based, for display)
        n = solver.n
        m_display = []
        for i in range(1, n + 1):
            row = []
            for j in range(1, n + 1):
                if i > j:
                    row.append(None)  # unused cell
                else:
                    row.append(solver.m[i][j])
            m_display.append(row)

        s_display = []
        for i in range(1, n + 1):
            row = []
            for j in range(1, n + 1):
                if i >= j:
                    row.append(None)  # unused cell
                else:
                    row.append(solver.s[i][j])
            s_display.append(row)

        # Build step-by-step computation for visualization
        steps = _build_steps(dims, n)

        return jsonify({
            "n": n,
            "p": dims,
            "cost": solver.cost,
            "parens": solver.parens,
            "m_table": m_display,
            "s_table": s_display,
            "steps": steps,
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _build_steps(p, n):
    """Xây dựng các bước tính toán chi tiết cho visualization."""
    import math

    steps = []
    m = [[0] * (n + 1) for _ in range(n + 1)]
    s = [[0] * (n + 1) for _ in range(n + 1)]

    # Step 0: Initialization
    steps.append({
        "title": "Khởi tạo",
        "description": "Đặt m[i][i] = 0 cho mọi i = 1..n (nhân 1 ma trận không tốn chi phí)",
        "type": "init",
        "cells_updated": [{"i": i, "j": i, "value": 0} for i in range(1, n + 1)],
    })

    # Steps for each chain length
    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            m[i][j] = math.inf
            best_k = i
            candidates = []

            for k in range(i, j):
                q = m[i][k] + m[k + 1][j] + p[i - 1] * p[k] * p[j]
                candidates.append({
                    "k": k,
                    "cost": q,
                    "formula": f"m[{i}][{k}] + m[{k+1}][{j}] + p[{i-1}]·p[{k}]·p[{j}] = {m[i][k]} + {m[k+1][j]} + {p[i-1]}·{p[k]}·{p[j]} = {q}",
                })
                if q < m[i][j]:
                    m[i][j] = q
                    s[i][j] = k
                    best_k = k

            steps.append({
                "title": f"Tính m[{i}][{j}] (chuỗi dài {length}: A{i}..A{j})",
                "description": f"Thử mọi vị trí tách k = {i}..{j-1}, chọn k tối ưu",
                "type": "compute",
                "i": i,
                "j": j,
                "length": length,
                "candidates": candidates,
                "best_k": best_k,
                "best_cost": int(m[i][j]),
                "cells_updated": [
                    {"i": i, "j": j, "value": int(m[i][j]), "table": "m"},
                    {"i": i, "j": j, "value": best_k, "table": "s"},
                ],
            })

    return steps


if __name__ == "__main__":
    app.run(debug=True, port=5000)
