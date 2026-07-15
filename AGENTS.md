# AGENTS.md — Coconut Task-Oriented IQA

> File ngữ cảnh cho AI coding tool (Claude Code, Cursor, ...). Đọc trước khi implement.
> Nếu tool của bạn dùng `CLAUDE.md`, có thể symlink/đổi tên file này.
> Ngôn ngữ dự án: tiếng Việt (thuật ngữ kỹ thuật giữ tiếng Anh).

## 1. Mục tiêu

Bài báo khoa học về **task-oriented Image Quality Assessment (IQA)** cho ảnh chụp cây/trái dừa.
Tags: IQA, multi-label classification, smart agriculture.

Xác định một tấm ảnh có **hữu dụng** cho một tác vụ phân tích cụ thể phía sau hay không, nhằm
**phản hồi tức thời cho người nông dân tại hiện trường**: ảnh không đạt → báo chụp lại ngay, tránh
mang ảnh vô dụng về phòng lab rồi phải ra đồng chụp lại. Mô hình chạy **trên thiết bị di động / edge**
nên phải nhẹ.

"Hữu dụng" định nghĩa theo **sự thành công của tác vụ hạ nguồn** (task-driven), không phải chất lượng
thẩm mỹ chung.

## 2. Bài toán & bộ nhãn

Phân loại **đa nhãn (multi-label)**: mỗi ảnh → vector 5 chiều, mỗi chiều một **sigmoid độc lập**
(không dùng softmax). Nhãn thật `y_k ∈ {0,1}`. Một ảnh có thể phù hợp cho nhiều, một, hoặc không
tác vụ nào.

| Mã | Tác vụ | Ground-truth |
|----|--------|--------------|
| `1_maturity_evaluation` | Đánh giá độ chín | Nhãn mức chín `dry`/`green`/`tender` từng trái (bộ Roboflow) |
| `2_foliar_disease` | Chẩn bệnh trên lá (cận cảnh lá) | Gray Leaf Spot, Leaf Rot |
| `3_trunk_disease` | Chẩn bệnh thân (bề mặt thân) | Stem Bleeding |
| `4_crown_disease` | Chẩn bệnh đọt/crown (đỉnh đọt, nhìn từ trên xuống) | Bud Rot |
| `5_petiole` | Đánh giá tình trạng tàu lá (sàng lọc bệnh rễ/rụng chồi) | Bud Root Dropping |

Các tác vụ phân theo *required-view* — ảnh phải thể hiện đúng đối tượng/góc nhìn (trái / lá / thân / đọt nhìn từ trên xuống / cuống lá + độ rủ).

Ngưỡng quyết định `τ_k` mỗi tác vụ hiệu chỉnh trên tập kiểm định (tối đa hóa F1), không cố định 0.5.

## 3. Pipeline

Mô hình đa nhãn nhẹ (**MobileNetV3 / EfficientNet-Lite**, pretrained ImageNet, tinh chỉnh trên dữ
liệu dừa), backbone dùng chung cho 5 tác vụ (multi-task), đầu ra 5 sigmoid.

Để phục vụ mục tiêu phản hồi tức thời, có thể đặt một **bộ tiền kiểm chất lượng nhẹ** (đo mờ / phơi
sáng / độ phân giải) chạy trên thiết bị trước khi gọi mô hình: ảnh quá kém → báo chụp lại ngay.

Thiết kế đầy đủ: `paper/Methodology.md`.

## 4. Dữ liệu

Thư mục `Dataset/`:

- `Dataset/coconut-veirf-v5/` — bộ **Roboflow coconut v5** (`nit-calicut/coconut-veirf`, CC BY 4.0), định dạng
  YOLO, chia sẵn train/valid/test (**392 ảnh gốc → 948 ảnh** sau tăng cường ×3 ở tập train).
  **3 lớp = mức độ chín**: `data.yaml` → `names: ['dry','green','tender']` (class 0/1/2), gán cho từng
  trái. Đây chính là **ground-truth độ chín** (1232 box: tender 685, green 320, dry 227).
  ⚠️ Ảnh đã qua resize-stretch + auto-contrast + ×3 phơi sáng khi export → các bản augment của cùng
  một ảnh gốc PHẢI nằm cùng split (chống rò rỉ), và không dùng ảnh này để đánh giá tín hiệu chất lượng.
