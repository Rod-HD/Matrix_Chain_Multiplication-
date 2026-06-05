"use strict";

// Trạng thái kết quả và bước đang xem.
let current = null;
let stepIndex = 0;

// Danh sách kích thước từng ma trận: mỗi phần tử {rows, cols}.
// Bất biến: matrices[i].cols === matrices[i+1].rows (số cột nối số hàng).
let matrices = [];

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  $("solve-btn").addEventListener("click", solve);
  $("add-matrix").addEventListener("click", () => {
    addMatrix();
    renderBuilder();
  });
  $("rm-matrix").addEventListener("click", () => {
    if (matrices.length > 1) {
      matrices.pop();
      renderBuilder();
    }
  });

  // Keyboard input: type the desired count and press Enter
  $("matrix-count-input").addEventListener("change", applyCountInput);
  $("matrix-count-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") applyCountInput();
  });
  $("apply-dims").addEventListener("click", applyRawDims);
  $("dims").addEventListener("keydown", (e) => {
    if (e.key === "Enter") applyRawDims();
  });

  document.querySelectorAll(".example").forEach((btn) => {
    btn.addEventListener("click", () => {
      loadDims(btn.dataset.dims.split(/[\s,]+/).map(Number));
      solve();
    });
  });

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab));
  });

  $("step-prev").addEventListener("click", () => moveStep(-1));
  $("step-next").addEventListener("click", () => moveStep(1));

  // Vẽ sơ đồ ví dụ cho phần giải thích (cố định theo ví dụ kinh điển).
  renderBraceDiagram([30, 35, 15, 5, 10, 20, 25]);

  // Khởi đầu với ví dụ kinh điển 6 ma trận.
  loadDims([30, 35, 15, 5, 10, 20, 25]);
});

// Vẽ sơ đồ "ngoặc" minh hoạ: mỗi ma trận Ai nằm dưới hai mốc kích thước liền kề.
function renderBraceDiagram(p) {
  const prefix = "p:  ";
  const gap = 3; // số khoảng trắng giữa hai con số

  // Dựng dòng số và ghi lại vị trí ký tự bắt đầu/kết thúc của mỗi số.
  let line = prefix;
  const start = [];
  const end = [];
  const numHtml = [prefix];
  for (let k = 0; k < p.length; k++) {
    if (k > 0) {
      line += " ".repeat(gap);
      numHtml.push(" ".repeat(gap));
    }
    start[k] = line.length;
    const s = String(p[k]);
    line += s;
    end[k] = line.length;
    numHtml.push(`<span class="bnum">${s}</span>`);
  }
  const lines = [numHtml.join("")];

  // Mỗi ma trận i (0-based) trải dưới số i và số i+1.
  const n = p.length - 1;
  for (let i = 0; i < n; i++) {
    const left = start[i];
    const right = end[i + 1] - 1;
    const span = right - left + 1;
    const label = "A" + (i + 1);
    const inner = span - 2; // chỗ giữa hai góc └ ┘
    let mid;
    if (inner <= label.length) {
      mid = `<span class="blabel">${label}</span>`;
    } else {
      const fill = inner - label.length;
      const lf = Math.floor(fill / 2);
      const rf = fill - lf;
      mid = "─".repeat(lf) + `<span class="blabel">${label}</span>` + "─".repeat(rf);
    }
    lines.push(" ".repeat(left) + "└" + mid + "┘");
  }
  $("brace-diagram").innerHTML = lines.join("\n");
}

// --- Quản lý danh sách ma trận ------------------------------------------------

function addMatrix() {
  if (matrices.length === 0) {
    matrices.push({ rows: 10, cols: 20 });
  } else {
    // Ma trận mới nối tiếp: số hàng = số cột của ma trận cuối hiện tại.
    const prev = matrices[matrices.length - 1];
    matrices.push({ rows: prev.cols, cols: 10 });
  }
}

// Nạp một mảng kích thước p vào danh sách ma trận.
function loadDims(p) {
  matrices = [];
  for (let i = 0; i + 1 < p.length; i++) {
    matrices.push({ rows: p[i], cols: p[i + 1] });
  }
  if (matrices.length === 0) matrices.push({ rows: 10, cols: 20 });
  renderBuilder();
}

