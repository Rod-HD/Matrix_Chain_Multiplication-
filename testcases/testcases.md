# Bộ testcase - Matrix Chain Multiplication

Bộ testcase tường minh gồm **16 ca**: 12 ca input hợp lệ và 4 ca input sai.
Chạy tất cả: `python testcases/run_testcases.py`

---

## Nhóm 1 - Input hợp lệ (12 ca)

Mỗi ca kiểm tra cả hai: **chi phí tối thiểu** (`expected_cost`) và **dấu ngoặc tối ưu** (`expected_parens`).

> Mọi `expected_cost` được đối chiếu độc lập bằng `naive_min_cost` (liệt kê
> toàn bộ cách đặt ngoặc) nên đây là đáp án tối ưu thật, không phải tự đặt.

| ID  | Mô tả | Mảng kích thước p | n | Chi phí tối thiểu | Dấu ngoặc tối ưu |
|-----|-------|-------------------|---|-------------------|------------------|
| V01 | Ba ma trận, ví dụ cơ bản | `[3, 10, 7, 2]` | 3 | 200 | `(A1(A2A3))` |
| V02 | Bốn ma trận, tách phải rồi gộp trái | `[10, 20, 50, 1, 100]` | 4 | 2200 | `((A1(A2A3))A4)` |
| V03 | Sáu ma trận, ví dụ kinh điển | `[30, 35, 15, 5, 10, 20, 25]` | 6 | 15125 | `((A1(A2A3))((A4A5)A6))` |
| V04 | Biên: một ma trận, không có phép nhân nào | `[5, 7]` | 1 | 0 | `A1` |
| V05 | Hai ma trận, chỉ một cách nhân duy nhất | `[10, 30, 5]` | 2 | 1500 | `(A1A2)` |
| V06 | Ba ma trận, thứ tự ngoặc đổi chi phí gấp 10 lần | `[10, 100, 5, 50]` | 3 | 7500 | `((A1A2)A3)` |
| V07 | Kích thước tăng dần, dồn ngoặc về trái | `[1, 2, 3, 4, 5]` | 4 | 38 | `(((A1A2)A3)A4)` |
| V08 | Kích thước giảm dần, dồn ngoặc về phải | `[5, 4, 3, 2, 1]` | 4 | 38 | `(A1(A2(A3A4)))` |
| V09 | Mọi kích thước bằng nhau, nhiều lời giải cùng chi phí | `[2, 2, 2, 2, 2]` | 4 | 24 | `(A1(A2(A3A4)))` |
| V10 | Kích thước dao động mạnh, ép tách ở giữa | `[100, 1, 100, 1, 100]` | 4 | 10200 | `(A1((A2A3)A4))` |
| V11 | Bảy ma trận, kích thước hỗn hợp không quy luật | `[4, 10, 3, 12, 20, 7, 5, 8]` | 7 | 1581 | `((A1A2)((((A3A4)A5)A6)A7))` |
| V12 | Số nguyên tố không cấu trúc đặc biệt | `[13, 5, 89, 3, 34]` | 4 | 2856 | `((A1(A2A3))A4)` |

### Ghi chú một số ca đáng chú ý

**V03** - ví dụ kinh điển 6 ma trận:
- `A1 = 30×35`, `A2 = 35×15`, `A3 = 15×5`, `A4 = 5×10`, `A5 = 10×20`, `A6 = 20×25`
- Cách tối ưu: `((A1(A2A3))((A4A5)A6))` = 15125 phép nhân

**V06** - minh họa tầm quan trọng của thứ tự đặt ngoặc:
- `((A1A2)A3)`: 10·100·5 + 10·5·50 = 5000 + 2500 = **7500**
- `(A1(A2A3))`: 100·5·50 + 10·100·50 = 25000 + 50000 = **75000** (gấp 10 lần)

**V07 vs V08** - cùng chi phí 38 nhưng cấu trúc đối xứng:
- Kích thước tăng → ngoặc trái: `(((A1A2)A3)A4)`
- Kích thước giảm → ngoặc phải: `(A1(A2(A3A4)))`

**V09** - mọi kích thước bằng nhau: mọi cách đặt ngoặc có cùng chi phí 24;
bản bottom-up chọn một trong các đáp án tối ưu đó.

---

## Nhóm 2 - Input sai (4 ca)

Mỗi ca kiểm tra chương trình phải ném `DimensionError` với thông điệp
**trùng khớp nguyên văn** (từng ký tự).

| ID  | Mô tả | Input | Thông điệp lỗi mong đợi |
|-----|-------|-------|-------------------------|
| E01 | Mảng một phần tử | `[5]` | `Mảng kích thước cần tối thiểu 2 phần tử để mô tả ít nhất 1 ma trận` |
| E02 | Chứa phần tử bằng 0 | `[10, 0, 5]` | `Phần tử tại vị trí 1 phải là số nguyên dương, không nhận 0` |
| E03 | Chứa phần tử âm | `[10, -3, 5]` | `Phần tử tại vị trí 1 phải là số nguyên dương, không nhận -3` |
| E04 | Chứa số thực | `[10, 2.5, 5]` | `Phần tử tại vị trí 1 phải là số nguyên dương, không nhận 2.5` |

---

## Tiêu chí đánh giá

- Ca hợp lệ **PASS** khi cả `cost` lẫn `parens` khớp giá trị mong đợi.
- Ca sai **PASS** khi chương trình ném `DimensionError` với thông điệp trùng khớp nguyên văn.
- Mọi `expected_cost` đã được đối chiếu với `naive_min_cost` (liệt kê toàn bộ).
