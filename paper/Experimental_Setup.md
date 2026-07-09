# 4. Thiết lập thực nghiệm (Experimental Setup)

> Phần này mô tả các thành phần **đã cố định** của thiết lập thực nghiệm: nguồn dữ
> liệu và thống kê thật, tiêu chí gán nhãn, giao thức chia dữ liệu, tiền xử lý, họ
> kiến trúc ứng viên, khung huấn luyện và bộ chỉ số đánh giá. Các giá trị phụ thuộc
> vào việc chạy thí nghiệm (siêu tham số đã chốt, phần cứng đo lường, số lượng nhãn
> sau hợp nhất, ngưỡng đã hiệu chỉnh...) **chưa được đưa vào** và được liệt kê riêng
> ở cuối tài liệu (mục "Ghi chú — cần bổ sung", không thuộc thân bài báo).

## 4.1. Nguồn dữ liệu và thống kê

Bộ dữ liệu được tổng hợp từ hai nguồn ảnh dừa công khai, phủ đủ năm tác vụ hạ nguồn.
Mỗi ảnh mang đáp án đúng (ground-truth) cho đúng một tác vụ theo nguồn của nó. Tổng
cộng **6.746 ảnh**.

**(a) Độ chín — bộ *coconut* (v5), Roboflow Universe [1]** (giấy phép CC BY 4.0),
định dạng YOLO, nhãn ba mức độ chín (`dry`, `green`, `tender`) gán ở cấp độ **từng
trái** (bounding box). Bộ này đã chia sẵn train/valid/test; tập huấn luyện được nhà
cung cấp tăng cường sẵn ×3.

| Split | Số ảnh | Ghi chú |
|-------|--------|---------|
| train | 834 | 278 ảnh gốc × 3 bản tăng cường |
| valid | 78 | không tăng cường |
| test | 36 | không tăng cường |
| **Tổng** | **948** | từ **392 ảnh gốc** |

Phân bố nhãn mức chín ở cấp độ trái: **1.232 bounding box** (tender 685, green 320,
dry 227).

**(b) Bệnh cây dừa — *Coconut Tree Disease Dataset*, Mendeley Data [2]**, gồm năm
thư mục lớp bệnh, ánh xạ sang bốn tác vụ theo *required-view*:

| Lớp bệnh (nguồn) | Số ảnh | Tác vụ hạ nguồn |
|------------------|--------|-----------------|
| Gray Leaf Spot | 2.135 | `2_foliar_disease` (bệnh lá) |
| Leaf Rot | 1.673 | `2_foliar_disease` (bệnh lá) |
| Stem Bleeding | 1.006 | `3_trunk_disease` (bệnh thân) |
| Bud Rot | 470 | `4_crown_disease` (bệnh đọt/crown) |
| Bud Root Dropping | 514 | `5_petiole` (tình trạng tàu lá) |
| **Tổng bệnh** | **5.798** | |

Hai lớp Gray Leaf Spot và Leaf Rot cùng dồn về tác vụ bệnh lá (3.808 ảnh), phản ánh
việc cả hai đều được chẩn đoán trên cùng một *required-view* (phiến lá cận cảnh).

## 4.2. Tiêu chí gán nhãn theo required-view

Nhãn độ hữu dụng được định nghĩa theo *sự thành công của tác vụ hạ nguồn*
(task-driven), không theo cảm quan thẩm mỹ. Mỗi tác vụ gắn với một *required-view* —
ảnh phải thể hiện đúng đối tượng/góc nhìn thì mới được coi là hữu dụng; "hữu dụng"
nghĩa là **thấy rõ đối tượng đủ để đánh giá** (kể cả khi kết luận là khỏe mạnh), chứ
không đòi ảnh phải chứa triệu chứng bệnh:

| Tác vụ | Required-view (đối tượng phải thấy rõ) |
|--------|----------------------------------------|
| `1_maturity_evaluation` | Trái dừa (kích thước/hình dạng/màu vỏ trung thực) |
| `2_foliar_disease` | Phiến lá (lá chét) |
| `3_trunk_disease` | Bề mặt thân |
| `4_crown_disease` | Đỉnh đọt/crown (lý tưởng nhìn từ trên xuống) |
| `5_petiole` | Cuống lá hoặc tư thế/độ rủ tàu lá (đủ đánh giá độ rủ/vàng úa/còi cọc) |

