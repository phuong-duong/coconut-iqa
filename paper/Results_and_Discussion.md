# 5. Kết quả và thảo luận (Results and Discussion)

> Quy ước số liệu: chỉ dùng số thật từ pipeline đã chạy. Ô `[CHỜ SỐ]` là chỉ số thuộc
> bước chưa hoàn tất (mô hình IQA cuối `train_iqa`, LF6 suy giảm có kiểm soát, quét kích
> thước đầu vào), sẽ điền khi có. Định nghĩa chỉ số: xem paper/Methodology.md §3.8; hạn
> chế: §3.9.

Nguồn số đã có: `gold_seed/gold_seed_labels.csv` (300 ảnh gold seed, phân tầng 60
ảnh/tác vụ), `labels/validation/gold_seed_report.csv` (độ tin từng LF), classifier bệnh
dùng chung `labels/disease_clf/oof_predictions.csv`, và nhãn hợp nhất
`labels/fused/usability_labels.csv`. LF7 (vision) **không đưa vào bản này** do lần chạy
diện rộng chưa hoàn tất; đánh giá LF7 để lại cho phiên bản sau.

## 5.1. Chất lượng nhãn yếu trên gold seed

Bảng 5.1 báo cáo độ tin từng LF trên gold seed. κ = Cohen's kappa (mức đồng thuận vượt
ngẫu nhiên; κ = 0: ngang đoán theo lớp đa số; κ < 0: dưới mức ngẫu nhiên; **n/a**: cả
nhãn người lẫn phiếu LF đều là hằng số nên κ không xác định). α̂ = ước lượng độ chính xác;
coverage = tỷ lệ ảnh LF có bỏ phiếu.

**Bảng 5.1 — Độ tin từng LF trên gold seed (n = 60 ảnh/tác vụ; làm tròn 3 chữ số).**

| LF | Tác vụ | α̂ | κ | Coverage |
|----|--------|-----|-----|----------|
| LF1 maturity | 1_maturity_evaluation | 0.783 | −0.060 | 1.000 |
| LF2 foliar   | 2_foliar_disease      | 0.983 | 0.000 | 1.000 |
| LF3 trunk    | 3_trunk_disease       | 1.000 | n/a | 1.000 |
| LF4 crown    | 4_crown_disease       | 1.000 | n/a | 1.000 |
| LF5 petiole  | 5_petiole             | 1.000 | n/a | 1.000 |

Điều bảng 5.1 không tự nói: **cả bốn LF correctness cho tác vụ bệnh (LF2–LF5) đều gần hoặc
hoàn toàn là hằng số "hữu dụng"**, nên không phân biệt được ảnh không phù hợp. Nguyên nhân
là nền gold seed lệch rất mạnh về lớp hữu dụng: trong 60 ảnh native mỗi tác vụ, tỷ lệ ảnh
người gán là hữu dụng là 96,7% (1_maturity), 98,3% (2_foliar) và **100%** ở 3_trunk /
4_crown / 5_petiole. Với LF3/LF4/LF5, cả nhãn người lẫn phiếu LF đều bằng 1 trên toàn phần
chồng lấn → α̂ = 1.000 nhưng κ **không xác định** (không có phương sai để đánh giá). LF2
tương tự ở mức κ = 0.000 (phiếu 1 gần như tuyệt đối, precision = 0.983 = tỷ lệ lớp đa số).
Chỉ LF1 có phương sai phiếu, nhưng κ = −0.060 (< 0): các phiếu sai rơi vào lớp thiểu số
"không hữu dụng", nên xét theo κ, LF1 cũng chưa mang thông tin phân biệt trên gold seed hiện
tại.

