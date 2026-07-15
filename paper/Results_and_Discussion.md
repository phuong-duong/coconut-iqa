# 5. Kết quả và thảo luận (Results and Discussion)

> Quy ước số liệu: chỉ dùng số thật từ pipeline đã chạy. Ô `[CHỜ SỐ]` là chỉ số
> thuộc bước chưa chạy hoặc chưa sinh output (mô hình nhãn hợp nhất, mô hình IQA,
> quét kích thước đầu vào, classifier bệnh dùng chung, điểm gãy LF6), sẽ điền sau
> khi hoàn tất. Định nghĩa các chỉ số: xem paper/Methodology.md §3.8; danh sách bước
> còn thiếu: xem paper/Experimental_Setup.md ("Ghi chú — cần bổ sung").

Nguồn số hiện có: `gold_seed/gold_seed_labels.csv` (300 ảnh gold seed, phân tầng 60
ảnh/tác vụ) và `labels/validation/gold_seed_report.csv` (độ tin từng LF neo trên gold
seed). Các nguồn còn lại (`fusion_label_model`, `train_iqa`,
`labels/disease_clf/oof_predictions.csv`) chưa sinh số.

## 5.1. Chất lượng nhãn yếu trên gold seed

Bảng 5.1 báo cáo độ tin từng LF trên gold seed. κ = Cohen's kappa, mức đồng thuận
vượt mức ngẫu nhiên (κ = 0: chỉ ngang đoán mò; κ < 0: dưới mức ngẫu nhiên); α̂ = ước
lượng độ chính xác của LF; coverage = tỷ lệ ảnh LF có bỏ phiếu.

**Bảng 5.1 — Độ tin từng LF trên gold seed (n = 60 ảnh/tác vụ; α̂, κ, coverage làm tròn 3 chữ số).**

| LF | Tác vụ | α̂ | κ | Coverage |
|----|--------|-----|-----|----------|
| LF1 maturity | 1_maturity_evaluation | 0.783 | −0.060 | 1.000 |
| LF2 foliar   | 2_foliar_disease      | 0.983 | 0.000 | 1.000 |
| LF3 trunk    | 3_trunk_disease       | n/a (0 phiếu) | n/a (0 phiếu) | 0.000 |
| LF4 crown    | 4_crown_disease       | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| LF5 petiole  | 5_petiole             | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| LF7 vision — 1_maturity_evaluation | 1_maturity_evaluation | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| LF7 vision — 2_foliar_disease | 2_foliar_disease | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| LF7 vision — 3_trunk_disease | 3_trunk_disease | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| LF7 vision — 4_crown_disease | 4_crown_disease | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| LF7 vision — 5_petiole | 5_petiole | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |

Điều bảng 5.1 không tự nói: α̂ cao đi cùng κ ≤ 0 ở cả hai LF có phiếu là hệ quả của
lệch lớp trên gold seed. Trong 60 ảnh gold seed của mỗi tác vụ, tỷ lệ ảnh hữu dụng là
96,7% (58/60) ở `1_maturity_evaluation` và 98,3% (59/60) ở `2_foliar_disease`; với nền
lệch như vậy, một LF gần như luôn bỏ phiếu "hữu dụng" vẫn đạt α̂ ≈ tỷ lệ lớp đa số.
LF2 rơi đúng trường hợp này: recall = 1.000 và precision = 0.983 (= tỷ lệ lớp đa số),
κ = 0.000 — LF2 là bộ phân loại gần-hằng-số, không phân biệt được ảnh không hữu dụng.
LF1 có κ = −0.060 (< 0) dù α̂ = 0.783: các phiếu sai của LF1 tập trung vào lớp thiểu số
"không hữu dụng", nên xét theo κ, LF1 không mang thông tin phân biệt trên gold seed
hiện tại. Cả hai LF vì thế **không được coi là đáng tin** dựa trên α̂ đơn lẻ; đây đúng
là rủi ro đã nêu ở paper/Methodology.md §3.9 (cổng go/no-go chỉ dựa `α̂ > ½` có thể giữ
lại một LF gần-hằng-số).

LF3 (trunk) không bỏ phiếu nào chồng lấn gold seed (coverage = 0.000, 0 phiếu) nên bị
loại theo `gold_seed_report.csv`; hiện `labels/votes/lf3_trunk.csv` chỉ có dòng tiêu đề.
LF4, LF5 và LF7 chưa được đối chiếu định lượng với gold seed. LF7 mới ở mức pilot 48 ảnh
(`labels/lf7_vision_pilot.csv`), chưa chạy diện rộng. LF6 (suy giảm có kiểm soát) không
nằm trong bảng này vì được kiểm định bằng đường cong suy giảm riêng; hiện
`labels/lf6_degradation_manifest.csv` mới có tiêu đề, điểm gãy δ\* mỗi trục: [CHỜ SỐ].
Định nghĩa/vai trò từng LF: xem docs/LF1_Methodology.md … docs/LF6_Methodology.md.

