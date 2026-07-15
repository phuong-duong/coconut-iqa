# Kế hoạch gán nhãn & triển khai — Coconut task-driven IQA

## 0. Bộ nhãn (đã chốt — 5 tác vụ, phân theo required-view)

| Mã | Tác vụ | Ảnh phải thể hiện | Ground-truth |
|----|--------|-------------------|--------------|
| `1_maturity_evaluation` | Độ chín | Cận cảnh **trái** | Mức chín `dry`/`green`/`tender` từng trái (Roboflow) |
| `2_foliar_disease` | Bệnh trên lá | Cận cảnh **lá** | Gray Leaf Spot, Leaf Rot |
| `3_trunk_disease` | Bệnh thân | Bề mặt **thân** | Stem Bleeding |
| `4_crown_disease` | Bệnh đọt/crown | **Đỉnh đọt**, nhìn từ trên xuống | Bud Rot |
| `5_petiole` | Tình trạng tàu lá (sàng lọc bệnh rễ/rụng chồi) | **Cuống lá / độ rủ** | Bud Root Dropping |

Mỗi ảnh có GT cho **đúng một tác vụ** theo nguồn của nó. Một bộ tiền kiểm chất lượng nhẹ có thể chạy trước mô hình để báo chụp lại với ảnh quá kém.

## 1. Bảng Labeling Functions (LF)

Mỗi LF bỏ phiếu cho từng tác vụ: `1` (hữu dụng), `0` (không), hoặc **abstain** (bỏ qua khi không chắc). Label model hợp nhất các phiếu thành nhãn xác suất. Độ tin xếp giảm dần LF1→LF10.

| LF | Tín hiệu | Bỏ phiếu cho tác vụ | Quy tắc `1` / `0` | Khi ABSTAIN | Độ tin |
|----|----------|---------------------|-------------------|-------------|--------|
| LF1 `correct_maturity` | Model độ chín vs nhãn `dry/green/tender` | `1_maturity` | đọc đúng mức chín → 1; sai → 0 | ảnh không có nhãn mức chín | **Cao** |
| LF2 `correct_foliar` | Model bệnh-lá vs lớp GT | `2_foliar` | chẩn đúng → 1; sai → 0 | ảnh không có GT lớp lá | **Cao** |
| LF3 `correct_trunk` | Model bệnh-thân vs lớp GT | `3_trunk` | chẩn đúng → 1; sai → 0 | ảnh không có GT lớp thân | **Cao** |
| LF4 `correct_crown` | Model bệnh-đọt vs lớp GT | `4_crown` | chẩn đúng → 1; sai → 0 | ảnh không có GT lớp đọt | **Cao** |
| LF5 `correct_petiole` | Model tình-trạng-tàu-lá vs lớp GT | `5_petiole` | chẩn đúng → 1; sai → 0 | ảnh không có GT lớp này | **Cao** |
| LF6 `degrade_boundary` | Suy giảm có kiểm soát → điểm gãy | mọi tác vụ | còn dưới ngưỡng gãy → 1; vượt → 0 | trục không liên quan tác vụ | **Cao** (nhân quả) |
| LF7 `vision_model` | Model thị giác chấm suitable+confidence (notebook pilot) | mọi tác vụ | conf≥τ_high → 1; conf≤τ_low → 0 | τ_low<conf<τ_high | Trung bình |
| LF8 `folder_native` | Thư mục gốc → nhãn kỳ vọng | tác vụ tương ứng thư mục | khớp thư mục → 1 | tác vụ khác thư mục | Trung bình |
| LF9 `conf_calibrated`/OOD | Confidence đã calibrate / Mahalanobis, energy | tác vụ correctness thưa | in-distribution → 1; OOD → 0 | đã có correctness rõ | Trung bình |
| LF10 `tta_agreement` | Nhất quán qua nhiều augment | mọi tác vụ | nhất quán cao → 1; phân tán → 0 | phương sai trung gian | Thấp–TB |

**Cạm bẫy tương quan:** LF6 (degrade-mờ) và bất kỳ heuristic mờ nào cùng nhìn một tín hiệu → để label model mô hình hóa tương quan, đừng coi độc lập.

**Output — mỗi LF một file riêng:** mỗi LF ghi `labels/votes/lf<N>_<tên>.csv` theo schema chung (`src/utils/lf_io.ipynb`, long/tidy: `lf, image_id, task, vote, confidence, reason, source, path` + cột extra tuỳ LF). KHÔNG dùng chung một manifest → chạy nhiều LF song song không tranh chấp file. Abstain = bỏ dòng. Bước label model đọc mọi file bằng `fuse_votes(labels/votes)` để dựng ma trận `(image_id, task) × lf`.

