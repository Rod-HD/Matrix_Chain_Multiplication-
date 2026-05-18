# Matrix Chain Multiplication — Quy hoạch động Bottom-Up (CLRS 15.2)

## Mô tả bài toán

Cho chuỗi `n` ma trận `<A₁, A₂, …, Aₙ>` trong đó ma trận `Aᵢ` có kích thước `p[i-1] × p[i]`, bài toán **Matrix Chain Multiplication (MCM)** yêu cầu tìm cách đặt ngoặc (parenthesization) sao cho tổng số phép nhân vô hướng khi tính tích `A₁·A₂·…·Aₙ` là **ít nhất**.

Chương trình triển khai thuật toán **quy hoạch động Bottom-Up** theo đúng mã giả `MATRIX-CHAIN-ORDER` và `PRINT-OPTIMAL-PARENS` trong CLRS chương 15.2, sử dụng ba vòng lặp lồng nhau với độ phức tạp **Θ(n³)** thời gian và **Θ(n²)** bộ nhớ.

## Công thức truy hồi

```
m[i, j] = 0                                              nếu i = j

m[i, j] = min { m[i, k] + m[k+1, j] + p[i-1]·p[k]·p[j] }   nếu i < j
          i ≤ k < j
```

Trong đó:
- `m[i, j]` là số phép nhân vô hướng tối thiểu để tính `Aᵢ × … × Aⱼ`
- `s[i, j] = k` là vị trí tách tối ưu chia chuỗi thành `(Aᵢ…Aₖ)(Aₖ₊₁…Aⱼ)`

## Cài đặt

Yêu cầu: **Python 3.10+** (chỉ dùng thư viện chuẩn cho runtime).

```bash
# Clone repo và cài ở chế độ phát triển (bao gồm pytest):
pip install -e ".[dev]"
```

## Sử dụng

### Qua dòng lệnh (positional arguments)

```bash
# Mode full (mặc định): in bảng m, bảng s, cách đóng ngoặc, chi phí tối thiểu
python -m mcm 30 35 15 5 10 20 25 --mode=full

# Mode none: chỉ in cách đóng ngoặc và chi phí tối thiểu
python -m mcm 30 35 15 5 10 20 25 --mode=none

# Mode partial: in một bảng (m hoặc s) + kết quả
python -m mcm 30 35 15 5 10 20 25 --mode=partial --table=m
python -m mcm 30 35 15 5 10 20 25 --mode=partial --table=s
```

### Qua stdin

```bash
echo "30 35 15 5 10 20 25" | python -m mcm --mode=full
```

### Sử dụng như thư viện Python

```python
from mcm import MCMSolver, DisplayMode, format_trace

p = [30, 35, 15, 5, 10, 20, 25]
solver = MCMSolver(p)

print(solver.cost)    # 15125
print(solver.parens)  # ((A1(A2A3))((A4A5)A6))

# In trace đầy đủ
print(format_trace(solver.p, solver.m, solver.s, DisplayMode.FULL_TABLES))
```

## Sample Output

Chạy `python -m mcm 30 35 15 5 10 20 25 --mode=full` với ví dụ kinh điển CLRS (6 ma trận):

```
Bảng m:
            j=1     j=2     j=3     j=4     j=5     j=6
    i=1       0   15750    7875    9375   11875   15125
    i=2       -       0    2625    4375    7125   10500
    i=3       -       -       0     750    2500    5375
    i=4       -       -       -       0    1000    3500
    i=5       -       -       -       -       0    5000
    i=6       -       -       -       -       -       0
Bảng s:
        j=2   j=3   j=4   j=5   j=6
  i=1     1     1     3     3     3
  i=2     -     2     3     3     3
  i=3     -     -     3     3     3
  i=4     -     -     -     4     5
  i=5     -     -     -     -     5
Cách đóng mở ngoặc tối ưu: ((A1(A2A3))((A4A5)A6))
Số phép nhân vô hướng tối thiểu: 15125
```

**Giải thích kết quả:**
- `m[1,6] = 15125`: cần tối thiểu 15.125 phép nhân vô hướng
- `s[1,6] = 3`: tách tối ưu tại `k=3`, tức `(A₁A₂A₃)(A₄A₅A₆)`
- Cách đóng ngoặc đầy đủ: `((A₁(A₂A₃))((A₄A₅)A₆))`

## Chạy test

```bash
# Chạy toàn bộ test suite
pytest -v

# Chạy riêng test solver
pytest tests/test_solver.py -v

# Chạy riêng test formatter
pytest tests/test_formatter.py -v
```

## Cấu trúc dự án

```
matrix-chain/
├── src/mcm/
│   ├── __init__.py       # Re-export public API
│   ├── solver.py         # matrix_chain_order, print_optimal_parens, MCMSolver
│   ├── validator.py      # validate_dimension_array
│   ├── formatter.py      # DisplayMode, format_table, format_trace
│   ├── cli.py            # Entry point CLI (argparse)
│   └── __main__.py       # python -m mcm
├── tests/
│   ├── test_validator.py
│   ├── test_solver.py
│   └── test_formatter.py
├── pyproject.toml
└── README.md
```

## Tham chiếu

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press. **Chapter 15.2: Matrix-chain multiplication**.
- Slide bài giảng môn "Phân tích và Thiết kế Thuật toán" — Giảng viên Huỳnh Thị Thanh Thương, UIT.