## 5.2. Nhãn hợp nhất so với gold seed

Mô hình nhãn hợp nhất (`fusion_label_model`) chưa chạy nên độ phủ và đồng thuận với
gold seed chưa có (Bảng 5.2). Điều kiện đầu vào cho hợp nhất hiện chưa đủ ở phía nguồn:
LF3 chưa sinh phiếu (§5.1), và LF4/LF5/LF7 chưa đối chiếu gold. Vì gold seed phân tầng
60 ảnh/tác vụ nhưng một ảnh có thể phù hợp nhiều tác vụ, số ảnh dương trên toàn 300 ảnh
gold seed lệch theo tác vụ: `1_maturity_evaluation` 62/300 (20,7%), `2_foliar_disease`
151/300 (50,3%), `3_trunk_disease` 71/300 (23,7%), `4_crown_disease` 69/300 (23,0%),
`5_petiole` 103/300 (34,3%). Hai tác vụ ít ảnh nguồn nhất — `4_crown_disease` (Bud Rot,
470 ảnh) và `5_petiole` (Bud Root Dropping, 514 ảnh; xem paper/Experimental_Setup.md
§4.1) — dự kiến có độ phủ nhãn hợp nhất thấp nhất sau khi chạy.

**Bảng 5.2 — Nhãn hợp nhất so với gold seed (Accuracy/κ làm tròn 3 chữ số).**

| Tác vụ | #ảnh có nhãn hợp nhất | Accuracy vs gold | κ vs gold |
|--------|----------------------|------------------|-----------|
| 1_maturity_evaluation | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 2_foliar_disease      | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 3_trunk_disease       | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 4_crown_disease       | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 5_petiole             | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |

## 5.3. Hiệu năng mô hình IQA trên gold seed

Mô hình IQA (`train_iqa`) chưa chạy; các bảng 5.3a–5.3c để `[CHỜ SỐ]`. macro-F1 =
trung bình F1 của năm tác vụ (mỗi tác vụ trọng số bằng nhau); micro-F1 = F1 gộp toàn bộ
quyết định nhãn; subset-accuracy = tỷ lệ ảnh đúng đồng thời cả năm nhãn; Hamming-loss =
tỷ lệ nhãn đơn lẻ bị dự đoán sai. Theo hướng vận hành (§3.8), chỉ số cần đọc trước là
**recall của lớp "không phù hợp"** mỗi tác vụ, vì bỏ sót một ảnh kém tốn kém hơn yêu
cầu chụp lại; chỉ số này sẽ được tách riêng khi có output.

**Bảng 5.3a — Hiệu năng mô hình IQA trên gold seed, theo tác vụ (F1/AUC làm tròn 3 chữ số).**

| Tác vụ | Precision | Recall | F1 | AUC |
|--------|-----------|--------|-----|-----|
| 1_maturity_evaluation | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 2_foliar_disease      | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 3_trunk_disease       | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 4_crown_disease       | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 5_petiole             | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |

**Bảng 5.3b — Tổng hợp cấp vector nhãn (làm tròn 3 chữ số).**

| macro-F1 | micro-F1 | subset-accuracy | Hamming-loss |
|----------|----------|-----------------|--------------|
| [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ]        | [CHỜ SỐ]     |

Bảng 5.3c báo cáo F1 theo từng nguồn ảnh để phát hiện *shortcut learning* — mô hình
phân biệt nguồn ảnh thay vì độ hữu dụng (§3.9). Vì nhãn tương quan chặt với nguồn (mỗi
nguồn ánh xạ gần như 1–1 với một tác vụ; xem §4.1), F1 per-source cao đồng đều nhưng
recall lớp "không phù hợp" thấp sẽ là dấu hiệu mô hình học nguồn thay vì chất lượng.

**Bảng 5.3c — F1 theo nguồn ảnh (phát hiện shortcut; F1 làm tròn 3 chữ số).**

| Nguồn ảnh | Tác vụ | F1 |
|-----------|--------|-----|
| coconut-veirf-v5 | 1_maturity_evaluation | [CHỜ SỐ] |
| Gray Leaf Spot   | 2_foliar_disease      | [CHỜ SỐ] |
| Leaf Rot         | 2_foliar_disease      | [CHỜ SỐ] |
| Stem Bleeding    | 3_trunk_disease       | [CHỜ SỐ] |
| Bud Rot          | 4_crown_disease       | [CHỜ SỐ] |
| Bud Root Dropping| 5_petiole             | [CHỜ SỐ] |

Classifier bệnh dùng chung (`labels/disease_clf/oof_predictions.csv`) đã gán fold
cross-fit K = 5 cho 5.798 ảnh bệnh nhưng cột dự đoán còn trống (0/5.798 dòng có
`pred_class`); accuracy out-of-fold và ma trận nhầm lẫn: [CHỜ SỐ].

## 5.4. Kích thước đầu vào và triển khai

