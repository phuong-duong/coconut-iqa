# Kế hoạch gán nhãn & triển khai — Coconut task-driven IQA

## 0. Bộ nhãn (đã chốt — 3 tác vụ)

| Mã | Tác vụ | Ground-truth sẵn có |
|----|--------|----------------------|
| `1_maturity_evaluation` | Độ chín | Nhãn mức chín `dry`/`green`/`tender` từng trái (Roboflow) — **có** |
| `2_foliar_disease` | Bệnh trên lá | Gray Leaf Spot, Leaf Rot — **có** |
| `3_trunk_crown_disease` | Bệnh thân/ngọn | Stem Bleeding, Bud Rot, Bud Root Dropping — **có** |

Bộ Roboflow dùng cho tác vụ độ chín (nhãn `dry/green/tender`). Một bộ tiền kiểm chất lượng nhẹ có thể chạy trước mô hình để báo chụp lại với ảnh quá kém.

## 1. Bảng Labeling Functions (LF)

Mỗi LF bỏ phiếu cho từng tác vụ: `1` (hữu dụng), `0` (không), hoặc **abstain** (bỏ qua khi không chắc). Label model hợp nhất các phiếu thành nhãn xác suất.

| LF | Tín hiệu | Bỏ phiếu cho tác vụ | Quy tắc `1` / `0` | Khi ABSTAIN | Độ tin |
|----|----------|---------------------|-------------------|-------------|--------|
| LF1 `correct_maturity` | Model độ chín vs nhãn `dry/green/tender` | `1_maturity` | đọc đúng mức chín → 1; sai → 0 | ảnh không có nhãn mức chín | **Cao** |
| LF2 `correct_foliar` | Model bệnh-lá vs lớp GT | `2_foliar` | chẩn đúng lớp lá → 1; sai → 0 | ảnh không có GT lớp lá | **Cao** |
| LF3 `correct_trunk` | Model bệnh-thân vs lớp GT | `3_trunk_crown` | chẩn đúng lớp thân/ngọn → 1; sai → 0 | ảnh không có GT lớp thân | **Cao** |
| LF4 `degrade_boundary` | Suy giảm có kiểm soát → điểm gãy | mọi tác vụ | còn dưới ngưỡng gãy → 1; vượt → 0 | trục không liên quan tác vụ | **Cao** (nhân quả) |
| LF5 `vision_model` | Model thị giác chấm suitable+confidence (notebook pilot) | mọi tác vụ | conf≥τ_high → 1; conf≤τ_low → 0 | τ_low<conf<τ_high | Trung bình |
| LF6 `folder_native` | Thư mục gốc → nhãn kỳ vọng | tác vụ tương ứng thư mục | khớp thư mục → 1 | tác vụ khác thư mục | Trung bình |
| LF7 `conf_calibrated`/OOD | Confidence đã calibrate / Mahalanobis, energy | tác vụ correctness thưa | in-distribution → 1; OOD → 0 | đã có correctness rõ | Trung bình |
| LF8 `tta_agreement` | Nhất quán qua nhiều augment | mọi tác vụ | nhất quán cao → 1; phân tán → 0 | phương sai trung gian | Thấp–TB |

**Cạm bẫy tương quan:** LF4 (degrade-mờ) và bất kỳ heuristic mờ nào cùng nhìn một tín hiệu → để label model mô hình hóa tương quan, đừng coi độc lập.

## 2. Kế hoạch triển khai (theo thứ tự ưu tiên)

**Giai đoạn A — Nền (bắt buộc, không bỏ)**
1. **Gold seed**: chọn ngẫu nhiên phân tầng ~300–500 ảnh, người gán độ hữu dụng thật cho 3 tác vụ. Đây là đòn bẩy cao nhất — không có nó, mọi nhãn tự động đều không kiểm chứng được.
2. **LF1–LF3 (correctness)**: tích hợp 3 mô hình hạ nguồn (độ-chín / bệnh-lá / bệnh-thân) vào `notebooks/label_correctness.ipynb`. Đã có sẵn phần đọc GT (kể cả nhãn mức chín `dry/green/tender`) + logic; chỉ cần bổ sung hàm suy luận của mô hình.

**Giai đoạn B — Trụ bổ sung**
3. **LF4 (degradation)**: dựng bộ suy giảm có kiểm soát trên ảnh anchor (ảnh model làm đúng), dò điểm gãy cho từng tác vụ × từng trục.
4. **LF phụ khác**: vision LF, TTA, OOD... bổ sung nơi correctness thưa (vd độ chín ở ảnh nhiều trái, bệnh chéo lá/thân).

**Giai đoạn C — Hợp nhất & huấn luyện**
5. **Label model**: gộp mọi LF (Snorkel hoặc biểu quyết-có-trọng-số nếu gọn), calibrate theo gold seed, xuất nhãn xác suất.
6. **Group split** 70/15/15 theo ảnh gốc (gộp ×3 augment Roboflow cùng tập).
7. **Huấn luyện** backbone nhẹ (MobileNetV3/EfficientNet-Lite), 3 sigmoid heads, BCE có trọng số lớp; dò kích thước đầu vào (224/320/384).
8. **Đánh giá** trên gold seed; báo cáo macro/micro-F1, AUC, per-source; hiệu chỉnh ngưỡng τ_k theo F1.

**Giai đoạn D — Triển khai**
9. Nén INT8 → TFLite/ONNX Mobile; đo latency + size; dựng đường cong accuracy–latency.

## 3. Ước lượng công sức

| Việc | Công sức | Ghi chú |
|------|----------|---------|
| Gold seed (300–500 ảnh) | 1–2 ngày người gán | Việc thủ công chính, làm 1 lần |
| Tích hợp LF1–3 vào notebook | Thấp | Notebook đã sẵn; cần 3 mô hình hạ nguồn đủ tốt |
| Degradation (LF4) | Trung bình | Viết bộ biến đổi + vòng dò điểm gãy |
| Label model + fusion | Trung bình | Snorkel hoặc trọng số đơn giản |
| Dò kích thước đầu vào | ~3× compute train | Compute nền, ít công thủ công |

## 4. Việc cần bạn quyết / chuẩn bị

- Đã có sẵn 3 model hạ nguồn (độ-chín, bệnh-lá, bệnh-thân) chưa? Nếu chưa, cần huấn luyện/tải trước khi LF1–3 chạy được. Model độ chín có thể train ngay trên nhãn `dry/green/tender` của bộ Roboflow.
- Trong notebook pilot, ảnh bộ Roboflow ánh xạ native sang `maturity_evaluation` (vì có nhãn độ chín `dry/green/tender`).
