"""Test cho module ``mcm.formatter``.

Task 8.2 — Golden output test cho :func:`format_table`:
- So sánh nguyên văn output của ``format_table(m, "Bảng m:", 3, kind="m")``
  và ``format_table(s, "Bảng s:", 3, kind="s")`` cho ``p = [3, 10, 7, 2]``
  với block mẫu trong "Mẫu output" của ``design.md``.

Validates: Requirements 5.2, 5.5, 5.6
"""

import pytest

from mcm.formatter import DisplayMode, format_table, format_trace
from mcm.solver import matrix_chain_order


# Block mẫu nguyên văn theo "Mẫu output" trong design.md cho p = [3, 10, 7, 2].
EXPECTED_M_TABLE = (
    "Bảng m:\n"
    "        j=1   j=2   j=3\n"
    "  i=1     0   210   200\n"
    "  i=2     -     0   140\n"
    "  i=3     -     -     0"
)

EXPECTED_S_TABLE = (
    "Bảng s:\n"
    "        j=2   j=3\n"
    "  i=1     1     1\n"
    "  i=2     -     2"
)


def test_format_table_m_golden_output():
    """``format_table(m, "Bảng m:", 3, kind="m")`` khớp nguyên văn block mẫu.

    Kiểm tra:
    - Tiêu đề ``j=k`` cho ``k = 1..n`` (Req 5.2).
    - Ô không dùng (``i > j``) hiển thị ``"-"`` (Req 5.5).
    - Các cột canh lề phải đồng đều (Req 5.6).
    """
    p = [3, 10, 7, 2]
    m, _ = matrix_chain_order(p)

    actual = format_table(m, "Bảng m:", 3, kind="m")

    assert actual == EXPECTED_M_TABLE


def test_format_table_s_golden_output():
    """``format_table(s, "Bảng s:", 3, kind="s")`` khớp nguyên văn block mẫu.

    Kiểm tra:
    - Tiêu đề chỉ có ``j=2..n`` (s_table không có cột ``j=1``) (Req 5.2).
    - Ô không dùng (``i >= j``) hiển thị ``"-"`` (Req 5.5).
    - Các cột canh lề phải đồng đều (Req 5.6).
    """
    p = [3, 10, 7, 2]
    _, s = matrix_chain_order(p)

    actual = format_table(s, "Bảng s:", 3, kind="s")

    assert actual == EXPECTED_S_TABLE


# ---------------------------------------------------------------------------
# Task 8.3 — Property test 8: Ô không sử dụng được hiển thị "-"
# ---------------------------------------------------------------------------

import random

from mcm.formatter import format_table as _format_table  # alias để rõ ý dùng lại