Hệ quả: các LF correctness (LF1–LF5) chủ yếu cung cấp **mỏ neo dương** ("ảnh nguồn sạch là
hữu dụng"), không cung cấp tín hiệu "không phù hợp". Đây đúng là rủi ro đã nêu ở
paper/Methodology.md §3.9 (cổng go/no-go chỉ dựa `α̂ > ½` có thể giữ lại một LF gần-hằng-số)
và cho thấy tín hiệu phân biệt phải đến từ LF6 (suy giảm có kiểm soát) — hiện `[CHỜ SỐ]`.
Định nghĩa/vai trò từng LF: xem docs/LF1_Methodology.md … docs/LF6_Methodology.md.

Classifier bệnh dùng chung (nguồn của LF2–LF5) đạt **độ chính xác out-of-fold 0.9934**
(đúng lớp) và **0.9998** ở mức view (đúng bộ phận), trên 5.798 ảnh bệnh, cross-fit K = 5.
Chính độ chính xác gần bão hòa này giải thích vì sao correctness ở mức view suy biến thành
hằng số dương trên ảnh nguồn sạch.

## 5.2. Nhãn hợp nhất so với gold seed

Nhãn hợp nhất (`fusion_label_model`, biểu quyết có trọng số trên các phiếu LF1–LF5) phủ
6.726 cặp (ảnh, tác vụ). Bảng 5.2 đối chiếu với gold seed: nhãn hợp nhất **thừa hưởng đúng
lệch base-rate** của các LF nguồn — accuracy cao nhưng κ ≤ 0 hoặc không xác định, xác nhận
tín hiệu phân biệt chưa hình thành khi chưa có LF6.

**Bảng 5.2 — Nhãn hợp nhất so với gold seed (làm tròn 3 chữ số; n_overlap = 60/tác vụ).**

| Tác vụ | #nhãn hợp nhất | Accuracy vs gold | κ vs gold |
|--------|---------------:|------------------|-----------|
| 1_maturity_evaluation | 942  | 0.783 | −0.060 |
| 2_foliar_disease      | 3794 | 0.983 | 0.000 |
| 3_trunk_disease       | 1006 | 1.000 | n/a |
| 4_crown_disease       | 470  | 1.000 | n/a |
| 5_petiole             | 514  | 1.000 | n/a |

Hai tác vụ ít ảnh nguồn nhất — 4_crown (Bud Rot, 470) và 5_petiole (Bud Root Dropping,
514; xem paper/Experimental_Setup.md §4.1) — có độ phủ nhãn thấp nhất.

## 5.3. Hiệu năng mô hình IQA trên gold seed

Mô hình IQA đa nhãn (`train_iqa`) chưa chạy; các Bảng 5.3a–5.3b để `[CHỜ SỐ]`. macro-F1 =
trung bình F1 năm tác vụ; micro-F1 = F1 gộp toàn bộ quyết định nhãn; subset-accuracy = tỷ
lệ ảnh đúng đồng thời cả năm nhãn; Hamming-loss = tỷ lệ nhãn đơn lẻ sai. Theo hướng vận
hành (§3.8), chỉ số cần đọc trước là **recall của lớp "không phù hợp"** mỗi tác vụ, vì bỏ
sót một ảnh kém tốn kém hơn yêu cầu chụp lại; sẽ tách riêng khi có output.

**Bảng 5.3a — Hiệu năng mô hình IQA trên gold seed, theo tác vụ.**

| Tác vụ | Precision | Recall | F1 | AUC |
|--------|-----------|--------|-----|-----|
| 1_maturity_evaluation | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 2_foliar_disease      | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 3_trunk_disease       | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 4_crown_disease       | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 5_petiole             | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |

**Bảng 5.3b — Tổng hợp cấp vector nhãn.**

| macro-F1 | micro-F1 | subset-accuracy | Hamming-loss |
|----------|----------|-----------------|--------------|
| [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ]        | [CHỜ SỐ]     |

**Bảng 5.3c — Classifier bệnh dùng chung (out-of-fold, K = 5, 5.798 ảnh bệnh).**

| Chỉ số | Giá trị |
|--------|---------|
| Accuracy đúng-lớp (5 lớp bệnh) | 0.9934 |
| Accuracy đúng-view (4 required-view) | 0.9998 |

F1 theo từng nguồn ảnh (phát hiện *shortcut learning*) chỉ đo được sau khi có mô hình IQA;
để `[CHỜ SỐ]`. Vì nhãn tương quan chặt với nguồn (mỗi nguồn ánh xạ gần 1–1 với một tác vụ,
§4.1), recall lớp "không phù hợp" thấp sẽ là dấu hiệu mô hình học nguồn thay vì chất lượng.

## 5.4. Kích thước đầu vào và triển khai

Quét kích thước đầu vào chưa chạy; Bảng 5.4 để `[CHỜ SỐ]`. Định vị "nhẹ / chạy tại biên"
chỉ được khẳng định bằng số latency (ms/ảnh) và kích thước sau lượng tử hóa INT8 (MB) đo
trên thiết bị đại diện, không bằng nhận định định tính.

**Bảng 5.4 — Đánh đổi kích thước đầu vào và triển khai.**

| Input size | macro-F1 | Params (M) | Latency (ms) | Kích thước INT8 (MB) |
|-----------|----------|------------|--------------|----------------------|
| 224 | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 320 | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 384 | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |

## 5.5. Thảo luận

**Trạng thái tín hiệu theo tác vụ.** Với số hiện có, các LF correctness (LF1–LF5) đều không
phân biệt được lớp "không phù hợp" trên gold seed: LF3/LF4/LF5 là hằng số dương (κ không
xác định), LF2 gần hằng số (κ = 0), LF1 có phương sai nhưng κ = −0.060. Nguyên nhân gốc là
**classifier bệnh dùng chung đạt độ chính xác view gần 1.0**, nên trên ảnh nguồn sạch "đọc
đúng view" gần như luôn đúng — correctness suy biến thành nhãn dương. Điều này nhất quán với
định nghĩa usability của đề tài (§4.2): usability = *required-view hiện đủ rõ để đánh giá, kể
cả kết luận khỏe*, không phải *có triệu chứng bệnh*; trên ảnh dataset đã cận cảnh, view gần
như luôn rõ.

**Hệ quả cho thiết kế.** Tín hiệu phân biệt chất lượng (ảnh mờ/khuất/thiếu view → không phù
hợp) **không** đến từ correctness trên ảnh sạch mà phải từ **LF6 (suy giảm có kiểm soát)** —
làm hỏng dần ảnh anchor tới điểm gãy để sinh phiếu âm. LF6 vì thế là trụ của tín hiệu âm và
là bước kế tiếp bắt buộc trước khi huấn luyện mô hình IQA cuối; hiện `[CHỜ SỐ]`. Bổ sung ảnh
*không hữu dụng* vào gold seed (hiện tỷ lệ dương native 96,7–100%) cũng cần thiết để κ có ý
nghĩa.

**Đối chiếu khoảng trống kép và mục tiêu hiện trường.** Đóng góp nhắm vào hai khoảng trống
đồng thời (paper/Methodology.md §3.1, Related Work): (i) IQA hướng-tác-vụ cho ảnh dừa chưa
được giải quyết; (ii) mô hình phân tích dừa hiện có không kèm tiền kiểm chất lượng, còn IQA
nhẹ tổng quát lại không xét *tính phù hợp theo tác vụ*. Giá trị vận hành — phản hồi tức thời
tại hiện trường để chụp lại ngay — chỉ được chứng minh bằng số latency/kích thước ở Bảng 5.4
(hiện `[CHỜ SỐ]`).

**Giới hạn (nhất quán §3.9).** Kết quả hiện tại giới hạn ở khâu **chất lượng nhãn yếu**: gold
seed 300 ảnh lệch mạnh về lớp hữu dụng (không có ảnh không-phù-hợp cho ba tác vụ bệnh); các
LF correctness chỉ tạo nhãn dương; LF6, mô hình IQA cuối và quét kích thước đầu vào chưa
chạy; LF7 (vision) chưa đưa vào. Nhãn là proxy sinh theo quy tắc và đặc thù theo mô hình hạ
nguồn; dữ liệu là ảnh dataset đã chuẩn hóa, lệch phân phối so với ảnh điện thoại ngoài đồng.
Biện pháp giảm thiểu và hướng phát triển: xem paper/Methodology.md §3.9.