- `Dataset/Coconut Tree Disease Dataset/` — bộ bệnh (Mendeley `gh56wbsnj5`), 5 thư mục lớp:
  Gray Leaf Spot (2135), Leaf Rot (1673) → `2_foliar_disease`;
  Stem Bleeding (1006) → `3_trunk_disease`; Bud Rot (470) → `4_crown_disease`;
  Bud Root Dropping (514) → `5_petiole`.

Tổng ~6746 ảnh. Ground-truth cho cả 5 tác vụ đều có sẵn trong hai bộ trên (mỗi ảnh có GT cho đúng một tác vụ theo nguồn).

## 5. Chiến lược gán nhãn (task-driven)

Độ hữu dụng = tác vụ hạ nguồn thành công. Sinh nhãn bằng **weak-supervision fusion neo vào gold seed**:

- **Correctness vs ground-truth** (tín hiệu mạnh nhất): mô hình hạ nguồn dự đoán ĐÚNG trên ảnh → ảnh
  hữu dụng cho tác vụ đó. Cả 5 tác vụ đều có GT.
- **Suy giảm có kiểm soát (controlled degradation)**: làm hỏng dần ảnh tốt, dò mức mà tác vụ bắt đầu
  thất bại → sinh mẫu quanh ranh giới hữu dụng.
- **Vision LF / confidence đã calibrate / OOD / TTA**: bổ sung nơi correctness thưa.
- **Gold seed** (~300–500 ảnh người gán, phân tầng): calibrate label model, báo cáo Cohen's κ, và làm
  **tập kiểm thử vàng**. Đánh giá cuối cùng phải trên gold seed, không trên nhãn tự sinh.

Bảng labeling function + kế hoạch chi tiết: `docs/Labeling_Plan.md`.

## 6. Bản đồ file

```
paper/Methodology.md                   # Mục Phương pháp hoàn chỉnh — nguồn chân lý về thiết kế
docs/Labeling_Plan.md                  # Bảng LF + kế hoạch triển khai + ước lượng công sức (nội bộ, không thuộc paper)
src/utils/lf_io.ipynb                  # Module dùng chung: schema phiếu chuẩn + writer (make_vote, write_lf_votes, fuse_votes). Notebook LF nạp bằng %run
notebooks/lf1-5_correctness.ipynb      # LF1–5: scaffold correctness (placeholder), ghi mỗi tác vụ 1 file
notebooks/lf1_maturity_yolov8.ipynb    # LF1 bản thật (YOLOv8 + cross-fitting) -> labels/votes/lf1_maturity.csv
notebooks/lf6_degradation.ipynb        # LF6: suy giảm có kiểm soát -> labels/votes/lf6_degradation.csv
notebooks/lf7_vision_label.ipynb       # LF7: vision model + cổng chất lượng -> labels/votes/lf7_vision.csv
labels/votes/lf<N>_<tên>.csv           # MỖI LF một file riêng (long schema) -> chạy song song, fusion gộp bằng fuse_votes
Dataset/                               # Dữ liệu (xem mục 4)
```

**Output mỗi LF một file (không dùng chung manifest):** mỗi LF ghi `labels/votes/lf<N>_<tên>.csv` theo
schema chung (`src/utils/lf_io.ipynb`, long/tidy: `lf, image_id, task, vote, confidence, reason, source, path` + cột extra).
Nhờ vậy chạy nhiều LF song song không tranh chấp file; bước fusion đọc mọi file bằng `fuse_votes(labels/votes)`.

## 7. Lộ trình triển khai (thứ tự ưu tiên)

1. **Gold seed**: gán tay ~300–500 ảnh cho 5 tác vụ + viết annotation protocol. (Đòn bẩy cao nhất.)
2. **Huấn luyện & tích hợp 5 mô hình hạ nguồn** (độ-chín trên `dry/green/tender`; bệnh-lá; bệnh-thân; bệnh-đọt; tàu-lá) vào
   `DownstreamModels` trong `notebooks/lf1-5_correctness.ipynb` (xem mục 8).
3. **Degradation LF**: bộ suy giảm có kiểm soát + dò điểm gãy cho từng tác vụ × từng trục.
4. **Label model** (Snorkel hoặc biểu quyết có trọng số) hợp nhất các LF → nhãn xác suất; calibrate theo gold seed.
5. **Split 70/15/15 group theo ảnh gốc** (gộp ×3 augment cùng split).
6. **Train mô hình IQA** nhẹ, 5 sigmoid heads, BCE có trọng số lớp; **dò kích thước đầu vào** (224/320/384) như siêu tham số.
7. **Đánh giá** trên gold seed: macro/micro-F1, AUC, per-source; hiệu chỉnh `τ_k` theo F1.
8. **Nén** INT8 → TFLite/ONNX Mobile; đo latency + size; dựng đường cong accuracy–latency.