Quét kích thước đầu vào chưa chạy; Bảng 5.4 để `[CHỜ SỐ]`. Định vị "nhẹ / chạy tại
biên" chỉ được khẳng định bằng số latency (ms/ảnh) và kích thước sau lượng tử hóa INT8
(MB) đo trên thiết bị di động đại diện, không bằng nhận định định tính. Đường cong đánh
đổi macro-F1 ↔ latency ↔ kích thước qua ba mức 224/320/384 và mức chênh do INT8 sẽ được
điền sau khi có output `train_iqa`.

**Bảng 5.4 — Đánh đổi kích thước đầu vào và triển khai (macro-F1 3 chữ số; latency ms/ảnh; kích thước MB).**

| Input size | macro-F1 | Params (M) | Latency (ms) | Kích thước INT8 (MB) |
|-----------|----------|------------|--------------|----------------------|
| 224 | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 320 | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |
| 384 | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] | [CHỜ SỐ] |

## 5.5. Thảo luận

**Theo tác vụ và vì sao.** Với số hiện có, chất lượng tín hiệu chia theo tác vụ như
sau. `2_foliar_disease` có LF2 phủ 1.000 nhưng κ = 0.000: LF2 gần-hằng-số dương, nên
tín hiệu phân biệt cho tác vụ này chưa đến từ LF2 mà phải dựa vào LF6/LF7. Nguyên nhân
là nền gold seed lệch 98,3% dương (§5.1), cộng với việc cả Gray Leaf Spot và Leaf Rot
cùng là ảnh lá cận cảnh rõ nét nên hầu hết đều hữu dụng cho tác vụ lá. `1_maturity_
evaluation` có LF1 phủ 1.000 nhưng κ = −0.060: LF1 (đọc đúng mức chín từ detector, xem
docs/LF1_Methodology.md) chưa phân biệt được ảnh không hữu dụng trên nền lệch 96,7%
dương. `3_trunk_disease` hiện không có tín hiệu LF3 (0 phiếu). `4_crown_disease` và
`5_petiole` là hai tác vụ ít ảnh nguồn nhất (Bud Rot 470, Bud Root Dropping 514; §4.1),
nên độ phủ nhãn dự kiến thấp nhất và phương sai ước lượng cao nhất. Riêng `5_petiole`
kém đặc hiệu do suy tàn tàu lá (rủ, vàng úa) đến từ nhiều nguyên nhân, phù hợp sàng lọc
bước đầu hơn chẩn xác (§3.9); usability ở đây là *thấy cuống lá/độ rủ đủ để đánh giá —
kể cả khi kết luận khỏe mạnh*, không phải *có triệu chứng bệnh* (§4.2).

**Hệ quả cho thiết kế nhãn.** Ba quan sát trên củng cố quyết định ở §3.9: không dựa cổng
đơn `α̂ > ½`, mà đọc kèm κ và baseline lớp đa số; bổ sung ảnh *không hữu dụng* vào gold
seed để cân bằng lớp âm (hiện tỷ lệ dương trong native-task là 96,7–100%); và dồn tín
hiệu phân biệt chủ lực vào LF6 (suy giảm có kiểm soát) thay vì correctness trên ảnh
nguồn sạch. Rủi ro shortcut theo nguồn (§3.9) chưa kiểm định được vì Bảng 5.3c còn
`[CHỜ SỐ]`; đây là phép thử bắt buộc trước khi kết luận mô hình học chất lượng.

**Đối chiếu khoảng trống kép và mục tiêu hiện trường.** Đóng góp nhắm vào hai khoảng
trống đồng thời (xem paper/Methodology.md §3.1 và Related Work): (i) IQA hướng-tác-vụ
cho ảnh dừa chưa được giải quyết; (ii) mô hình phân tích dừa hiện có không kèm bước tiền
kiểm chất lượng, còn IQA nhẹ tổng quát lại không xét *tính phù hợp theo tác vụ*. Giá trị
vận hành — phản hồi tức thời tại hiện trường để chụp lại ngay, tránh vòng lặp hiện
trường ↔ phòng thí nghiệm — chỉ được chứng minh khi có số latency/kích thước ở Bảng 5.4;
hiện `[CHỜ SỐ]`.

**Giới hạn (nhất quán §3.9).** Kết quả hiện tại giới hạn ở: gold seed 300 ảnh lệch mạnh
về lớp hữu dụng; hai trong năm LF (LF1, LF2) có κ ≤ 0; LF3 chưa sinh phiếu; LF4/LF5/LF7,
mô hình nhãn hợp nhất, mô hình IQA, classifier bệnh dùng chung và quét kích thước đầu
vào chưa chạy. Nhãn là proxy sinh theo quy tắc và đặc thù theo mô hình hạ nguồn; dữ liệu
là ảnh dataset đã chuẩn hóa, lệch phân phối so với ảnh điện thoại chụp ngoài đồng. Các
biện pháp giảm thiểu và hướng phát triển: xem paper/Methodology.md §3.9.
