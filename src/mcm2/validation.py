"""Kiểm tra hợp lệ cho mảng kích thước của chuỗi ma trận.

Quy ước theo CLRS chương 15.2 (T. H. Cormen et al., Introduction to
Algorithms, 3rd ed., MIT Press, 2009): chuỗi gồm n ma trận A_1, ..., A_n;
ma trận thứ i có kích thước p[i-1] x p[i] với p là mảng 0-based gồm n+1
phần tử nguyên dương.

Thông điệp lỗi bằng tiếng Việt cho khớp ngữ cảnh môn học.
"""

from __future__ import annotations

from typing import Sequence


class DimensionError(ValueError):
    """Lỗi khi mảng kích thước không hợp lệ.

    Kế thừa ValueError để nơi gọi có thể bắt chung bằng ValueError nếu muốn,
    nhưng vẫn phân biệt được đây là lỗi dữ liệu kích thước.
    """


def validate_dimensions(dims: Sequence[object]) -> int:
    """Kiểm tra mảng kích thước và trả về số ma trận n.

    Thứ tự kiểm tra được chọn để tránh lỗi phụ: xét độ dài trước, rồi
    kiểu phần tử, cuối cùng mới xét dấu (so sánh <= 0 chỉ an toàn khi đã
    chắc chắn phần tử là số nguyên).

    Tham số:
        dims: mảng kích thước p. Kỳ vọng là dãy số nguyên dương, độ dài
            tối thiểu 2 (tương ứng n >= 1 ma trận).

    Trả về:
        n = len(dims) - 1, số ma trận trong chuỗi.

    Ném:
        DimensionError: nếu mảng quá ngắn, chứa phần tử không phải số
            nguyên, hoặc chứa phần tử <= 0.
    """
    # 1) Độ dài: cần ít nhất 2 mốc kích thước để tạo thành 1 ma trận.
    if len(dims) < 2:
        raise DimensionError(
            "Mảng kích thước cần tối thiểu 2 phần tử để mô tả ít nhất 1 ma trận"
        )

    # 2) Kiểu: chỉ chấp nhận int thật. Loại bool vì bool là lớp con của int
    #    trong Python (True/False sẽ lọt qua nếu chỉ dùng isinstance(x, int)).
    for index, value in enumerate(dims):
        if type(value) is not int:
            raise DimensionError(
                f"Phần tử tại vị trí {index} không phải số nguyên: {value!r}"
            )

    # 3) Dấu: mọi kích thước phải là số nguyên dương.
    for index, value in enumerate(dims):
        if value <= 0:
            raise DimensionError(
                f"Phần tử tại vị trí {index} phải là số nguyên dương, nhận {value}"
            )

    return len(dims) - 1
