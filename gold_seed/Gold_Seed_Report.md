# Gold Seed — Báo cáo (chốt ngày 2026-07-11)

Tập kiểm thử vàng do người gán (Duong Thi My Phuong), dùng để hiệu chỉnh label model,
đo độ đồng thuận và **đánh giá cuối cùng**. Đây là bản đã chốt.

## 1. Lấy mẫu
- **300 ảnh, cân bằng 60/tác vụ** (5 tác vụ), phân tầng theo nguồn GT.
- Nguồn Roboflow (maturity) **dedupe ở cấp ảnh gốc** (bỏ ×3 augment) chống rò rỉ/trùng.
- `seed=42`, tái lập bằng `sample_gold_seed.py`.
- Gán tay qua `annotate.html` theo `Annotation_Protocol.md`; **300/300 gán đủ 5 tác vụ, 0 skip**.

## 2. Phân bố nhãn

| Tác vụ | pos (1) | neg (0) | %pos |
|--------|--------:|--------:|-----:|
| 1_maturity | 62 | 238 | 20.7% |
| 2_foliar | 151 | 149 | 50.3% |
| 3_trunk | 71 | 229 | 23.7% |
| 4_crown | 69 | 231 | 23.0% |
| 5_petiole | 103 | 197 | 34.3% |

Mọi tác vụ đủ cả hai lớp (thiểu số ≥ 62) → F1/AUC per-task ổn định.

Cấu trúc đa nhãn: 0 nhãn dương = 2 ảnh · 1 = 191 · 2 = 58 · 3 = 47 · 4 = 2 ảnh.

## 3. Positive theo nguồn GT (kiểm shortcut)

| nguồn ↓ \\ nhãn → | maturity | foliar | trunk | crown | petiole |
|---|--:|--:|--:|--:|--:|
| maturity (60) | 58 | 5 | 3 | 0 | 12 |
| foliar (60) | 0 | 59 | 0 | 1 | 0 |
| trunk (60) | 0 | 0 | 60 | 0 | 0 |
| crown (60) | 0 | 60 | 0 | 60 | 31 |
| petiole (60) | 4 | 27 | 8 | 8 | 60 |

## 4. Hạn chế đã biết (đưa vào Limitations/Future Work)
1. **Positive đơn-nguồn (shortcut cao) ở trunk & crown**: `trunk=1` chỉ đến từ nguồn trunk
   (60/60), `crown=1` chỉ từ nguồn crown (60/60). Độ hữu dụng gần như trùng với domain →
   mô hình có thể học "nhận domain" thay vì "view có đánh giá được không". maturity cũng lệch
   (58/62) nhưng có positive đa nguồn + có negative nội nguồn. foliar/petiole an toàn (positive
   đa nguồn).
2. **Dữ liệu bệnh chỉ chứa mẫu bệnh (không có mẫu lành)**: cả 4 tác vụ nguồn-bệnh (foliar,
   trunk, crown, petiole) đều thiếu ảnh cơ quan **khỏe mạnh** → mô hình chỉ thấy cơ quan ở
   trạng thái bệnh.
3. **Thiếu negative khó** (đúng đối tượng nhưng chất lượng kém): dữ liệu tuyển sạch nên ít ảnh
   hỏng thật; cần LF6 degradation để bù, và ảnh thực địa của nông dân là future work.

**Đối phó bắt buộc:** luôn báo cáo **F1/AUC per-source**; ưu tiên bổ sung ảnh **cơ quan khỏe
mạnh + off-target + degraded** cho trunk/crown trước tiên.

Số liệu tái lập bằng `analyze_labels.py`.
