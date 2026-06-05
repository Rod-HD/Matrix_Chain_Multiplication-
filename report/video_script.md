# Kịch bản quay video demo - Matrix Chain Multiplication

Thời lượng đề xuất: 4-6 phút. Quay màn hình kèm giọng nói (OBS Studio hoặc
Xbox Game Bar: Win + G).

Trước khi quay, mở sẵn:
- Một terminal đã ở thư mục `version2`, đã kích hoạt venv.
- Trên Windows, chạy `set PYTHONIOENCODING=utf-8` để in tiếng Việt không lỗi font.
- Trình duyệt (chưa cần mở tab).

---

## Phân cảnh 1 - Giới thiệu (0:00 - 0:30)

Hiện màn hình terminal sạch hoặc mở `README.md`.

> "Đây là demo bài tập lớn Matrix Chain Multiplication. Bài toán: cho một
> chuỗi n ma trận, tìm cách đặt dấu ngoặc sao cho tổng số phép nhân vô hướng
> là ít nhất. Em cài đặt bằng quy hoạch động trên đoạn, kèm hai bản đối chiếu
> là đệ quy thuần và đệ quy có ghi nhớ. Em sẽ demo: chạy test, chạy dòng lệnh,
> đo hiệu năng, và giao diện web."

---

## Phân cảnh 2 - Chạy test (0:30 - 1:30)

```
pytest -q
```
Chờ ra dòng `42 passed`.

```
python testcases/run_testcases.py
```
Cuộn cho thấy `17/17 ca PASS`.

> "Bộ pytest có 42 test, gồm test ví dụ, test thông điệp lỗi, và test sinh
> ngẫu nhiên đối chiếu với liệt kê toàn bộ. Tất cả đều pass. Bộ testcase
> tường minh có 17 ca - 12 ca hợp lệ kiểm tra chi phí và dấu ngoặc, 5 ca sai
> kiểm tra thông điệp lỗi. Tất cả đều đúng."

---

## Phân cảnh 3 - Dòng lệnh (1:30 - 2:45)

1. Ví dụ kinh điển, in cả hai bảng:
```
python -m mcm2 30 35 15 5 10 20 25
```
> "Đây là ví dụ 6 ma trận. Bảng chi phí cho số phép nhân tối thiểu, bảng vị
> trí cắt cho điểm tách tối ưu. Kết quả: dấu ngoặc ((A1(A2A3))((A4A5)A6)),
> chi phí 15125."

2. Chỉ in kết quả:
```
python -m mcm2 30 35 15 5 10 20 25 --tables=none
```

3. Nhập qua stdin:
```
echo 3 10 7 2 | python -m mcm2
```

4. Thử dữ liệu sai:
```
python -m mcm2 10 0 5
```
> "Nếu nhập sai - ví dụ có phần tử bằng 0 - chương trình báo lỗi rõ ràng bằng
> tiếng Việt và không in kết quả."

---

## Phân cảnh 4 - Đo hiệu năng (2:45 - 3:30)

```
python bench_naive.py
```
> "Bảng này so số lần gọi của đệ quy thuần với bản ghi nhớ. Bản thuần tăng
> theo hàm mũ - tới n bằng 15 đã gần năm triệu lần gọi - trong khi bản ghi
> nhớ chỉ vài chục. Đây chính là lý do cần quy hoạch động."

```
python benchmark.py
```
> "Bảng này đo thời gian bản bottom-up. Khi n tăng gấp đôi, thời gian tăng
> khoảng tám lần, đúng với độ phức tạp n mũ ba."

---

## Phân cảnh 5 - Giao diện web (3:30 - 5:00)

```
python web_app.py
```
Mở `http://127.0.0.1:5001`.

1. Mở khối giải thích thu gọn ở đầu trang (bấm dòng "Mảng kích thước p được
   hiểu thế nào?").
> "Trước khi nhập, mình mở phần giải thích. Mảng p không phải kích thước của
> từng ma trận mà là chuỗi các mốc nối tiếp: ma trận thứ i nằm giữa mốc p[i-1]
> và p[i]. Sơ đồ này cho thấy mỗi ma trận trải dưới hai mốc liền kề, và con số
> ở giữa được dùng chung cho hai ma trận cạnh nhau."

2. Dùng bộ dựng để nhập: bấm + thêm ma trận, sửa kích thước, chỉ vào ô đỏ.
> "Mình nhập trực tiếp hàng nhân cột của từng ma trận. Ô số hàng tô đỏ là ô tự
> điền - nó luôn bằng số cột của ma trận trước nên không sửa được, đảm bảo
> chuỗi luôn hợp lệ. Phần xem trước hiện luôn chuỗi ma trận và mảng p tương
> ứng."

3. Bấm **Giải**, xem phần tóm tắt.
> "Phần tóm tắt hiện số ma trận, chi phí tối thiểu, số cách đặt ngoặc, và dấu
> ngoặc tối ưu."

4. Tab **Bảng chi phí & cắt**.
> "Tab đầu là hai bảng. Ô đáp số được tô nổi bật, ô không dùng để dấu gạch."

5. Tab **Các bước lấp bảng**, bấm **Sau** vài lần.
> "Tab này liệt kê từng bước theo độ dài đoạn. Mỗi ô hiện mọi vị trí cắt k kèm
> công thức, đánh dấu lựa chọn tối ưu, và tô sáng ô đang tính."

6. Tab **Cây dấu ngoặc**.
> "Tab cuối dựng biểu thức dấu ngoặc từ bảng vị trí cắt."

7. (Tuỳ chọn) nhập dữ liệu sai để thấy thông báo lỗi.

---

## Phân cảnh 6 - So sánh AI và kết luận (5:00 - 5:45)

(Tuỳ chọn) mở ảnh chụp ChatGPT giải cùng ví dụ.

> "Em cũng thử cho ChatGPT giải. Với ví dụ kinh điển, AI trả lời đúng. Nhưng
> với dữ liệu lạ, AI không phải lúc nào cũng kèm bảng đầy đủ và khó kiểm
> chứng. Hệ thống của em cho kết quả tất định, có kiểm tra chéo nội bộ, có ba
> lời giải đối chiếu và bộ testcase làm đối chứng, và minh hoạ được từng bước.
> Em xin kết thúc phần demo, cảm ơn thầy cô."

---

## Ghi chú quay

- Nói chậm, dừng vài giây sau mỗi lệnh để người xem kịp đọc.
- Phóng to cỡ chữ terminal để dễ nhìn.
- Nếu terminal lỗi font tiếng Việt, kiểm tra lại `PYTHONIOENCODING=utf-8`.
- Tắt server web bằng Ctrl + C sau khi quay xong.