def test_property_8_unused_cells_display_dash():
    """Property 8: Ô không sử dụng được hiển thị ``"-"``.

    **Validates: Requirements 5.5**

    Cho cả ``kind="m"`` (ô ``i > j``) và ``kind="s"`` (ô ``i >= j``):
    sinh ngẫu nhiên ``Dimension_Array`` hợp lệ, render bảng bằng
    :func:`format_table`, parse ngược các dòng dữ liệu rồi assert
    token tương ứng tại các vị trí "không sử dụng" đúng bằng ``"-"``.

    PBT framework: chỉ dùng ``random.Random(seed)`` (Req 8.3 — không
    được dùng ``hypothesis``). Seed = ``20251128 + 8`` (offset 8 cho
    Property 8). Phạm vi: ``n_max = 8``, mỗi phần tử của ``p`` ∈ [1, 50],
    100 iteration.
    """
    rng = random.Random(20251128 + 8)
    n_max = 8
    iterations = 100

    for iteration in range(iterations):
        # Sinh n ∈ [1, n_max] và p độ dài n+1 với mỗi phần tử ∈ [1, 50].
        n = rng.randint(1, n_max)
        p = [rng.randint(1, 50) for _ in range(n + 1)]
        m, s = matrix_chain_order(p)

        # ---- kind="m" --------------------------------------------------
        # Bảng m có n hàng dữ liệu (i = 1..n) và n cột (j = 1..n).
        # Ô không sử dụng: i > j.
        m_output = _format_table(m, "Bảng m:", n, kind="m")
        m_lines = m_output.split("\n")
        for i in range(1, n + 1):
            # Dòng 0 là nhãn "Bảng m:", dòng 1 là header "j=k", dữ liệu bắt
            # đầu từ dòng 2 — tức row index i ứng với line i + 1.
            tokens = m_lines[i + 1].split()
            # Token đầu là nhãn hàng "i=k", n token sau là các ô j = 1..n.
            assert tokens[0] == f"i={i}", (
                f"Iter {iteration}, p={p}, kind=m: row label mismatch "
                f"at line {i + 1} — got {tokens[0]!r}"
            )
            assert len(tokens) == 1 + n, (
                f"Iter {iteration}, p={p}, kind=m: hàng i={i} có "
                f"{len(tokens) - 1} ô, kỳ vọng {n}"
            )
            for j in range(1, n + 1):
                cell = tokens[j]
                if i > j:
                    assert cell == "-", (
                        f"Iter {iteration}, p={p}, kind=m: ô không sử dụng "
                        f"tại (i={i}, j={j}) phải là '-', nhận được {cell!r}"
                    )

        # ---- kind="s" --------------------------------------------------
        # Bảng s có n-1 hàng dữ liệu (i = 1..n-1) và n-1 cột (j = 2..n).
        # Ô không sử dụng: i >= j.
        # Khi n = 1, s không có hàng dữ liệu nào — vòng lặp dưới rỗng,
        # property đúng vacuously.
        s_output = _format_table(s, "Bảng s:", n, kind="s")
        s_lines = s_output.split("\n")
        for i in range(1, n):  # i = 1..n-1
            tokens = s_lines[i + 1].split()
            assert tokens[0] == f"i={i}", (
                f"Iter {iteration}, p={p}, kind=s: row label mismatch "
                f"at line {i + 1} — got {tokens[0]!r}"
            )
            assert len(tokens) == 1 + (n - 1), (
                f"Iter {iteration}, p={p}, kind=s: hàng i={i} có "
                f"{len(tokens) - 1} ô, kỳ vọng {n - 1}"
            )
            # Cột j chạy từ 2..n; vị trí token tương ứng là (j - 1).
            for offset, j in enumerate(range(2, n + 1), start=1):
                cell = tokens[offset]
                if i >= j:
                    assert cell == "-", (
                        f"Iter {iteration}, p={p}, kind=s: ô không sử dụng "
                        f"tại (i={i}, j={j}) phải là '-', nhận được {cell!r}"
                    )


# ---------------------------------------------------------------------------
# Task 8.4 — Property test 9: Format bảng canh lề nhất quán
# ---------------------------------------------------------------------------


def test_property_9_column_alignment_consistent():
    """Property 9: Format bảng canh lề nhất quán.

    **Validates: Requirements 5.6**

    Với ``format_table(...)``: mọi dòng nội dung (header + data rows) có
    cùng số token (split theo whitespace) và mỗi cột có cùng độ rộng
    (tức right-aligned nhất quán).

    PBT framework: ``random.Random(seed)`` cố định (Req 8.3). Seed =
    ``20251128 + 9 = 20251137`` (offset 9 cho Property 9). Phạm vi:
    ``n`` ∈ [1, 8] (len(p) ∈ [2, 9]), mỗi phần tử ∈ [1, 50], 100 iteration.
    """
    rng = random.Random(20251137)
    iterations = 100

    for iteration in range(iterations):
        # Sinh Dimension_Array hợp lệ: len(p) ∈ [2, 9] → n ∈ [1, 8].
        n = rng.randint(1, 8)
        p = [rng.randint(1, 50) for _ in range(n + 1)]
        m, s = matrix_chain_order(p)

        for kind in ("m", "s"):
            table = m if kind == "m" else s
            label = "Bảng m:" if kind == "m" else "Bảng s:"
            output = format_table(table, label, n, kind=kind)
            all_lines = output.split("\n")

            # Dòng đầu là nhãn (label line) — bỏ qua.
            # Dòng tiếp theo là header (j=k), sau đó là data rows (i=k ...).
            content_lines = all_lines[1:]

            # Nếu không có dòng nội dung, bỏ qua.
            if not content_lines:
                continue

            # Header line có ô đầu tiên rỗng (placeholder cho cột nhãn
            # hàng), nên khi split() sẽ ít hơn data rows 1 token. Ta chỉ
            # kiểm tra các data rows (từ dòng thứ 2 trong content_lines).
            header_line = content_lines[0]
            data_lines = content_lines[1:]

            # --- Kiểm tra 1: Mọi dòng dữ liệu có cùng số token ---
            if data_lines:
                token_counts = [len(line.split()) for line in data_lines]
                expected_count = token_counts[0]
                for line_idx, count in enumerate(token_counts):
                    assert count == expected_count, (
                        f"Iter {iteration}, p={p}, kind={kind!r}: "
                        f"data dòng {line_idx} có {count} token, "
                        f"kỳ vọng {expected_count}.\n"
                        f"Dòng: {data_lines[line_idx]!r}"
                    )

                # Header phải có đúng (expected_count - 1) token (vì ô đầu
                # rỗng bị split() bỏ qua).
                header_token_count = len(header_line.split())
                assert header_token_count == expected_count - 1, (
                    f"Iter {iteration}, p={p}, kind={kind!r}: "
                    f"header có {header_token_count} token, "
                    f"kỳ vọng {expected_count - 1}.\n"
                    f"Header: {header_line!r}"
                )

            # --- Kiểm tra 2: Mỗi cột có cùng độ rộng ký tự ---
            # format_table dùng rjust(width) + " ".join cho mọi dòng
            # (header và data). Vì mỗi ô cùng width và cùng số cột,
            # tất cả content_lines phải có cùng độ dài ký tự.
            line_lengths = [len(line) for line in content_lines]
            expected_length = line_lengths[0]
            for line_idx, length in enumerate(line_lengths):
                assert length == expected_length, (
                    f"Iter {iteration}, p={p}, kind={kind!r}: "
                    f"dòng {line_idx} dài {length} ký tự, "
                    f"kỳ vọng {expected_length}.\n"
                    f"Dòng: {content_lines[line_idx]!r}"
                )


