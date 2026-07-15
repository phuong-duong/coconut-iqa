# LF1 — Chọn kiến trúc model độ chín (downstream) để sinh nhãn

Mục đích: LF1 cần một model phân loại độ chín `dry/green/tender`. Model này **chạy offline trong lab** để sinh nhãn correctness cho LF1 — KHÔNG phải model triển khai trên thiết bị. Do đó **ưu tiên độ chính xác, không cần nhẹ**. (Model nhẹ/mobile-edge là dành cho bộ phân loại IQA cuối cùng, không phải LF1.)

## Các paper đã đọc

### 1. Palm Fruit Maturity Classification (arXiv 2502.20223, 2025) — chi tiết nhất, mở
- Bài toán gần nhất: phân loại độ chín trái cọ dầu, 5 mức, ~8.000 ảnh outdoor (nhiều góc/ánh sáng), 80/20 train-test.
- So sánh: CNN shallow (baseline) vs **ResNet50** vs InceptionV3, đều transfer learning + fine-tune từ ImageNet, input 224×224.
- Kết quả test: baseline 70.9% → **ResNet50 86.4%** → InceptionV3 85.2%.
- Bài học rút ra (rất hữu ích cho LF1):
  - **ResNet50 tổng quát hoá tốt nhất**, ổn định sau ~6 epoch, chênh train/val nhỏ.
  - **InceptionV3 bị overfit** (train 100%, test ~85%).
  - **EfficientNet thất bại** ở đây: train cao nhưng test <50% → tránh, hoặc phải tinh chỉnh kỹ.
  - Transfer learning cho độ chính xác cao chỉ trong vài epoch, **không cần tiền xử lý xoá nền / chỉnh sáng**.
  - Cảnh báo data leakage: paper trước (Altaheri) có ảnh gần trùng ở cả train lẫn test → accuracy ảo. **LF1 phải tách train/holdout sạch.**

### 2. Coconut Maturity Recognition Using CNN (Springer, 2022) — paywall, chỉ đọc abstract
- 7 backbone: VGG16/19, Xception, MobileNet, InceptionV3, InceptionResNetV2, ResNet50.
- Chỉ 2 mức (tender vs mature), ảnh outdoor nền phức tạp.
- **ResNet50 tốt nhất: top-1 98.3–98.5%.**

### 3. Deep Learning Based Coconut Fruit Maturity Classification (Springer, 2023) — paywall
- Liên quan trực tiếp (phân loại độ chín trái dừa), chưa lấy được full text. Cần tải thủ công nếu muốn trích số liệu.

## Khuyến nghị cho LF1

**Backbone: ResNet50, transfer learning + fine-tune từ ImageNet, input 224×224, 3 lớp `dry/green/tender`.**

Lý do:
- Thắng nhất quán trên cả 2 paper dừa/cọ liên quan.
- Tổng quát hoá tốt, ít overfit hơn InceptionV3, ổn định hơn EfficientNet.
- Nhẹ đủ để train nhanh trên Colab/GPU đơn.

Baseline để so sánh (đưa vào paper cho khách quan): một CNN nông + InceptionV3.

## Thiết lập để tránh data leakage (bắt buộc)
- Chia bộ Roboflow `coconut-veirf-v5` thành **train_maturity / holdout**.
- Model độ chín **chỉ train trên train_maturity**.
- LF1 **chỉ chấm correctness trên holdout** (ảnh model chưa thấy).
- Ghi rõ split này trong Experimental Setup.

## Bước tiếp theo
1. Kiểm tra cấu trúc `Dataset/coconut-veirf-v5` (train/valid/test, nhãn YOLO dry/green/tender).
2. Train ResNet50 3-lớp trên train split, giữ holdout.
3. Cắm `predict_maturity` vào `notebooks/lf1-5_correctness.ipynb`, chạy lại → điền cột `1_maturity_evaluation`.

## Nguồn
- Palm Fruit Maturity (arXiv): https://arxiv.org/pdf/2502.20223
- Coconut Maturity Recognition Using CNN (Springer 2022): https://link.springer.com/chapter/10.1007/978-981-16-9991-7_7
- Deep Learning Based Coconut Fruit Maturity Classification (Springer 2023): https://link.springer.com/10.1007/978-3-031-49529-8_6
- CNN Transfer Learning cho detect/count/segment dừa từ ảnh vệ tinh (ICTACT 2021): https://ictactjournals.in/paper/IJIVP_Vol_11_Iss_4_Paper_9_2475_2482.pdf