## 8. Cách chạy & mở rộng

Mở `notebooks/lf1-5_correctness.ipynb` và chạy tuần tự các cell. Khi mô hình hạ nguồn chưa được
tích hợp (còn là hàm giữ chỗ), mọi phiếu là abstain → các file `labels/votes/lf2_foliar.csv`… chỉ có dòng tiêu đề.

Tích hợp mô hình hạ nguồn thực (sửa cell tạo `DownstreamModels` ở cuối notebook):
```python
models = DownstreamModels(
    predict_maturity  = lambda p: my_maturity_clf.predict(p),   # 'dry'/'green'/'tender'
    predict_foliar    = lambda p: my_foliar_clf.predict(p),     # bool
    predict_trunk     = lambda p: my_trunk_clf.predict(p),      # bool
    predict_crown     = lambda p: my_crown_clf.predict(p),      # bool
    predict_petiole = lambda p: my_petiole_clf.predict(p),  # bool
)
```
Logic correctness: `maturity_correct` (đúng nếu mức dự đoán ∈ tập mức thật của ảnh),
`cls_correct` (đúng lớp bệnh → hữu dụng). Mỗi ảnh bệnh chỉ gán tác vụ gốc (nơi có GT); tác vụ khác để trống (abstain).

## 9. Nguyên tắc không được vi phạm

- Multi-label: mỗi nhãn một sigmoid độc lập, **không softmax**.
- Hữu dụng = thấy rõ đối tượng đủ để **đánh giá** (kể cả kết luận khỏe mạnh), KHÔNG đòi triệu chứng bệnh.
- **Group-split theo ảnh gốc** — bộ Roboflow có ×3 bản augment, dễ rò rỉ train/test.
- Nhãn là **proxy** → xác thực bằng gold seed người gán (κ); đánh giá cuối trên gold seed, không trên nhãn tự sinh.
- Báo cáo hiệu năng **per-source** để phát hiện shortcut (model học phân biệt nguồn thay vì độ hữu dụng).
- Thư mục đồng bộ đám mây: file có thể bị "evict" khỏi đĩa; nếu lệnh CLI báo không thấy file, mở/đọc nó trước để tải về.

## 10. Tham khảo dữ liệu

- [1] Roboflow Universe `nit-calicut/coconut-veirf` (v5, CC BY 4.0) — https://universe.roboflow.com/nit-calicut/coconut-veirf
- [2] Coconut Tree Disease Dataset, Mendeley Data — https://data.mendeley.com/datasets/gh56wbsnj5/1

## 11. Bảng thuật ngữ

Giải thích ngắn cho các thuật ngữ dùng trong repo này.