# ---------------------------------------------------------------------------
# Task 9.2 — Test cho 4 tổ hợp Display_Mode
# ---------------------------------------------------------------------------


class TestFormatTraceDisplayModes:
    """Test ``format_trace`` với 4 tổ hợp ``DisplayMode`` trên ``p=[3,10,7,2]``.

    Validates: Requirements 5.2, 5.3, 5.4, 5.7, 5.8, 9.1
    """

    @pytest.fixture()
    def mcm_data(self):
        """Tính m, s cho p=[3,10,7,2] dùng chung cho các test."""
        p = [3, 10, 7, 2]
        m, s = matrix_chain_order(p)
        return p, m, s

    def test_full_tables_contains_all_four_labels(self, mcm_data):
        """FULL_TABLES: output chứa đủ 4 nhãn tiếng Việt.

        Validates: Requirements 5.2, 9.1
        """
        p, m, s = mcm_data
        output = format_trace(p, m, s, DisplayMode.FULL_TABLES)

        assert "Bảng m:" in output
        assert "Bảng s:" in output
        assert "Cách đóng mở ngoặc tối ưu:" in output
        assert "Số phép nhân vô hướng tối thiểu:" in output

    def test_partial_tables_choice_m_only_m_table(self, mcm_data):
        """PARTIAL_TABLES với partial_choice="m": chỉ có "Bảng m:", không có "Bảng s:".

        Validates: Requirements 5.3, 5.8
        """
        p, m, s = mcm_data
        output = format_trace(
            p, m, s, DisplayMode.PARTIAL_TABLES, partial_choice="m"
        )

        assert "Bảng m:" in output
        assert "Bảng s:" not in output
        assert "Cách đóng mở ngoặc tối ưu:" in output
        assert "Số phép nhân vô hướng tối thiểu:" in output

    def test_partial_tables_choice_s_only_s_table(self, mcm_data):
        """PARTIAL_TABLES với partial_choice="s": chỉ có "Bảng s:", không có "Bảng m:".

        Validates: Requirements 5.3, 5.8
        """
        p, m, s = mcm_data
        output = format_trace(
            p, m, s, DisplayMode.PARTIAL_TABLES, partial_choice="s"
        )

        assert "Bảng s:" in output
        assert "Bảng m:" not in output
        assert "Cách đóng mở ngoặc tối ưu:" in output
        assert "Số phép nhân vô hướng tối thiểu:" in output

    def test_none_no_tables_but_has_final_labels(self, mcm_data):
        """NONE: không có "Bảng m:" và "Bảng s:" nhưng có 2 nhãn cuối.

        Validates: Requirements 5.4, 5.7
        """
        p, m, s = mcm_data
        output = format_trace(p, m, s, DisplayMode.NONE)

        assert "Bảng m:" not in output
        assert "Bảng s:" not in output
        assert "Cách đóng mở ngoặc tối ưu:" in output
        assert "Số phép nhân vô hướng tối thiểu:" in output

    def test_partial_tables_missing_choice_raises_valueerror(self, mcm_data):
        """PARTIAL_TABLES với partial_choice=None: raise ValueError chứa "partial_choice".

        Validates: Requirements 5.3
        """
        p, m, s = mcm_data

        with pytest.raises(ValueError, match="partial_choice"):
            format_trace(p, m, s, DisplayMode.PARTIAL_TABLES, partial_choice=None)