Bài toán là **phân loại đa nhãn**: mỗi ảnh → vector năm chiều, mỗi chiều một hàm
kích hoạt *sigmoid độc lập* (không dùng *softmax*), cho phép một ảnh phù hợp với
nhiều, một, hoặc không tác vụ nào. Chi tiết cơ chế sinh nhãn (weak-supervision
fusion neo vào gold seed) trình bày ở mục Phương pháp (§3.3).

## 4.3. Giao thức chia dữ liệu

Dữ liệu được chia huấn luyện/kiểm định/kiểm thử theo tỷ lệ **70/15/15** có **phân
tầng** (giữ cân bằng tỷ lệ nhãn và nguồn giữa các tập). Việc chia thực hiện ở **cấp
độ ảnh gốc (group split)**: mọi bản tăng cường sinh từ cùng một ảnh gốc bắt buộc nằm
trong cùng một tập, để chống rò rỉ dữ liệu — ràng buộc này đặc biệt quan trọng với bộ
Roboflow (mỗi ảnh gốc có ba bản tăng cường gần trùng). Mô hình được huấn luyện trên
nhãn hợp nhất, còn **đánh giá cuối cùng thực hiện trên tập gold seed do người gán**,
không trên nhãn tự sinh.

## 4.4. Tiền xử lý và tăng cường

Ảnh được chuẩn hóa về không gian màu và dải giá trị thống nhất, đưa về kích thước đầu
vào của mô hình bằng phép co giãn **giữ tỷ lệ khung hình kèm đệm (*letterbox
padding*)** để tránh méo hình, rồi chuẩn hóa theo trung bình/độ lệch chuẩn của tập
huấn luyện. Độ phân giải đầu vào **không cố định ở 224×224** mà được coi là một siêu
tham số cần dò thực nghiệm, khảo sát các mức đại diện **224, 320, 384**; lý do là độ
hữu dụng phụ thuộc mạnh vào chi tiết cục bộ (màu/bề mặt vỏ trái; triệu chứng nhỏ trên
lá/thân) mà nén ảnh quá mạnh có thể xóa mất. Tăng cường dữ liệu mô phỏng biến thiên
hiện trường (lật, xoay nhẹ, dịch/thu phóng, nhiễu loạn màu) được áp dụng có kiểm soát
để không mâu thuẫn với nhãn.

Lưu ý về đặc thù nguồn: ảnh bộ Roboflow (độ chín) **đã qua tiền xử lý sẵn** (resize
stretch, auto-contrast và tăng cường phơi sáng ×3 khi xuất). Vì vậy bộ này không được
dùng để đánh giá tín hiệu chất lượng ảnh, và các bản tăng cường của cùng một ảnh gốc
phải nằm cùng split (xem §4.3).

## 4.5. Họ kiến trúc ứng viên

Do ràng buộc triển khai trên điện thoại tại hiện trường, mô hình ưu tiên backbone
tích chập **nhẹ dành cho thiết bị biên**: **MobileNetV3** và **EfficientNet-Lite**,
khởi tạo bằng trọng số tiền huấn luyện trên ImageNet rồi tinh chỉnh trên dữ liệu dừa.
Phần đầu phân loại được thay bằng một lớp fully-connected sinh **K = 5** đầu ra, mỗi
đầu ra qua *sigmoid* độc lập. Backbone **dùng chung cho cả năm tác vụ** theo cơ chế
học đa nhiệm, tái sử dụng đặc trưng cấp thấp và giảm mạnh số tham số so với năm mô
hình riêng biệt — yếu tố then chốt cho ràng buộc bộ nhớ/năng lượng của thiết bị di
động.

## 4.6. Khung huấn luyện

Hàm mất mát là *binary cross-entropy* trung bình trên K = 5 nhãn, có trọng số lớp
$w_k$ đặt tỷ lệ nghịch với tần suất nhãn dương để bù mất cân bằng:

$$\mathcal{L} = -\frac{1}{K}\sum_{k=1}^{K}\Big[ w_k\, y_k \log \hat{y}_k + (1 - y_k)\log(1 - \hat{y}_k)\Big].$$

Khi huấn luyện trên nhãn xác suất mềm từ mô hình nhãn, $y_k$ được thay bằng xác suất
tương ứng. Bộ tối ưu là **AdamW** với lịch giảm học suất *cosine annealing* và **dừng
sớm** theo chỉ số trên tập kiểm định. Ngưỡng quyết định $\tau_k$ của mỗi tác vụ
**không cố định ở 0.5** mà được hiệu chỉnh trên tập kiểm định bằng cách tối đa hóa
F1.

## 4.7. Bộ chỉ số đánh giá