## 2. Kế hoạch triển khai (theo thứ tự ưu tiên)

**Giai đoạn A — Nền (bắt buộc, không bỏ)**
1. **Gold seed**: chọn ngẫu nhiên phân tầng ~300–500 ảnh, người gán độ hữu dụng thật cho 5 tác vụ. Đây là đòn bẩy cao nhất — không có nó, mọi nhãn tự động đều không kiểm chứng được.
2. **LF1–LF5 (correctness)**: tích hợp 5 mô hình hạ nguồn (độ-chín / bệnh-lá / bệnh-thân / bệnh-đọt / tàu-lá) vào `notebooks/lf1-5_correctness.ipynb`. Đã có sẵn phần đọc GT (kể cả nhãn mức chín `dry/green/tender`) + logic; chỉ cần bổ sung hàm suy luận của mô hình.

**Giai đoạn B — Trụ bổ sung**
3. **LF6 (degradation)**: dựng bộ suy giảm có kiểm soát trên ảnh anchor (ảnh model làm đúng), dò điểm gãy cho từng tác vụ × từng trục.
4. **LF phụ khác**: vision LF (LF7), TTA, OOD... bổ sung nơi correctness thưa (vd tác vụ chéo — ảnh bệnh có dùng được cho độ chín không).

**Giai đoạn C — Hợp nhất & huấn luyện**
5. **Label model**: gộp mọi LF (Snorkel hoặc biểu quyết-có-trọng-số nếu gọn), calibrate theo gold seed, xuất nhãn xác suất.
6. **Group split** 70/15/15 theo ảnh gốc (gộp ×3 augment Roboflow cùng tập).
7. **Huấn luyện** backbone nhẹ (MobileNetV3/EfficientNet-Lite), 5 sigmoid heads, BCE có trọng số lớp; dò kích thước đầu vào (224/320/384).
8. **Đánh giá** trên gold seed; báo cáo macro/micro-F1, AUC, per-source; hiệu chỉnh ngưỡng τ_k theo F1.

**Giai đoạn D — Triển khai**
9. Nén INT8 → TFLite/ONNX Mobile; đo latency + size; dựng đường cong accuracy–latency.

## 3. Ước lượng công sức

| Việc | Công sức | Ghi chú |
|------|----------|---------|
| Gold seed (300–500 ảnh) | 1–2 ngày người gán | Việc thủ công chính, làm 1 lần |
| Tích hợp LF1–5 vào notebook | Thấp | Notebook đã sẵn; cần 5 mô hình hạ nguồn đủ tốt |
| Degradation (LF6) | Trung bình | Viết bộ biến đổi + vòng dò điểm gãy |
| Label model + fusion | Trung bình | Snorkel hoặc trọng số đơn giản |
| Dò kích thước đầu vào | ~3× compute train | Compute nền, ít công thủ công |

## 4. Việc cần bạn quyết / chuẩn bị

- Đã có sẵn 5 model hạ nguồn (độ-chín, bệnh-lá, bệnh-thân, bệnh-đọt, tàu-lá) chưa? Nếu chưa, cần huấn luyện/tải trước khi LF1–5 chạy được. Model độ chín có thể train ngay trên nhãn `dry/green/tender` của bộ Roboflow.
- Các lớp bệnh nhỏ (Bud Rot 470, Bud Root Dropping 514) → cân nhắc tăng cường/điều chỉnh khi huấn luyện model hạ nguồn tương ứng.
- `5_petiole` là tín hiệu **kém đặc hiệu** (tàu lá suy tàn do nhiều nguyên nhân) → phù hợp sàng lọc bước đầu; ghi rõ giới hạn này khi báo cáo.

## 5. Hạn chế đã biết → Future Work

- **Prompt của LF7 (vision) được tinh chỉnh thủ công và RẤT nhạy cảm với cách diễn đạt required-view.** Qua nhiều vòng pilot, chỉ đổi câu chữ mô tả góc nhìn (nhất là tác vụ `5_petiole`) đã làm thay đổi đáng kể phiếu của model — ví dụ "toàn cây" quá rộng, "trọn một tàu lá từ gốc đến chóp" quá hẹp, "bẹ/chỗ bám vào thân" lại dễ nhầm với đọt. Bản prompt hiện tại đã hợp lý nhưng **chưa được tối ưu một cách hệ thống**. Hướng cải thiện (đưa vào Future Work của paper): (i) tối ưu/chuẩn hóa prompt có kiểm chứng — dò nhiều biến thể và đo trên gold seed thay vì tinh chỉnh cảm tính; (ii) dùng few-shot kèm ảnh ví dụ cho từng required-view; (iii) hiệu chỉnh ngưỡng `τ` của LF7 theo gold seed.
