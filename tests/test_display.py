"""Test cho module display và CLI."""

import re

from mcm2 import solve
from mcm2.display import format_cost_table, format_split_table, render_result
from mcm2 import cli


def test_cost_table_marks_unused_cells():
    """Ô dưới đường chéo của bảng chi phí hiển thị dấu '-'."""
    result = solve([3, 10, 7, 2])
    text = format_cost_table(result.cost, result.n)
    lines = text.splitlines()
    # Hàng dữ liệu thứ hai (i=2) phải bắt đầu có dấu '-' ở cột j=1.
    assert "-" in lines[2]


def test_split_table_uses_one_based_values():
    """Bảng vị trí cắt hiển thị giá trị theo chỉ số 1-based (CLRS)."""
    result = solve([10, 20, 50, 1, 100])
    text = format_split_table(result.split, result.n)
    assert "Bảng" not in text
    # Hàng dữ liệu đầu (i=1): cột j=1 là ô không dùng "-", cột j=2 phải là
    # split[1][2]. Với hai ma trận A1A2 chỉ có một cách cắt k=1 -> giá trị 1.
    first_data_row = text.splitlines()[1].split()
    assert first_data_row[1] == "-"          # ô (i=1, j=1) không dùng
    assert first_data_row[2] == str(result.split[1][2])


def test_columns_aligned():
    """Mọi dòng trong bảng có cùng số cột và độ rộng thống nhất."""
    result = solve([30, 35, 15, 5, 10, 20, 25])
    text = format_cost_table(result.cost, result.n)
    lines = text.splitlines()
    widths = {len(line) for line in lines}
    assert len(widths) == 1  # mọi dòng cùng độ rộng


def test_render_result_modes():
    """render_result tôn trọng các cờ show_cost / show_split."""
    result = solve([3, 10, 7, 2])
    full = render_result(result)
    assert "Bảng chi phí" in full
    assert "Bảng vị trí cắt" in full

    none = render_result(result, show_cost=False, show_split=False)
    assert "Bảng chi phí" not in none
    assert "Bảng vị trí cắt" not in none
    assert "Dấu ngoặc tối ưu" in none
    assert "Số phép nhân vô hướng tối thiểu" in none


def test_cost_is_plain_integer():
    """Dòng chi phí là số nguyên thuần, không có dấu phân cách nghìn."""
    result = solve([30, 35, 15, 5, 10, 20, 25])
    text = render_result(result)
    last = text.splitlines()[-1]
    assert re.fullmatch(r"Số phép nhân vô hướng tối thiểu: \d+", last)


def test_cli_happy_path(capsys):
    """CLI in đủ bảng và kết quả cho ví dụ hợp lệ."""
    code = cli.main(["3", "10", "7", "2"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Bảng chi phí" in out
    assert "(A1(A2A3))" in out
    assert "200" in out


def test_cli_tables_none(capsys):
    """--tables=none bỏ qua mọi bảng nhưng vẫn in kết quả."""
    code = cli.main(["3", "10", "7", "2", "--tables=none"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Bảng chi phí" not in out
    assert "Dấu ngoặc tối ưu" in out


def test_cli_invalid_input(capsys):
    """Dữ liệu sai cho mã thoát 1 và thông điệp lỗi ra stderr."""
    code = cli.main(["10", "0", "5"])
    err = capsys.readouterr().err
    assert code == 1
    assert "Lỗi dữ liệu" in err