Do bài toán đa nhãn và mất cân bằng, hiệu năng được báo cáo trên **từng tác vụ** và
tổng hợp toàn cục:

- Precision, recall, **F1 (macro và micro)**, độ chính xác từng nhãn và **AUC-ROC**
  cho mỗi tác vụ;
- **Subset accuracy** (đúng đồng thời cả năm nhãn) và **Hamming loss** ở cấp độ vector
  nhãn;
- Về vận hành, chú trọng **recall của lớp "không phù hợp"** mỗi tác vụ, vì bỏ sót một
  ảnh kém (để lọt vào tác vụ hạ nguồn) tốn kém hơn việc yêu cầu chụp lại;
- **Báo cáo per-source** (theo từng nguồn dữ liệu) để phát hiện *shortcut learning* —
  mô hình phân biệt nguồn ảnh thay vì độ hữu dụng thật.

Bộ tiền kiểm chất lượng (Tầng 1) được đánh giá riêng. Hiệu quả triển khai (độ trễ,
kích thước mô hình) được báo cáo song song với độ chính xác dưới dạng đường cong đánh
đổi accuracy–latency (chi tiết ở mục Phương pháp §3.7).

---

## Ghi chú — cần bổ sung (KHÔNG thuộc thân bài báo)

Các mục dưới đây phụ thuộc vào việc chạy pipeline, hiện **chưa có số liệu thật** nên
chưa đưa vào bài. Cần hoàn thành rồi mới điền:

1. **Nhãn correctness (LF1–5) chưa sinh.** `labels/lf1-5_correctness_manifest.csv` có
   đủ 6.746 dòng nhưng **cả năm cột nhãn đang trống** — vì mô hình hạ nguồn còn là hàm
   giữ chỗ (stub). → Cần huấn luyện/tích hợp năm mô hình hạ nguồn, chạy notebook để
   điền nhãn.
2. **Gold seed chưa có.** Cần gán tay ~300–500 ảnh phân tầng + viết annotation
   protocol. Bổ sung vào §4.3: **kích thước gold seed thật, quy trình gán, số người
   gán, Cohen's κ**.
3. **Label model (fusion) chưa chạy.** Sau khi có LF1–5, LF-degradation và LF-vision,
   cần hợp nhất → nhãn xác suất, calibrate theo gold seed. Bổ sung: **phân bố
   dương/âm mỗi tác vụ sau hợp nhất** (bảng thống kê nhãn cuối).
4. **Controlled degradation LF chưa triển khai.** Cần bộ suy giảm theo trục (mờ, phơi
   sáng, phân giải/nén, che khuất, cân bằng trắng) + dò điểm gãy mỗi tác vụ.
5. **LF-vision mới ở mức pilot 48 ảnh** (`labels/lf7_vision_pilot.csv`). Cần chạy diện
   rộng nếu dùng làm tín hiệu chính thức.
6. **Chia dữ liệu chưa thực thi.** Đã có giao thức (70/15/15, group-split) nhưng chưa
   chạy. Bổ sung: **số ảnh thực tế mỗi split** sau khi chia.
7. **Backbone và độ phân giải cuối cùng chưa chốt.** Hiện là *ứng viên* (MobileNetV3 /
   EfficientNet-Lite; 224/320/384). Sau thí nghiệm cần ghi rõ **lựa chọn cuối**.
8. **Siêu tham số cụ thể chưa có.** Learning rate, batch size, số epoch, tham số
   cosine schedule, tiêu chí early-stopping cụ thể — điền sau khi tune.
9. **Môi trường phần cứng/phần mềm chưa ghi.** GPU huấn luyện, thiết bị di động đại
   diện để đo latency, phiên bản framework (PyTorch/TF, TFLite/ONNX Runtime Mobile),
   cấu hình lượng tử hóa INT8 — cần một tiểu mục "Implementation details".
10. **Ngưỡng $\tau_k$ chưa hiệu chỉnh** (cần tập kiểm định có nhãn thật) — điền giá trị
    sau.
11. **Kết quả nén** (kích thước MB, độ trễ ms/ảnh trước–sau INT8) — thuộc phần Kết quả
    nhưng cấu hình đo cần khai báo ở Setup.

**Nguồn tham khảo dữ liệu**
[1] coconut dataset (v5), nit-calicut, Roboflow Universe (CC BY 4.0). https://universe.roboflow.com/nit-calicut/coconut-veirf
[2] Coconut Tree Disease Dataset, Mendeley Data. https://data.mendeley.com/datasets/gh56wbsnj5/1
