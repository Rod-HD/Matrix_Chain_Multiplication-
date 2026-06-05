# Bộ testcase tường minh - Matrix Chain Multiplication

Bộ testcase này tách riêng với pytest trong `tests/`. Mỗi ca nêu rõ **đầu
vào** và **kết quả mong đợi** để người chấm đối chiếu trực tiếp.

## Cấu trúc

- `cases.json` - dữ liệu test dạng máy đọc, hai nhóm:
  - `valid`: 12 ca hợp lệ, mỗi ca có `expected_cost` và `expected_parens`.
  - `invalid`: 4 ca dữ liệu sai, mỗi ca có `expected_error`.
- `testcases.md` - dữ liệu test dạng bảng Markdown, dễ đọc trên GitHub/IDE.
- `testcases.txt` - dữ liệu test dạng văn bản thuần, mở được bằng mọi editor.
- `run_testcases.py` - trình chạy: nạp `cases.json`, chạy từng ca qua
  `solve`, so khớp và in bảng PASS/FAIL.

## Cách chạy

Từ thư mục gốc dự án:

```bash
python testcases/run_testcases.py
```

## Cách dựng giá trị mong đợi

- Bốn ca `V01`-`V04` lấy từ ví dụ trong tài liệu môn học và Cormen.
- Các ca `V05`-`V12` được thiết kế để phủ nhiều dạng cấu trúc: chuỗi 2 ma
  trận (một cách nhân duy nhất), thứ tự ngoặc đổi chi phí lớn, kích thước
  tăng/giảm/bằng nhau, dao động mạnh và hỗn hợp ngẫu nhiên.
- Mọi `expected_cost` đều được đối chiếu độc lập bằng lời giải đệ quy thuần
  (`naive_min_cost`) liệt kê toàn bộ cách đặt ngoặc, nên là chi phí tối ưu
  thật. Với các ca có nhiều lời giải cùng chi phí (ví dụ `V09`), trường
  `expected_parens` ghi đúng dấu ngoặc mà bản bottom-up chọn.

## Tiêu chí đánh giá

- Ca hợp lệ PASS khi **cả** chi phí lẫn dấu ngoặc khớp.
- Ca sai PASS khi `solve` ném `DimensionError` với thông điệp **trùng khớp
  nguyên văn**.