# ---------------------------------------------------------------------------
# Task 9.3 — Property test 10: Trace_Output FULL_TABLES chứa đủ 4 nhãn
# ---------------------------------------------------------------------------


def test_property_10_full_tables_contains_all_four_labels():
    """Property 10: Trace_Output FULL_TABLES chứa đủ 4 nhãn.

    **Validates: Requirements 9.1**

    Với mọi ``Dimension_Array`` hợp lệ, khi gọi
    ``format_trace(p, m, s, DisplayMode.FULL_TABLES)``, output phải chứa
    nguyên văn cả 4 nhãn tiếng Việt:
    - "Bảng m:"
    - "Bảng s:"
    - "Cách đóng mở ngoặc tối ưu:"
    - "Số phép nhân vô hướng tối thiểu:"

    PBT framework: ``random.Random(seed)`` cố định (Req 8.3 — không dùng
    ``hypothesis``). Seed = ``20251128 + 10 = 20251138`` (offset 10 cho
    Property 10). Phạm vi: ``len(p)`` ∈ [2, 9] (tức ``n`` ∈ [1, 8]),
    mỗi phần tử ∈ [1, 50], 100 iteration.
    """
    rng = random.Random(20251138)
    iterations = 100

    for iteration in range(iterations):
        # Sinh Dimension_Array hợp lệ: len(p) ∈ [2, 9] → n ∈ [1, 8].
        n = rng.randint(1, 8)
        p = [rng.randint(1, 50) for _ in range(n + 1)]
        m, s = matrix_chain_order(p)

        output = format_trace(p, m, s, DisplayMode.FULL_TABLES)

        assert "Bảng m:" in output, (
            f"Iter {iteration}, p={p}: output thiếu nhãn 'Bảng m:'"
        )
        assert "Bảng s:" in output, (
            f"Iter {iteration}, p={p}: output thiếu nhãn 'Bảng s:'"
        )
        assert "Cách đóng mở ngoặc tối ưu:" in output, (
            f"Iter {iteration}, p={p}: output thiếu nhãn "
            f"'Cách đóng mở ngoặc tối ưu:'"
        )
        assert "Số phép nhân vô hướng tối thiểu:" in output, (
            f"Iter {iteration}, p={p}: output thiếu nhãn "
            f"'Số phép nhân vô hướng tối thiểu:'"
        )


# ---------------------------------------------------------------------------
# Task 9.4 — Property test 11: cost in dạng số nguyên thuần
# ---------------------------------------------------------------------------

import re


def test_property_11_cost_pure_integer_format():
    """Property 11: cost in dạng số nguyên thuần.

    **Validates: Requirements 9.3**

    Với mọi ``Dimension_Array`` hợp lệ, dòng cuối của output từ
    ``format_trace(p, m, s, DisplayMode.FULL_TABLES)`` phải khớp regex
    ``^Số phép nhân vô hướng tối thiểu: \\d+$`` — tức cost là số nguyên
    thập phân thuần, không có dấu phân cách hàng nghìn hay ký tự khác.

    PBT framework: ``random.Random(seed)`` cố định (Req 8.3 — không dùng
    ``hypothesis``). Seed = ``20251128 + 11 = 20251139`` (offset 11 cho
    Property 11). Phạm vi: ``len(p)`` ∈ [2, 9] (tức ``n`` ∈ [1, 8]),
    mỗi phần tử ∈ [1, 50], 100 iteration.
    """
    rng = random.Random(20251139)
    iterations = 100
    cost_pattern = re.compile(r"^Số phép nhân vô hướng tối thiểu: \d+$")

    for iteration in range(iterations):
        # Sinh Dimension_Array hợp lệ: len(p) ∈ [2, 9] → n ∈ [1, 8].
        n = rng.randint(1, 8)
        p = [rng.randint(1, 50) for _ in range(n + 1)]
        m, s = matrix_chain_order(p)

        output = format_trace(p, m, s, DisplayMode.FULL_TABLES)
        last_line = output.split("\n")[-1]

        assert cost_pattern.match(last_line), (
            f"Iter {iteration}, p={p}: dòng cuối không khớp regex "
            f"'^Số phép nhân vô hướng tối thiểu: \\d+$'.\n"
            f"Dòng cuối thực tế: {last_line!r}"
        )