// Dựng mảng kích thước p từ danh sách ma trận.
function buildP() {
  const p = [matrices[0].rows];
  for (const m of matrices) p.push(m.cols);
  return p;
}

// Khi sửa số cột của ma trận i, đồng bộ số hàng của ma trận i+1 (và ngược lại).
function setCols(i, value) {
  matrices[i].cols = value;
  if (i + 1 < matrices.length) matrices[i + 1].rows = value;
  renderBuilder();
}

function setRows(i, value) {
  matrices[i].rows = value;
  if (i - 1 >= 0) matrices[i - 1].cols = value;
  renderBuilder();
}

// --- Vẽ giao diện builder -----------------------------------------------------

function renderBuilder() {
  const list = $("matrix-list");
  list.innerHTML = "";

  matrices.forEach((m, i) => {
    const row = document.createElement("div");
    row.className = "matrix-row";

    // Ô số hàng: chỉ ma trận đầu cho sửa tự do; các ma trận sau bị khoá vì
    // số hàng phải bằng số cột ma trận trước (hiển thị nền xám).
    const rowsLocked = i > 0;
    row.innerHTML = `
      <span class="mname">A${i + 1}</span>
      <input class="dim ${rowsLocked ? "linked" : ""}" type="number" min="1"
             value="${m.rows}" data-role="rows" data-idx="${i}"
             ${rowsLocked ? "readonly title='Tự nối với số cột của A" + i + "'" : ""}>
      <span class="times">&times;</span>
      <input class="dim" type="number" min="1"
             value="${m.cols}" data-role="cols" data-idx="${i}">
    `;
    list.appendChild(row);
  });

  // Gắn sự kiện cho mọi ô nhập.
  list.querySelectorAll("input.dim").forEach((inp) => {
    inp.addEventListener("input", (e) => {
      const idx = Number(e.target.dataset.idx);
      const val = Math.max(1, Number(e.target.value) || 1);
      if (e.target.dataset.role === "cols") setCols(idx, val);
      else setRows(idx, val);
    });
  });

  $("matrix-count").textContent = `${matrices.length} ma trận`;
  $("matrix-count-input").value = matrices.length;
  $("rm-matrix").disabled = matrices.length <= 1;

  // Cập nhật phần xem trước.
  const p = buildP();
  $("chain-preview").textContent = matrices
    .map((m, i) => `A${i + 1}(${m.rows}×${m.cols})`)
    .join(" · ");
  $("p-preview").textContent = "[" + p.join(", ") + "]";
  $("dims").value = p.join(" ");
}

// Apply count from the keyboard number input
function applyCountInput() {
  const el = $("matrix-count-input");
  let target = Math.max(1, Math.min(20, parseInt(el.value) || 1));
  el.value = target;
  // Add or remove matrices to reach target count
  while (matrices.length < target) addMatrix();
  while (matrices.length > target) matrices.pop();
  renderBuilder();
}
function applyRawDims() {
  const raw = $("dims").value.trim();
  const p = raw
    .split(/[\s,]+/)
    .filter((t) => t.length > 0)
    .map((t) => Number(t));
  if (p.length < 2 || p.some((x) => !Number.isFinite(x) || x <= 0)) {
    showError("Mảng kích thước phải gồm ít nhất 2 số nguyên dương");
    return;
  }
  hideError();
  loadDims(p);
}

// --- Gọi máy chủ giải ---------------------------------------------------------

async function solve() {
  const dims = buildP();
  hideError();
  try {
    const res = await fetch("/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dims }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || "Có lỗi xảy ra");
      return;
    }
    current = data;
    stepIndex = 0;
    render();
  } catch (err) {
    showError("Không gọi được máy chủ: " + err.message);
  }
}

function render() {
  $("summary").classList.remove("hidden");
  $("tabs").classList.remove("hidden");

  $("sum-n").textContent = current.n;
  $("sum-cost").textContent = current.min_cost.toLocaleString("vi-VN");
  $("sum-catalan").textContent = current.num_parenthesizations.toLocaleString("vi-VN");
  $("sum-parens").textContent = current.parenthesization;

  renderTables();
  renderStep();
  renderTree();
  switchTab("tables");
}

