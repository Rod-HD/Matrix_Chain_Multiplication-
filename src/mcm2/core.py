"""Lõi thuật toán cho bài toán Matrix Chain Multiplication.

Quy ước chỉ số theo CLRS chương 15.2
(T. H. Cormen et al., Introduction to Algorithms, 3rd ed., MIT Press, 2009):
    - Chuỗi gồm n ma trận A_1, A_2, ..., A_n (1-based).
    - Ma trận A_i có kích thước p[i-1] x p[i]; p là mảng 0-based n+1 phần tử.
    - cost[i][j]: số phép nhân tối thiểu cho đoạn A_i..A_j, 1 <= i <= j <= n.
    - split[i][j]: vị trí cắt tối ưu k, i <= k < j.

Công thức truy hồi (CLRS 15.2, trang 370-378):

    cost[i][i] = 0
    cost[i][j] = min_{i <= k < j} ( cost[i][k] + cost[k+1][j]
                                    + p[i-1] * p[k] * p[j] )   với i < j

Đáp số: cost[1][n].

Ba lời giải để đối chiếu:
    - naive_min_cost: đệ quy thuần, độ phức tạp mũ.
    - memoized_min_cost: đệ quy có ghi nhớ (top-down), O(n^3).
    - bottom_up: lấp bảng theo độ dài đoạn tăng dần, O(n^3).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

from mcm2.validation import validate_dimensions

# Hằng số đại diện "vô cực" khi đi tìm cực tiểu. Mọi ứng viên chi phí thực
# tế đều nhỏ hơn giá trị này nên cực tiểu cuối cùng luôn là số nguyên.
INF = float("inf")


def naive_min_cost(dims: Sequence[int]) -> int:
    """Tính chi phí tối thiểu bằng đệ quy thuần (không ghi nhớ).

    Hàm này cố tình **không** lưu lại kết quả đoạn con, nên cùng một đoạn
    bị tính đi tính lại nhiều lần. Số lần gọi tăng theo số Catalan, tức
    theo hàm mũ. Mục đích duy nhất là minh hoạ vì sao cần quy hoạch động;
    chỉ nên gọi với n nhỏ.

    Tham số:
        dims: mảng kích thước p (đã hoặc chưa kiểm tra đều được; hàm tự
            kiểm tra).

    Trả về:
        Số phép nhân vô hướng tối thiểu cho cả chuỗi.
    """
    n = validate_dimensions(dims)
    p = list(dims)

    def cost(i: int, j: int) -> int:
        # Đoạn chỉ có một ma trận: không cần phép nhân nào.
        if i == j:
            return 0
        best = INF
        # Thử mọi cách đặt dấu ngoặc ngoài cùng tại vị trí cắt k.
        for k in range(i, j):
            # Công thức CLRS: p[i-1] * p[k] * p[j]
            q = cost(i, k) + cost(k + 1, j) + p[i - 1] * p[k] * p[j]
            if q < best:
                best = q
        return best

    return cost(1, n)


def memoized_min_cost(dims: Sequence[int]) -> int:
    """Tính chi phí tối thiểu bằng đệ quy có ghi nhớ (top-down).

    Mỗi đoạn (i, j) chỉ được giải đúng một lần rồi lưu lại, nên tổng số
    trạng thái là O(n^2) và mỗi trạng thái quét O(n) vị trí cắt, cho độ
    phức tạp O(n^3) - bằng đúng bản bottom-up nhưng tính theo nhu cầu.

    Tham số:
        dims: mảng kích thước p.

    Trả về:
        Số phép nhân vô hướng tối thiểu cho cả chuỗi.
    """
    n = validate_dimensions(dims)
    p = list(dims)

    @lru_cache(maxsize=None)
    def cost(i: int, j: int) -> int:
        if i == j:
            return 0
        best = INF
        for k in range(i, j):
            q = cost(i, k) + cost(k + 1, j) + p[i - 1] * p[k] * p[j]
            if q < best:
                best = q
        return best

    result = cost(1, n)
    cost.cache_clear()  # giải phóng bộ nhớ cache sau khi xong
    return result


def bottom_up(
    dims: Sequence[int],
) -> tuple[list[list[int]], list[list[int]]]:
    """Lấp bảng quy hoạch động từ dưới lên theo độ dài đoạn tăng dần.

    Lấp bảng theo chiều dài đoạn length = 2..n đảm bảo: khi tính
    cost[i][j], mọi đoạn con ngắn hơn (cost[i][k] và cost[k+1][j]) đều đã
    có sẵn. Đây là điểm mấu chốt của thứ tự "theo đường chéo" mà bài toán
    này nổi tiếng khó hình dung.

    Tham số:
        dims: mảng kích thước p (hàm tự kiểm tra hợp lệ).

    Trả về:
        Cặp (cost, split), đều là ma trận (n+1) x (n+1) với chỉ số gốc 1
        theo CLRS (ô index 0 không dùng):
            - cost[i][j]: chi phí tối thiểu cho đoạn A_i..A_j (i <= j).
              Ô i > j không dùng, giữ giá trị 0.
            - split[i][j]: vị trí cắt tối ưu k (i <= k < j) cho đoạn i..j.
              Ô i >= j không dùng, giữ giá trị 0.
        Đáp số là cost[1][n].
    """
    n = validate_dimensions(dims)
    p = list(dims)

    # Bảng kích thước (n+1) x (n+1); ô index 0 là padding không dùng.
    cost = [[0] * (n + 1) for _ in range(n + 1)]
    split = [[0] * (n + 1) for _ in range(n + 1)]

    # Đường chéo cost[i][i] = 0 cho mọi i = 1..n (đã sẵn bằng 0).
    for i in range(1, n + 1):
        cost[i][i] = 0

    # Lấp bảng theo độ dài đoạn tăng dần (length = 2..n).
    for length in range(2, n + 1):
        # i: chỉ số đầu đoạn A_i..A_j với j = i + length - 1 <= n.
        for i in range(1, n - length + 2):
            j = i + length - 1
            best = INF
            best_k = i
            # k: vị trí cắt, chia đoạn thành (A_i..A_k)(A_{k+1}..A_j).
            for k in range(i, j):
                # Công thức CLRS 15.2: q = cost[i][k] + cost[k+1][j] + p[i-1]*p[k]*p[j]
                q = cost[i][k] + cost[k + 1][j] + p[i - 1] * p[k] * p[j]
                if q < best:
                    best = q
                    best_k = k
            cost[i][j] = best
            split[i][j] = best_k

    return cost, split


def optimal_parenthesization(split: list[list[int]], i: int, j: int) -> str:
    """Dựng chuỗi dấu ngoặc tối ưu cho đoạn A_i..A_j từ bảng split.

    Truy vết đệ quy theo vị trí cắt đã lưu trong bảng split (CLRS
    PRINT-OPTIMAL-PARENS). Tên ma trận theo chỉ số 1-based (A1, A2, ...).

    Tham số:
        split: bảng vị trí cắt do bottom_up trả về.
        i, j: hai đầu đoạn (1-based), 1 <= i <= j <= n.

    Trả về:
        Chuỗi dấu ngoặc, ví dụ "((A1(A2A3))A4)". Khi i == j trả về "A{i}".
    """
    if i == j:
        return f"A{i}"
    k = split[i][j]
    left = optimal_parenthesization(split, i, k)
    right = optimal_parenthesization(split, k + 1, j)
    return f"({left}{right})"


def count_parenthesizations(n: int) -> int:
    """Đếm số cách đặt dấu ngoặc cho chuỗi n ma trận (số Catalan C_{n-1}).

    Số cách đặt ngoặc khác nhau của n ma trận đúng bằng số Catalan thứ
    n - 1. Hàm dùng để minh hoạ kích thước không gian tìm kiếm mà lời giải
    đệ quy thuần phải duyệt.

    Tham số:
        n: số ma trận (n >= 1).

    Trả về:
        Số Catalan C_{n-1}. Quy ước trả về 1 khi n <= 1.
    """
    if n <= 1:
        return 1
    # C_m = (2m)! / ((m+1)! m!) với m = n - 1, tính bằng truy hồi nguyên.
    m = n - 1
    c = 1
    for k in range(m):
        c = c * 2 * (2 * k + 1) // (k + 2)
    return c


@dataclass(frozen=True)
class ChainResult:
    """Gói toàn bộ kết quả của một lần giải để tiện truyền đi nơi khác.

    Thuộc tính:
        n: số ma trận.
        dims: mảng kích thước gốc.
        cost: bảng chi phí (n+1) x (n+1), chỉ số 1-based. Đáp số cost[1][n].
        split: bảng vị trí cắt (n+1) x (n+1), chỉ số 1-based.
        min_cost: chi phí tối thiểu của cả chuỗi (cost[1][n]).
        parenthesization: chuỗi dấu ngoặc tối ưu.
    """

    n: int
    dims: list[int]
    cost: list[list[int]]
    split: list[list[int]]
    min_cost: int
    parenthesization: str


def solve(dims: Sequence[int]) -> ChainResult:
    """Giải trọn vẹn bài toán và kiểm tra chéo tính nhất quán.

    Quy trình: kiểm tra hợp lệ -> lấp bảng bottom-up -> truy vết dấu ngoặc
    -> tính lại chi phí từ dấu ngoặc và đối chiếu với cost[1][n]. Nếu hai
    con số lệch nhau thì có lỗi cài đặt và hàm sẽ báo lỗi ngay thay vì trả
    về kết quả sai.

    Tham số:
        dims: mảng kích thước p.

    Trả về:
        Một ChainResult chứa đầy đủ bảng và đáp số.

    Ném:
        DimensionError: nếu mảng kích thước không hợp lệ.
        RuntimeError: nếu phát hiện bất nhất quán nội bộ.
    """
    n = validate_dimensions(dims)
    p = list(dims)
    cost, split = bottom_up(p)
    parens = optimal_parenthesization(split, 1, n)

    # Kiểm tra chéo: tính lại chi phí trực tiếp từ bảng split, độc lập với
    # bảng cost, rồi so với đáp số. Bắt được cả split sai khoảng lẫn bảng
    # cost/split lệch nhau.
    recomputed = _recompute_from_split(split, p, 1, n)
    if recomputed != cost[1][n]:
        raise RuntimeError(
            f"Bất nhất quán nội bộ: cost[1][{n}] = {cost[1][n]} "
            f"nhưng chi phí suy ra từ bảng split là {recomputed}"
        )

    return ChainResult(
        n=n,
        dims=p,
        cost=cost,
        split=split,
        min_cost=cost[1][n],
        parenthesization=parens,
    )


def _recompute_from_split(
    split: list[list[int]], p: list[int], i: int, j: int
) -> int:
    """Tính lại chi phí đoạn A_i..A_j chỉ dựa trên bảng split (kiểm tra chéo).

    Tham số:
        split: bảng vị trí cắt.
        p: mảng kích thước (0-based: p[0]..p[n]).
        i, j: hai đầu đoạn (1-based), 1 <= i <= j <= n.

    Trả về:
        Tổng số phép nhân vô hướng suy ra từ cấu trúc dấu ngoặc.

    Ném:
        RuntimeError: nếu split[i][j] nằm ngoài khoảng [i, j-1].
    """
    if i == j:
        return 0
    k = split[i][j]
    if not (i <= k < j):
        raise RuntimeError(
            f"Bất nhất quán nội bộ: split[{i}][{j}] = {k} ngoài khoảng [{i}, {j - 1}]"
        )
    left = _recompute_from_split(split, p, i, k)
    right = _recompute_from_split(split, p, k + 1, j)
    # Công thức CLRS: p[i-1] * p[k] * p[j]
    return left + right + p[i - 1] * p[k] * p[j]
