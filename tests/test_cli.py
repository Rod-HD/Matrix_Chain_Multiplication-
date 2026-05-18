"""CLI smoke tests cho mcm.cli.main().

Kiểm tra:
- Happy path full mode (Req 5.2, 6.2, 9.1)
- Validation error trả exit code 1 (Req 1.2, 1.3)
- Mode none không in bảng nhưng vẫn in kết quả (Req 5.4)
"""

import sys
from io import StringIO

from mcm.cli import main


def test_cli_happy_path_full_mode(capsys):
    """Gọi main với p=[3,10,7,2] --mode=full, kiểm tra stdout chứa đủ thông tin."""
    ret = main(["3", "10", "7", "2", "--mode=full"])

    assert ret == 0

    captured = capsys.readouterr()
    stdout = captured.out

    # Req 9.1: nhãn tiếng Việt
    assert "Bảng m:" in stdout
    assert "Bảng s:" in stdout
    # Req 7.1: parenthesization đúng
    assert "(A1(A2A3))" in stdout
    # Req 6.2, 7.1: cost đúng
    assert "200" in stdout


def test_cli_validation_error_returns_1(capsys):
    """Gọi main với p=[0,1] — phần tử không dương, expect exit code 1."""
    ret = main(["0", "1"])

    assert ret == 1

    captured = capsys.readouterr()
    stderr = captured.err

    # Stderr bắt đầu bằng "Lỗi: " và chứa message tiếng Việt nguyên văn (Req 1.3)
    assert stderr.startswith("Lỗi: ")
    assert "Mọi phần tử của Dimension_Array phải là số nguyên dương" in stderr


def test_cli_mode_none(capsys):
    """Gọi main với --mode=none: không in bảng, nhưng vẫn in parens và cost."""
    ret = main(["3", "10", "7", "2", "--mode=none"])

    assert ret == 0

    captured = capsys.readouterr()
    stdout = captured.out

    # Mode NONE: không in bảng (Req 5.4)
    assert "Bảng m:" not in stdout
    assert "Bảng s:" not in stdout
    # Vẫn in kết quả (Req 5.7)
    assert "(A1(A2A3))" in stdout
    assert "200" in stdout
