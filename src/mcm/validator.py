"""Module validator: xác thực Dimension_Array p theo Requirement 1.

Triển khai bám đúng phần "Components and Interfaces / validator" trong
design.md. Thông điệp lỗi được giữ nguyên văn theo Req 1.2/1.3/1.4 để
khớp với tài liệu môn học (giảng viên có thể chấm wording).
"""

from __future__ import annotations


def validate_dimension_array(p) -> int:
    """Xác thực Dimension_Array ``p`` và trả về Matrix_Chain_Length ``n``.

    Thứ tự kiểm tra (theo design.md):
        1. ``len(p) < 2``           → Req 1.2.
        2. Tồn tại phần tử có ``type(x) is not int`` (loại trừ ``bool``
           vì ``bool`` là subclass của ``int`` trong Python) → Req 1.4.
        3. Tồn tại phần tử ``x <= 0`` → Req 1.3.

    Kiểu được kiểm tra trước giá trị để tránh ``TypeError`` khi so sánh
    ``<= 0`` với phần tử không phải số (ví dụ chuỗi).

    Args:
        p: mảng kích thước; kỳ vọng là ``list`` các số nguyên dương với
            ``len(p) >= 2``.

    Returns:
        ``n = len(p) - 1`` — Matrix_Chain_Length theo Req 1.5.

    Raises:
        ValueError: với thông điệp tiếng Việt nguyên văn theo
            Req 1.2/1.3/1.4.
    """
    # 1) Kiểm tra độ dài tối thiểu (Req 1.2).
    if len(p) < 2:
        raise ValueError(
            "Dimension_Array phải có ít nhất 2 phần tử "
            "(tương ứng n ≥ 1 ma trận)"
        )

    # 2) Kiểm tra kiểu trước giá trị (Req 1.4).
    #    `type(x) is int` loại trừ `bool` (vì `type(True) is bool`),
    #    đồng thời loại `float`, `str`, ...
    for x in p:
        if type(x) is not int:
            raise ValueError(
                "Mọi phần tử của Dimension_Array phải là số nguyên"
            )

    # 3) Kiểm tra giá trị dương (Req 1.3).
    for x in p:
        if x <= 0:
            raise ValueError(
                "Mọi phần tử của Dimension_Array phải là số nguyên dương"
            )

    # 4) Mọi điều kiện hợp lệ → trả về Matrix_Chain_Length (Req 1.5).
    return len(p) - 1
