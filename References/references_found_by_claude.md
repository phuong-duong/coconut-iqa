# Tài liệu tham khảo — do Claude TÌM RA (không phải tạo ra)

> Quy ước folder `References/`: nơi chứa tài liệu tham khảo từ người khác. **Dùng bất kỳ mục nào ở đây trong paper thì PHẢI dẫn nguồn.**
>
> File này liệt kê các tài liệu Claude tìm được kèm nguồn gốc. Claude **không tải được** các PDF có bản quyền/trả phí (Springer, các nhà xuất bản) — bạn tự tải về rồi bỏ file vào folder này. Mỗi mục ghi rõ: trích dẫn, link, dùng cho LF/mục nào, mức liên quan.

Ngày cập nhật: 2026-07-11

---

## Nguồn: FDSE 2025 — Proceedings Part II (CCIS vol. 2709, Springer)

Tuyển tập: Tran Khanh Dang, Josef Küng, Tai M. Chung (eds.), *Future Data and Security Engineering*, 12th Int. Conf. FDSE 2025, HCMC, Nov 27–29 2025, Part II. DOI: https://doi.org/10.1007/978-981-95-4724-1

Cảnh báo: **không có bài nào về dừa hay đúng 5 tác vụ hạ nguồn** → chỉ dùng làm citation cho Related Work / biện luận phương pháp, KHÔNG dùng làm mô hình hạ nguồn cho LF1–5.

### Đáng dùng rõ ràng

1. **Evaluating YOLOv11 for Traffic Object Detection Under Adverse Weather Conditions**
   - Thai-Bao Tran, Minh-Thanh Ta, Hai Thanh Nguyen. Pages 300–314.
   - DOI: https://doi.org/10.1007/978-981-95-4724-1_21
   - Dùng cho: **LF6 (controlled degradation)** + §2.2, §3.9. Bằng chứng "điều kiện ảnh xấu làm hỏng tác vụ detection".
   - Mức liên quan: CAO (khớp nhất).

2. **Vision-Based Large Language Models for Vietnamese Handwriting Recognition**
   - Anh Duc Le, Quoc-Dung Nguyen. Pages 468–475.
   - DOI: https://doi.org/10.1007/978-981-95-4724-1_35
   - Dùng cho: **LF7 (vision/VLM labeling)**. Ví dụ dùng VLM trên ảnh ở đúng venue FDSE.
   - Mức liên quan: CAO–VỪA.

3. **Towards Reliable Early Fire and Smoke Detection Using Optimized YOLOv11**
   - Nhan Phi Nguyen, Phu Thien Huynh, Kiet Anh Nguyen, Toan Thai Pham Tran, Thai T. Vo Nguyen, Hai Thanh Nguyen. Pages 363–378.
   - DOI: https://doi.org/10.1007/978-981-95-4724-1_25
   - Dùng cho: §2.4 (mô hình nhẹ chạy edge) + framing "độ tin cậy". Cùng loại ref [11][12] hiện có.
   - Mức liên quan: VỪA.

### Hỗ trợ (dùng khi cần độn citation cho một câu cụ thể)

4. **FallTrack-Net: Real-Time Detection … in a Smartphone-Based Safety System**
   - Huu Nghia Huynh, Vo Thien Bao Nguyen, Thien Phu Doan. Pages 227–241.
   - DOI: https://doi.org/10.1007/978-981-95-4724-1_16
   - Dùng cho: §2.4, §3.7 — dẫn chứng suy luận real-time trên smartphone/edge.

5. **Lightweight ViT-Based Image Retrieval System with Qdrant …**
   - Pham Tran Nhat Linh và cộng sự. Pages 442–450.
   - DOI: https://doi.org/10.1007/978-981-95-4724-1_32
   - Dùng cho: tham khảo backbone thị giác nhẹ (§3.5).

6. **An Efficient Model for Fracture Detection in Wrist Trauma Images**
   - Thanh Thien Nguyen, Hoang-Loc Tran, Duc-Lung Vu. Pages 419–426.
   - DOI: https://doi.org/10.1007/978-981-95-4724-1_29
   - Dùng cho: thêm ref cho "efficient/lightweight detection" trên ảnh.

7. **Robust ResNet-Based Models for Skin Lesion Detection**
   - Quoc-Dung Nguyen, Thien-An Ngoc Nguyen, Anh-Thu Nguyen Tran, Nguyet-Minh Phan. Pages 268–282.
   - DOI: https://doi.org/10.1007/978-981-95-4724-1_19
   - Dùng cho: LF6 (tangential) — tính bền của bộ phân loại ảnh.

8. **Using a Large Language Model to Build a Vietnamese Natural Language Inference Dataset**
   - Chinh Trong Nguyen, Tuyen Thi-Thanh Do, Dang Tuan Nguyen. Pages 394–408.
   - DOI: https://doi.org/10.1007/978-981-95-4724-1_27
   - Dùng cho: §3.3.2 — tương tự về mặt phương pháp dùng model sinh nhãn/dataset (weak supervision).

9. **LLM-Based Evaluation for Dynamic Routing Among Large Language Models**
   - Takeshi Tsuchiya và cộng sự. Pages 13–25.
   - DOI: https://doi.org/10.1007/978-981-95-4724-1_2
   - Dùng cho: tangential với LF7 (ý tưởng model-as-evaluator).

10. **Hybrid Deep Learning–Data Augmentation Approach for Sound Classification**
    - Tran Chau Thanh Thien. Pages 427–434.
    - DOI: https://doi.org/10.1007/978-981-95-4724-1_30
    - Dùng cho: §3.4 — phương pháp augmentation (rất yếu).

---

## Chưa kiểm tra

- **FDSE 2025 Part I** (ISBN 978-981-95-4721-0, DOI 10.1007/978-981-95-4721-0) — chưa lọc TOC. Nhiều khả năng có thêm bài nông nghiệp/thị giác hợp hơn (mục "Advances in ML" và "Smart City & Industry 4.0"). Cần rà tiếp.

---

## Tài liệu người dùng tự thêm (để đối chiếu, không phải Claude tìm)

- `lf1_paper_maturity.pdf` — dùng cho LF1 (đánh giá độ chín). Nguồn: do người dùng cung cấp.