| Thuật ngữ | Giải thích ngắn |
|-----------|-----------------|
| IQA (Image Quality Assessment) | Đánh giá chất lượng ảnh. Ở đây là "ảnh có dùng được cho tác vụ hạ nguồn không", không phải đẹp/xấu. |
| Task-oriented / task-driven | Định nghĩa "hữu dụng" theo việc **tác vụ phía sau có thành công không**, thay vì theo cảm quan. |
| Tác vụ hạ nguồn (downstream task) | Việc phân tích thực sự dùng ảnh: ở đây là đánh giá độ chín, chẩn bệnh lá, chẩn bệnh thân/ngọn. |
| Multi-label (đa nhãn) | Một ảnh có thể mang **nhiều nhãn cùng lúc** (phù hợp cho nhiều tác vụ), khác với chỉ chọn 1 lớp. |
| Sigmoid | Hàm cho mỗi nhãn một xác suất 0–1 **độc lập**. Dùng cho đa nhãn. |
| Softmax | Hàm bắt các lớp **cạnh tranh** nhau (tổng = 1), chỉ hợp khi mỗi ảnh đúng 1 lớp → KHÔNG dùng ở đây. |
| Ground-truth (GT) | "Đáp án đúng" của ảnh do con người/dataset gán sẵn (vd nhãn `dry/green/tender`, lớp bệnh). |
| Correctness | Cách gán nhãn: cho model hạ nguồn chạy, nếu nó dự đoán **đúng** so với GT thì ảnh được coi là hữu dụng. |
| Weak supervision | Gán nhãn tự động bằng nhiều tín hiệu "yếu" (không hoàn hảo) thay vì gán tay toàn bộ. |
| Labeling function (LF) | Một quy tắc yếu bỏ phiếu nhãn cho ảnh; có thể "abstain" (bỏ qua) khi không chắc. |
| Label model | Thuật toán **hợp nhất** phiếu của nhiều LF thành một nhãn xác suất, tự học độ tin của từng LF. |
| Gold seed | Tập nhỏ (~300–500) ảnh **người gán tay chuẩn**, dùng để kiểm chứng nhãn tự động và làm tập test. |
| Cohen's κ (kappa) | Chỉ số đo mức **đồng thuận** giữa hai người/nguồn gán nhãn (1 = trùng khớp hoàn toàn). |
| Controlled degradation | Chủ động làm hỏng ảnh tốt (mờ, tối, giảm nét...) để tìm ngưỡng mà tác vụ bắt đầu thất bại. |
| OOD (out-of-distribution) | Ảnh "lạ", nằm ngoài phân phối dữ liệu model từng thấy → model dễ sai. |
| TTA (test-time augmentation) | Chạy model trên nhiều biến thể của cùng ảnh; nhất quán cao = đáng tin. |
| Calibration | Hiệu chỉnh để **điểm tin cậy** của model phản ánh đúng xác suất thật (model hay "tự tin nhưng sai"). |
| Backbone | Phần mạng trích đặc trưng chính (vd MobileNetV3, EfficientNet-Lite). |
| MobileNet / EfficientNet-Lite | Các mạng CNN **nhẹ**, thiết kế cho điện thoại/thiết bị biên. |
| Transfer learning / pretrained | Khởi tạo model bằng trọng số đã học trên ImageNet rồi tinh chỉnh cho dữ liệu dừa. |
| Multi-task learning | Một backbone dùng chung cho nhiều tác vụ → nhẹ hơn nhiều model riêng. |
| BCE (binary cross-entropy) | Hàm mất mát cho bài toán nhị phân/đa nhãn (mỗi nhãn 0/1). |
| Class weight (trọng số lớp) | Nhân trọng số để bù **mất cân bằng** (lớp ít mẫu được coi trọng hơn khi huấn luyện). |
| Ngưỡng τ_k (threshold) | Mức xác suất để chốt nhãn = 1 cho tác vụ k; hiệu chỉnh theo F1 thay vì cố định 0.5. |
| F1 (macro / micro) | Chỉ số cân bằng precision & recall. Macro = trung bình đều các tác vụ; micro = gộp toàn bộ. |
| AUC-ROC | Đo khả năng phân biệt của model, không phụ thuộc ngưỡng. |
| Subset accuracy | Tỉ lệ ảnh dự đoán đúng **đồng thời cả 5 nhãn**. |
| Hamming loss | Tỉ lệ nhãn (từng ô) bị dự đoán sai trên toàn bộ vector nhãn. |
| Data leakage (rò rỉ) | Thông tin từ tập test lọt vào train → điểm số ảo. Ở đây do ×3 bản augment cùng ảnh gốc. |
| Group split | Chia train/val/test theo **ảnh gốc** để mọi biến thể của một ảnh nằm cùng một tập (chống rò rỉ). |
| Stratified (phân tầng) | Chia dữ liệu sao cho tỉ lệ nhãn/nguồn cân bằng giữa các tập. |
| Data augmentation | Tạo biến thể ảnh (lật, xoay, đổi sáng...) để tăng đa dạng khi huấn luyện. |
| Quantization INT8 | Nén model về số nguyên 8-bit → nhỏ & nhanh hơn, hợp thiết bị di động. |
| TFLite / ONNX Runtime Mobile | Định dạng/khung chạy model suy luận trên điện thoại. |
| Edge / on-device inference | Chạy model **ngay trên thiết bị** (không cần gửi lên server). |
| YOLO format / bounding box | Định dạng nhãn phát hiện đối tượng: mỗi dòng = 1 khung + lớp của một trái. |
| Per-source | Báo cáo hiệu năng **theo từng nguồn dữ liệu** để phát hiện model "học tủ" theo nguồn. |
| Shortcut learning | Model học đặc điểm ăn may (vd nhận ra nguồn ảnh) thay vì thứ ta thực sự muốn. |
