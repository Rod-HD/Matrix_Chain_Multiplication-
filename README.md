# Matrix Chain Multiplication

Cài đặt bài toán **Matrix Chain Multiplication (MCM)** bằng quy hoạch động trên
đoạn (interval dynamic programming), kèm dòng lệnh, bộ kiểm thử, đo hiệu năng và
một giao diện web minh hoạ từng bước.

> Môn CS112 - Phân tích và Thiết kế Thuật toán (UIT).

---

## Mục lục

- [1. Bài toán](#1-bài-toán)
- [2. Công thức và thuật toán](#2-công-thức-và-thuật-toán)
- [3. Cài đặt](#3-cài-đặt)
- [4. Dùng qua dòng lệnh (CLI)](#4-dùng-qua-dòng-lệnh-cli)
- [5. Dùng như thư viện Python](#5-dùng-như-thư-viện-python)
- [6. Giao diện web demo](#6-giao-diện-web-demo)
- [7. Kiểm thử](#7-kiểm-thử)
- [8. Đo hiệu năng](#8-đo-hiệu-năng)
- [9. Cấu trúc dự án](#9-cấu-trúc-dự-án)
- [10. Hiểu mảng kích thước `p`](#10-hiểu-mảng-kích-thước-p)
- [11. Quyết định thiết kế](#11-quyết-định-thiết-kế)
- [12. Xử lý lỗi thường gặp](#12-xử-lý-lỗi-thường-gặp)
- [13. Tài liệu tham khảo](#13-tài-liệu-tham-khảo)

---

## 1. Bài toán

Cho chuỗi `n` ma trận `A_1, A_2, ..., A_n`, trong đó ma trận `A_i` có kích thước
`p[i] × p[i+1]`. Toàn bộ kích thước mô tả bằng mảng `p` gồm `n + 1` phần tử.

Phép nhân ma trận có tính kết hợp: `(AB)C = A(BC)`. Kết quả không đổi nhưng
**số phép nhân vô hướng** thì phụ thuộc cách đặt dấu ngoặc. Ví dụ với
`A_1 (10×100)`, `A_2 (100×5)`, `A_3 (5×50)`:

| Cách đặt ngoặc | Số phép nhân |
|---|---|
| `((A1 A2) A3)` | `10·100·5 + 10·5·50` = **7500** |
| `(A1 (A2 A3))` | `100·5·50 + 10·100·50` = **75000** |

Cùng một tích nhưng lệch nhau gấp 10 lần. Bài toán MCM: **tìm cách đặt dấu ngoặc
để tổng số phép nhân vô hướng là nhỏ nhất** (chỉ tính chi phí và thứ tự, không
thực hiện phép nhân thật).

---

## 2. Công thức và thuật toán

Gọi `cost[i][j]` là số phép nhân tối thiểu để nhân đoạn `A_i..A_j`
(chỉ số gốc 0, `0 ≤ i ≤ j ≤ n-1`):

```
cost[i][i] = 0
cost[i][j] = min   ( cost[i][k] + cost[k+1][j] + p[i-1]·p[k]·p[j] )
           i ≤ k < j
```

Đáp số là `cost[1][n]` (chỉ số 1-based theo CLRS, với ma trận A_1..A_n và mảng kích thước p[0..n]).

Hệ thống cung cấp **ba lời giải** cho cùng công thức trên:

| Lời giải | Hàm | Độ phức tạp | Mục đích |
|---|---|---|---|
| Đệ quy thuần | `naive_min_cost` | mũ (`~3^(n-1)` lần gọi) | minh hoạ vì sao cần quy hoạch động |
| Đệ quy có ghi nhớ | `memoized_min_cost` | `O(n³)` thời gian, `O(n²)` bộ nhớ | top-down, tính theo nhu cầu |
| Lấp bảng từ dưới lên | `bottom_up` | `O(n³)` thời gian, `O(n²)` bộ nhớ | bản chính, có truy vết dấu ngoặc |

Bản bottom-up lấp bảng theo **độ dài đoạn tăng dần** (`length = 2..n`), đảm bảo
khi tính một đoạn thì mọi đoạn con ngắn hơn đã có sẵn.

---

## 3. Cài đặt

Yêu cầu **Python 3.10+**. Phần lõi chỉ dùng thư viện chuẩn; `pytest` chỉ cần khi
chạy test, `flask` chỉ cần khi chạy web demo.

```bash
# (khuyến nghị) tạo môi trường ảo riêng
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# cài gói ở chế độ phát triển, kèm pytest
pip install -e ".[dev]"
```

Cài kèm cả Flask cho web demo:

```bash
pip install -e ".[dev,web]"
```

Kiểm tra nhanh sau khi cài:

```bash
python -c "import mcm2; print('mcm2 OK')"
```

---

## 4. Dùng qua dòng lệnh (CLI)

Cú pháp: `python -m mcm2 [các_kích_thước...] [--tables {both,cost,split,none}]`

```bash
python -m mcm2 30 35 15 5 10 20 25                  # in cả hai bảng (mặc định)
python -m mcm2 30 35 15 5 10 20 25 --tables=cost    # chỉ bảng chi phí
python -m mcm2 30 35 15 5 10 20 25 --tables=split   # chỉ bảng vị trí cắt
python -m mcm2 30 35 15 5 10 20 25 --tables=none    # chỉ in kết quả
echo 30 35 15 5 10 20 25 | python -m mcm2           # nhập qua stdin
```

| Tham số | Ý nghĩa | Mặc định |
|---|---|---|
| `dims` | Mảng kích thước `p`, cách nhau bằng khoảng trắng. Bỏ trống thì đọc từ `stdin`. | (đọc stdin) |
| `--tables` | `both` / `cost` / `split` / `none` — chọn bảng để in | `both` |

**Mã thoát:** `0` thành công · `1` lỗi dữ liệu (mảng không hợp lệ) · `2` lỗi nội
bộ (bất nhất quán — về lý thuyết không xảy ra).

### Kết quả mẫu

`python -m mcm2 30 35 15 5 10 20 25`

```
Bảng chi phí (số phép nhân tối thiểu của từng đoạn):
              1       2       3       4       5       6
      1       0   15750    7875    9375   11875   15125
      2       -       0    2625    4375    7125   10500
      3       -       -       0     750    2500    5375
      4       -       -       -       0    1000    3500
      5       -       -       -       -       0    5000
      6       -       -       -       -       -       0
Bảng vị trí cắt tối ưu:
      1   2   3   4   5   6
  1   -   1   1   3   3   3
  2   -   -   2   3   3   3
  3   -   -   -   3   3   3
  4   -   -   -   -   4   5
  5   -   -   -   -   -   5
  6   -   -   -   -   -   -
Dấu ngoặc tối ưu: ((A1(A2A3))((A4A5)A6))
Số phép nhân vô hướng tối thiểu: 15125
```

**Đọc kết quả:**
- `cost[0][5] = 15125`: chuỗi 6 ma trận cần tối thiểu 15.125 phép nhân vô hướng.
- `split[1][6] = 3`: tách tối ưu tại `k = 3`, tức `(A1A2A3)(A4A5A6)`.
- Trong bảng, nhãn hàng/cột là tên ma trận (1-based); ô không dùng để dấu `-`.

---

## 5. Dùng như thư viện Python

API công khai gom trong `mcm2`:

```python
from mcm2 import solve

result = solve([30, 35, 15, 5, 10, 20, 25])
print(result.n)                 # 6
print(result.min_cost)          # 15125
print(result.parenthesization)  # ((A1(A2A3))((A4A5)A6))
print(result.cost[1][6])        # 15125  (đáp số cost[1][n])
print(result.split[1][6])       # 3      (vị trí cắt k=3 theo CLRS)
```

### Các hàm và kiểu chính

| Tên | Chữ ký | Ghi chú |
|---|---|---|
| `validate_dimensions(dims)` | `-> int` | trả `n = len(dims) - 1`; ném `DimensionError` nếu sai |
| `bottom_up(dims)` | `-> (cost, split)` | hai bảng `(n+1) × (n+1)`, 1-based theo CLRS |
| `naive_min_cost(dims)` | `-> int` | đệ quy thuần, chỉ dùng cho `n` nhỏ |
| `memoized_min_cost(dims)` | `-> int` | đệ quy có ghi nhớ |
| `optimal_parenthesization(split, i, j)` | `-> str` | dựng dấu ngoặc cho đoạn `A_i..A_j` |
| `count_parenthesizations(n)` | `-> int` | số Catalan `C_{n-1}` (số cách đặt ngoặc) |
| `solve(dims)` | `-> ChainResult` | giải trọn vẹn + kiểm tra chéo nội bộ |
| `format_cost_table(cost, n)` | `-> str` | bảng chi phí dạng văn bản |
| `format_split_table(split, n)` | `-> str` | bảng vị trí cắt dạng văn bản |
| `render_result(result, *, show_cost, show_split)` | `-> str` | gộp bảng + kết quả |

`ChainResult` là một dataclass bất biến gồm: `n`, `dims`, `cost`, `split`,
`min_cost`, `parenthesization`.

### Ví dụ dùng từng lời giải

```python
from mcm2 import naive_min_cost, memoized_min_cost, bottom_up

p = [10, 20, 50, 1, 100]
assert naive_min_cost(p) == 2200          # liệt kê toàn bộ
assert memoized_min_cost(p) == 2200       # top-down
cost, split = bottom_up(p)                # bottom-up
assert cost[0][len(p) - 2] == 2200
```

### Định dạng đầu ra tuỳ chọn

```python
from mcm2 import solve, render_result

result = solve([3, 10, 7, 2])
print(render_result(result, show_cost=True, show_split=False))
# Bảng chi phí (...)
# Dấu ngoặc tối ưu: (A1(A2A3))
# Số phép nhân vô hướng tối thiểu: 200
```

---

## 6. Giao diện web demo

```bash
pip install flask                # nếu chưa cài
python web_app.py                # mặc định http://127.0.0.1:5001
```

Mở trình duyệt vào địa chỉ in ra (mặc định `http://127.0.0.1:5001`). Tắt máy chủ
bằng `Ctrl + C`.

> Nếu đã có sẵn `venv` ở thư mục gốc dự án (có Flask), chạy nhanh:
> `..\venv\Scripts\python.exe web_app.py`

### Cách nhập liệu

Mảng `p` dễ gây nhầm vì nó là *chuỗi các mốc kích thước nối tiếp* chứ không phải
kích thước rời rạc của từng ma trận. Giao diện gỡ rào cản này bằng **bộ dựng
theo từng ma trận**:

- Mỗi ma trận là một dòng `Ai: [hàng] × [cột]`; thêm/bớt bằng nút `+` / `-`.
- Ô **số hàng** của mọi ma trận (trừ ma trận đầu) bị khoá và **tô đỏ**, tự lấy
  bằng số cột của ma trận liền trước — đảm bảo điều kiện "cột trước = hàng sau"
  nên không thể nhập chuỗi không hợp lệ.
- **Xem trước** hiển thị song song "Chuỗi ma trận" (vd `A1(30×35) · A2(35×15) …`)
  và "Mảng kích thước p" tương ứng.
- **Khối giải thích thu gọn** (bấm để mở) trình bày quy tắc `Ai = p[i-1] × p[i]`
  kèm sơ đồ mỗi ma trận trải dưới hai mốc kích thước liền kề.
- **Nhập nhanh:** dán thẳng mảng `p` phẳng nếu muốn.

### Ba tab kết quả

1. **Bảng chi phí & cắt** — hai bảng đầy đủ; ô đáp số tô nổi bật, ô không dùng để
   dấu `-`.
2. **Các bước lấp bảng** — mỗi bước ứng với một đoạn `(i, j)`, liệt kê mọi vị trí
   cắt `k` kèm công thức và đánh dấu lựa chọn tối ưu; có nút *Trước / Sau*, ô đang
   tính được tô sáng trên bảng.
3. **Cây dấu ngoặc** — dựng biểu thức dấu ngoặc tối ưu từ bảng vị trí cắt.

### API web

| Endpoint | Phương thức | Mô tả |
|---|---|---|
| `/` | GET | trả trang chính |
| `/api/solve` | POST | nhận `{"dims": [...]}`, trả JSON kết quả |

Phản hồi JSON gồm: `n`, `dims`, `min_cost`, `parenthesization`,
`num_parenthesizations`, `cost_table`, `split_table`, `steps`. Khi dữ liệu sai,
trả HTTP 400 kèm `{"error": "..."}`.

---

## 7. Kiểm thử

Hai lớp kiểm thử bổ trợ nhau.

### Bộ pytest (42 test)

```bash
pytest -q                        # chạy toàn bộ
pytest tests/test_core.py -v     # riêng phần lõi
```

Gồm: test 4 ví dụ bắt buộc, test ba lời giải cho cùng kết quả, test thông điệp
lỗi, và các test dựa trên tính chất (sinh ngẫu nhiên bằng `random.Random(seed)`
cố định, đối chiếu với liệt kê toàn bộ để chứng minh tối ưu toàn cục).

### Bộ testcase tường minh (16 ca)

```bash
python testcases/run_testcases.py
```

In bảng PASS/FAIL cho 12 ca hợp lệ + 4 ca sai. Dữ liệu ở `testcases/cases.json`,
mọi chi phí kỳ vọng đã được đối chiếu độc lập bằng `naive_min_cost`.

---

## 8. Đo hiệu năng

```bash
python benchmark.py              # thời gian bottom-up theo n
python bench_naive.py            # số lần gọi: thuần vs ghi nhớ vs Catalan
```

`benchmark.py` đo thời gian bottom-up với `n = 50..400` (lấy min qua nhiều lần
chạy, seed cố định) và so tỉ lệ tăng với `Θ(n³)`.

`bench_naive.py` đếm số lần gọi đệ quy: bản thuần tăng theo `~3^(n-1)`, bản ghi
nhớ chỉ `n(n+1)/2` — minh hoạ trực tiếp lý do cần quy hoạch động.

Số liệu tham khảo (Python 3.13): `n=50 ≈ 2.3ms`, `n=100 ≈ 19ms`, `n=200 ≈ 150ms`,
`n=300 ≈ 547ms`, `n=400 ≈ 1.5s`. Khi `n` tăng gấp đôi, thời gian tăng ~8 lần, đúng với `Θ(n³)`.

---

## 9. Cấu trúc dự án

```
matrix-chain/
├── src/mcm2/
│   ├── __init__.py        # gom public API
│   ├── validation.py      # validate_dimensions, DimensionError
│   ├── core.py            # ba lời giải + truy vết + kiểm tra chéo
│   ├── display.py         # format_cost_table, format_split_table, render_result
│   ├── cli.py             # giao diện dòng lệnh (argparse)
│   └── __main__.py        # cho phép `python -m mcm2`
├── tests/
│   ├── test_validation.py
│   ├── test_core.py
│   └── test_display.py
├── testcases/
│   ├── cases.json         # 12 ca hợp lệ + 4 ca sai (máy đọc)
│   ├── testcases.md       # dữ liệu test dạng bảng Markdown
│   ├── testcases.txt      # dữ liệu test dạng văn bản thuần
│   ├── run_testcases.py   # trình chấm
│   └── README.md
├── templates/index.html   # giao diện web
├── static/
│   ├── style.css
│   └── app.js
├── web_app.py             # máy chủ Flask
├── benchmark.py           # đo thời gian bottom-up
├── bench_naive.py         # đếm số lần gọi đệ quy
├── benchmark_results.txt  # kết quả đo thực tế (xem thủ công)
├── report/                # báo cáo LaTeX + kịch bản video
│   ├── report.tex
│   ├── report.pdf
│   ├── UIT.png
│   └── video_script.md
├── pyproject.toml
└── README.md
```

**Tách trách nhiệm:** mọi tính toán là hàm thuần (không in, không I/O); chỉ
`cli.py` và `web_app.py` đụng tới vào/ra. Nhờ vậy có thể gọi trực tiếp hàm trong
test và so sánh giá trị trả về.

---

## 10. Hiểu mảng kích thước `p`

Đây là điểm dễ nhầm nhất. Mảng `p` **không** liệt kê kích thước của từng ma trận
mà là chuỗi các mốc kích thước nối tiếp: ma trận thứ `i` có kích thước
`p[i-1] × p[i]` (1-based), nên số cột của một ma trận đồng thời là số hàng của ma
trận đứng sau.

Với `p = [30, 35, 15, 5, 10, 20, 25]` (7 số → 6 ma trận):

```
p:   30   35   15    5   10   20   25
     └─A1─┘
          └─A2─┘
               └A3┘
                   └A4┘
                      └─A5─┘
                           └─A6─┘
```

→ `A1 = 30×35`, `A2 = 35×15`, `A3 = 15×5`, `A4 = 5×10`, `A5 = 10×20`,
`A6 = 20×25`. Con số `35` vừa là cột của `A1` vừa là hàng của `A2` nên chỉ ghi
một lần. Đây cũng là điều kiện để hai ma trận liền kề nhân được với nhau.

---

## 11. Quyết định thiết kế

- **Chỉ số gốc 0.** Cả ma trận lẫn bảng đều dùng index 0, hệ số truy hồi viết là
  `p[i]·p[k+1]·p[j+1]`. Theo cách phát biểu gọn của Dasgupta-Papadimitriou-Vazirani.
  Tương đương cách 1-based của Cormen (`p[i-1]·p[k]·p[j]`), chỉ khác việc dịch chỉ số.
- **Ba lời giải đối chiếu.** Bản thuần và bản ghi nhớ dùng làm đối chứng cho bản
  bottom-up; điều này giúp phát hiện sai sót và minh hoạ giá trị của quy hoạch
  động.
- **Kiểm tra chéo nội bộ.** Sau khi giải, `solve` tính lại chi phí *chỉ từ bảng
  split* và so với `cost[1][n]`. Lệch nhau thì ném `RuntimeError` thay vì in
  kết quả sai.
- **Hàm thuần, tách I/O.** Dễ kiểm thử, dễ tái sử dụng trong cả CLI lẫn web.
- **Chỉ thư viện chuẩn cho phần lõi.** `pytest` và `flask` chỉ là phụ thuộc tuỳ
  chọn.

---

## 12. Xử lý lỗi thường gặp

| Tình huống | Thông điệp / hành vi |
|---|---|
| Mảng dưới 2 phần tử | `DimensionError`: "Mảng kích thước cần tối thiểu 2 phần tử để mô tả ít nhất 1 ma trận" |
| Phần tử ≤ 0 hoặc không phải số nguyên (số thực, chuỗi, bool) | `DimensionError`: "Phần tử tại vị trí i phải là số nguyên dương, không nhận ..." |
| `ModuleNotFoundError: mcm2` | chưa `pip install -e .`, hoặc chưa kích hoạt venv |
| `ModuleNotFoundError: flask` | chỉ cần khi chạy web demo: `pip install flask` |
| Tiếng Việt lỗi font trên Windows console | đặt `set PYTHONIOENCODING=utf-8` trước khi chạy |
| Cổng 5001 bận | sửa `port=5001` trong `web_app.py` sang cổng khác |

`DimensionError` kế thừa `ValueError`, nên có thể bắt bằng `except ValueError`.

---

## 13. Tài liệu tham khảo

- T. H. Cormen, C. E. Leiserson, R. L. Rivest, C. Stein. *Introduction to
  Algorithms*, Third Edition. The MIT Press, 2009. ISBN 978-0-262-03384-8.
  Chương 15, mục 15.2: Matrix-chain multiplication, trang 370-378.
  *(Công thức truy hồi, quy ước chỉ số, bảng split, truy vết.)*
- S. Dasgupta, C. H. Papadimitriou, U. V. Vazirani. *Algorithms*.
  Bản thảo, 2006. Chương 6, mục 6.5: Chain matrix multiplication.
  *(Phát biểu bài toán bổ sung.)*
- Huỳnh Thị Thanh Thương. *Bài giảng 16: Thiết kế thuật toán - Kỹ thuật
  Quy hoạch động*, môn CS112, mã C3T13. UIT, 30/05/2023.
  *(Mã giả và công thức truy hồi tham chiếu.)*
```
