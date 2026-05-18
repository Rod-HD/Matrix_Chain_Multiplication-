"""Flask web UI cho Matrix Chain Multiplication."""

import sys
from pathlib import Path

# Đảm bảo import được package mcm từ src/
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root / "src"))

from flask import Flask, render_template, request, jsonify
from mcm import MCMSolver

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/solve", methods=["POST"])
def solve():
    data = request.get_json()
    dims = data.get("dims", [])
    try:
        solver = MCMSolver(dims)
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400

    # Build steps data for visualization
    n = solver.n
    steps = []
    for length in range(2, n + 1):
        step_cells = []
        for i in range(1, n - length + 2):
            j = i + length - 1
            step_cells.append({
                "i": i, "j": j,
                "cost": solver.m[i][j],
                "k": solver.s[i][j]
            })
        steps.append({"length": length, "cells": step_cells})

    # Build m and s tables as 2D arrays (1-based, skip index 0)
    m_table = [[solver.m[i][j] for j in range(1, n + 1)] for i in range(1, n + 1)]
    s_table = [[solver.s[i][j] for j in range(1, n + 1)] for i in range(1, n + 1)]

    # Build recursive trace for parenthesization
    trace_lines = []
    _build_trace(solver.s, solver.p, 1, n, 0, trace_lines)

    return jsonify({
        "n": n,
        "p": solver.p,
        "cost": solver.cost,
        "parens": solver.parens,
        "m_table": m_table,
        "s_table": s_table,
        "steps": steps,
        "trace": trace_lines,
    })


def _build_trace(s, p, i, j, depth, lines):
    """Build recursive trace of PRINT-OPTIMAL-PARENS as indented lines."""
    if i == j:
        lines.append({
            "depth": depth,
            "text": f"A{i} ({p[i-1]}×{p[i]})"
        })
    else:
        k = s[i][j]
        cost = p[i - 1] * p[k] * p[j]
        lines.append({
            "depth": depth,
            "text": f"Tách A{i}..A{j} tại k={k}, chi phí nhân = {p[i-1]}×{p[k]}×{p[j]} = {cost}"
        })
        _build_trace(s, p, i, k, depth + 1, lines)
        _build_trace(s, p, k + 1, j, depth + 1, lines)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