function renderTables() {
  $("cost-table").innerHTML = buildTable(current.cost_table, true);
  $("split-table").innerHTML = buildTable(current.split_table, false);
}

function buildTable(grid, isCost) {
  const n = current.n;
  let html = "<table><thead><tr><th></th>";
  for (let j = 0; j < n; j++) html += `<th>A${j + 1}</th>`;
  html += "</tr></thead><tbody>";
  for (let i = 0; i < n; i++) {
    html += `<tr><th>A${i + 1}</th>`;
    for (let j = 0; j < n; j++) {
      const v = grid[i][j];
      if (v === null) {
        html += `<td class="unused">-</td>`;
      } else if (isCost && i === 0 && j === n - 1) {
        html += `<td class="optimal">${v}</td>`;
      } else {
        html += `<td data-i="${i}" data-j="${j}">${v}</td>`;
      }
    }
    html += "</tr>";
  }
  html += "</tbody></table>";
  return html;
}

function renderStep() {
  const steps = current.steps;
  if (steps.length === 0) {
    $("step-counter").textContent = "Không có bước nào (chỉ 1 ma trận)";
    $("step-detail").innerHTML = "";
    return;
  }
  const s = steps[stepIndex];
  $("step-counter").textContent = `Bước ${stepIndex + 1}/${steps.length}`;

  let html = `<div class="step-title">Tính đoạn A${s.i}..A${s.j} (độ dài ${s.length})</div>`;
  s.candidates.forEach((c) => {
    const best = c.k === s.best_k ? " best" : "";
    html += `<div class="candidate${best}">k = ${c.k}: ${c.formula}</div>`;
  });
  html += `<p>Chọn k = <strong>${s.best_k}</strong>, chi phí tối thiểu của đoạn = <strong>${s.best_cost}</strong>.</p>`;
  $("step-detail").innerHTML = html;

  document.querySelectorAll("#cost-table td").forEach((td) => td.classList.remove("highlight"));
  const cell = document.querySelector(`#cost-table td[data-i="${s.i - 1}"][data-j="${s.j - 1}"]`);
  if (cell) cell.classList.add("highlight");
}

function moveStep(delta) {
  if (!current || current.steps.length === 0) return;
  stepIndex = Math.max(0, Math.min(current.steps.length - 1, stepIndex + delta));
  renderStep();
  switchTab("steps");
}

// ─── SVG Tree + Trace ────────────────────────────────────────────────────────

function renderTree() {
  if (!current) return;
  const split = current.split_table; // 0-indexed array, values 1-based
  const dims  = current.dims;
  const n     = current.n;

  // 1) Build logical tree nodes (BFS layout)
  // Each node: { i, j, k, left, right, depth, x, y }
  function buildTree(i, j) {
    if (i === j) return { i, j, leaf: true };
    const k = split[i - 1][j - 1]; // split_table rows/cols are 0-indexed
    return { i, j, k, leaf: false,
             left: buildTree(i, k), right: buildTree(k + 1, j) };
  }
  const root = buildTree(1, n);

  // 2) Assign layout positions (in-order x, depth y)
  const NODE_W = 80, NODE_H = 48, GAP_X = 12, GAP_Y = 56;
  let xCursor = 0;

  function layout(node, depth) {
    node.depth = depth;
    if (node.leaf) {
      node.cx = xCursor * (NODE_W + GAP_X) + NODE_W / 2;
      xCursor++;
    } else {
      layout(node.left, depth + 1);
      const leftCx = node.left.cx;
      layout(node.right, depth + 1);
      const rightCx = node.right.cx;
      node.cx = (leftCx + rightCx) / 2;
    }
    node.cy = depth * (NODE_H + GAP_Y) + NODE_H / 2;
  }
  layout(root, 0);

  const svgW = xCursor * (NODE_W + GAP_X) + 40;
  const svgH = (getDepth(root) + 1) * (NODE_H + GAP_Y) + 20;

  function getDepth(node) {
    if (node.leaf) return 0;
    return 1 + Math.max(getDepth(node.left), getDepth(node.right));
  }

  // 3) Render SVG
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("width", svgW);
  svg.setAttribute("height", svgH);
  svg.setAttribute("viewBox", `0 0 ${svgW} ${svgH}`);

  const LEAF_BG = "#86efac", LEAF_FG = "#052e16";
  const INNER_BG = "#f59e0b", INNER_FG = "#1a0a00";
  const LINE_COLOR = "#94a3b8";

  function drawNode(node) {
    const x = node.cx - NODE_W / 2;
    const y = node.cy - NODE_H / 2;

    // Edge to children
    if (!node.leaf) {
      for (const child of [node.left, node.right]) {
        const line = document.createElementNS(NS, "line");
        line.setAttribute("x1", node.cx); line.setAttribute("y1", node.cy + NODE_H / 2);
        line.setAttribute("x2", child.cx); line.setAttribute("y2", child.cy - NODE_H / 2);
        line.setAttribute("stroke", LINE_COLOR);
        line.setAttribute("stroke-width", "1.5");
        svg.appendChild(line);
      }
    }

    // Node box
    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("x", x); rect.setAttribute("y", y);
    rect.setAttribute("width", NODE_W); rect.setAttribute("height", NODE_H);
    rect.setAttribute("rx", "8");
    rect.setAttribute("fill", node.leaf ? LEAF_BG : INNER_BG);
    svg.appendChild(rect);

    // Text line 1
    const t1 = document.createElementNS(NS, "text");
    t1.setAttribute("x", node.cx);
    t1.setAttribute("y", node.leaf ? node.cy + 5 : node.cy - 4);
    t1.setAttribute("text-anchor", "middle");
    t1.setAttribute("font-family", "Consolas, monospace");
    t1.setAttribute("font-size", "13");
    t1.setAttribute("font-weight", "700");
    t1.setAttribute("fill", node.leaf ? LEAF_FG : INNER_FG);
    t1.textContent = node.leaf ? `A${node.i}` : `k=${node.k}`;
    svg.appendChild(t1);

    // Text line 2 (range) for inner nodes
    if (!node.leaf) {
      const t2 = document.createElementNS(NS, "text");
      t2.setAttribute("x", node.cx);
      t2.setAttribute("y", node.cy + 11);
      t2.setAttribute("text-anchor", "middle");
      t2.setAttribute("font-family", "Consolas, monospace");
      t2.setAttribute("font-size", "10");
      t2.setAttribute("fill", INNER_FG);
      t2.textContent = `A${node.i}..A${node.j}`;
      svg.appendChild(t2);
    }

    if (!node.leaf) { drawNode(node.left); drawNode(node.right); }
  }
  drawNode(root);
  $("tree-svg-wrap").innerHTML = "";
  $("tree-svg-wrap").appendChild(svg);

  // 4) Trace
  function traceLines(node, indent) {
    const pad = "  ".repeat(indent);
    if (node.leaf) {
      const dimStr = `${dims[node.i - 1]}×${dims[node.i]}`;
      return [`${pad}<span class="trace-leaf">A${node.i} (${dimStr})</span>`];
    }
    const lines = [];
    lines.push(`${pad}<span class="trace-split">split(${node.i},${node.j}) tại k=${node.k}:</span>`);
    lines.push(`${pad}  Trái: A${node.i}..A${node.k}`);
    lines.push(...traceLines(node.left, indent + 2));
    lines.push(`${pad}  Phải: A${node.k + 1}..A${node.j}`);
    lines.push(...traceLines(node.right, indent + 2));
    return lines;
  }
  $("tree-trace").innerHTML = traceLines(root, 0).join("\n");
}

function switchTab(name) {
  document.querySelectorAll(".tab").forEach((t) =>
    t.classList.toggle("active", t.dataset.tab === name)
  );
  $("tab-tables").classList.toggle("hidden", name !== "tables");
  $("tab-steps").classList.toggle("hidden", name !== "steps");
  $("tab-tree").classList.toggle("hidden", name !== "tree");
}

function showError(msg) {
  const el = $("error");
  el.textContent = msg;
  el.classList.remove("hidden");
  $("summary").classList.add("hidden");
  $("tabs").classList.add("hidden");
  document.querySelectorAll(".tab-content").forEach((c) => c.classList.add("hidden"));
}

function hideError() {
  $("error").classList.add("hidden");
}
