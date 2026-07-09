# 3. Phương pháp nghiên cứu (Methodology)

## 3.1. Tổng quan khung phương pháp

Nghiên cứu đề xuất một khung đánh giá độ hữu dụng của ảnh chụp cây/trái dừa theo hướng *task-oriented Image Quality Assessment* (IQA), hoạt động như một bộ lọc đặt ngay trước các tác vụ phân tích hạ nguồn. Khác với IQA truyền thống vốn đánh giá chất lượng ảnh theo nghĩa thẩm mỹ hoặc kỹ thuật tổng quát (độ nét, phơi sáng, nhiễu), khung này đánh giá *tính phù hợp theo tác vụ*: một ảnh chỉ được coi là "hữu dụng" khi nó cung cấp đủ thông tin thị giác để một tác vụ cụ thể phía sau thực hiện thành công.

Pipeline gồm hai tầng nối tiếp:

- **Tầng 1 — Tiền kiểm chất lượng (quality pre-check).** Một bộ luật ảnh nhẹ (đo độ mờ, phơi sáng, độ phân giải) chạy tức thì trên thiết bị; ảnh quá kém được báo chụp lại ngay tại hiện trường, không cần gọi mô hình học sâu.
- **Tầng 2 — Mô hình phân loại đa nhãn theo tác vụ.** Ảnh qua tiền kiểm được đưa vào một mạng tích chập nhẹ, sinh ra quyết định phù hợp/không phù hợp cho từng tác vụ.

Nhờ suy luận tại biên (*edge inference*), hệ thống loại bỏ độ trễ và chi phí truyền dữ liệu, đồng thời tránh lãng phí công sức di chuyển giữa hiện trường và phòng thí nghiệm: người nông dân được phản hồi tức thời để chụp lại nếu ảnh không đạt.

## 3.2. Phát biểu bài toán

Gọi $x$ là một ảnh đầu vào. Ta xét $K = 5$ tác vụ hạ nguồn, phân theo *required-view* (ảnh phải thể hiện đúng đối tượng/góc nhìn):

- $t_1$ — đánh giá độ chín (`1_maturity_evaluation`);
- $t_2$ — chẩn đoán bệnh trên lá (`2_foliar_disease`);
- $t_3$ — chẩn đoán bệnh thân (`3_trunk_disease`);
- $t_4$ — chẩn đoán bệnh đọt/crown (`4_crown_disease`);
- $t_5$ — sàng lọc suy tàn toàn cây / bệnh rễ-rụng chồi (`5_wholetree_decline`).

Bài toán được hình thức hóa dưới dạng **phân loại đa nhãn** (*multi-label classification*): mô hình $f_\theta$ ánh xạ mỗi ảnh $x$ thành một vector xác suất

$$\hat{y} = f_\theta(x) \in [0,1]^K,$$

trong đó $\hat{y}_k$ là xác suất ảnh $x$ phù hợp cho tác vụ $t_k$, và nhãn thật $y_k \in \{0,1\}$. Thiết kế đa nhãn (thay vì đa lớp loại trừ lẫn nhau) phản ánh thực tế rằng một ảnh có thể đồng thời phù hợp cho nhiều tác vụ, phù hợp cho một số và không cho số còn lại, hoặc không cho tác vụ nào. Mỗi nhãn dùng một hàm kích hoạt *sigmoid* độc lập.

**Tiêu chí phù hợp theo tác vụ** (mỗi tác vụ gắn với một *required-view*): độ chín cần thấy rõ **trái** với kích thước/hình dạng/màu vỏ trung thực; bệnh lá cần thấy rõ **phiến lá** và triệu chứng; bệnh thân cần thấy rõ **bề mặt thân** (vết chảy nhựa); bệnh đọt/crown cần thấy rõ **đỉnh đọt** (lý tưởng nhìn từ trên xuống) với dấu hiệu thối/đổi màu; suy tàn toàn cây cần thấy **dáng cây tổng thể từ xa** (còi cọc, tán rủ, vàng úa).

## 3.3. Xây dựng tập dữ liệu và sinh nhãn

### 3.3.1. Nguồn dữ liệu

Dữ liệu được tổng hợp từ các nguồn ảnh dừa công khai:

- **Độ chín** — bộ *coconut* (v5) trên Roboflow Universe [1] (giấy phép CC BY 4.0; 392 ảnh gốc, 948 ảnh sau tăng cường ×3 ở tập huấn luyện), định dạng YOLO với nhãn **3 mức độ chín** (`dry`, `green`, `tender`) gán cho từng trái. Nhờ đó độ chín có đáp án đúng ở cấp độ từng trái và được gán bằng correctness (xem 3.3.2).
- **Bệnh cây dừa** — bộ *Coconut Tree Disease Dataset* trên Mendeley Data [2], gồm các lớp bệnh: Gray Leaf Spot, Leaf Rot (bệnh lá → `2_foliar_disease`); Stem Bleeding (bệnh thân → `3_trunk_disease`); Bud Rot (bệnh đọt/crown → `4_crown_disease`); Bud Root Dropping (suy tàn toàn cây → `5_wholetree_decline`).

**Nguồn tham khảo dữ liệu:**
[1] coconut dataset (v5), nit-calicut, Roboflow Universe (CC BY 4.0). https://universe.roboflow.com/nit-calicut/coconut-veirf
[2] Coconut Tree Disease Dataset, Mendeley Data. https://data.mendeley.com/datasets/gh56wbsnj5/1

### 3.3.2. Định nghĩa nhãn theo hướng task-driven

Điểm cốt lõi về phương pháp: độ hữu dụng **không được gán bằng phán đoán chủ quan** mà được **định nghĩa theo sự thành công của chính tác vụ hạ nguồn**. Cụ thể, một ảnh được coi là phù hợp cho tác vụ $t_k$ nếu mô hình chuyên trách cho tác vụ đó xử lý ảnh thành công. Đây là định nghĩa thao tác (operational), gắn trực tiếp với mục tiêu ứng dụng và tránh việc tự khẳng định độ hữu dụng.

Nhãn được sinh bằng cách **hợp nhất nhiều tín hiệu yếu (weak-supervision fusion) neo vào một tập nhỏ do người gán (gold seed)**, với ba nhóm tín hiệu chính:

1. **Tính đúng so với đáp án sẵn có (correctness vs. ground-truth).** Cả năm tác vụ đều có đáp án đúng trong dữ liệu: độ chín (nhãn mức `dry`/`green`/`tender` từng trái), và bốn tác vụ bệnh (nhãn lớp bệnh tương ứng của bộ Coconut Tree Disease Dataset). Mỗi ảnh có đáp án cho đúng một tác vụ theo nguồn của nó. Độ hữu dụng được xác định bằng việc mô hình hạ nguồn dự đoán *đúng* trên ảnh đó hay không (với độ chín: đọc đúng mức chín so với nhãn thật). Đây là tín hiệu đáng tin nhất.
2. **Suy giảm có kiểm soát (controlled degradation).** Từ các ảnh mà tác vụ hạ nguồn xử lý thành công, ta chủ động làm suy giảm theo từng trục mô phỏng lỗi chụp thực tế (mờ, phơi sáng sai, giảm phân giải/nén, che khuất, lệch cân bằng trắng) và xác định mức suy giảm mà tại đó tác vụ bắt đầu thất bại. Cách này sinh nhiều mẫu quanh đúng ranh giới hữu dụng và cho quan hệ nhân quả rõ ràng; đặc biệt quan trọng ở trục chất lượng.
3. **Confidence đã hiệu chỉnh / phát hiện ngoài phân phối (OOD).** Chỉ dùng ở nơi thiếu đáp án đúng; điểm tin cậy phải được hiệu chỉnh (calibration) trước khi dùng, vì mô hình học sâu thường tự tin nhưng sai trên ảnh xấu.

Các tín hiệu này được biểu diễn dưới dạng các *hàm gán nhãn* (labeling functions) — mỗi hàm bỏ phiếu phù hợp/không/bỏ qua cho từng tác vụ — rồi một *mô hình nhãn* (label model) hợp nhất chúng thành nhãn xác suất, có tính đến độ tin cậy và tương quan giữa các hàm. Một **tập gold seed** vài trăm ảnh do người gán (phân tầng) được dùng để: hiệu chỉnh mô hình nhãn, ước lượng độ chính xác từng hàm, báo cáo độ đồng thuận (Cohen's $\kappa$) làm bằng chứng độ tin cậy của nhãn tự động, và làm **tập kiểm thử vàng** cho đánh giá cuối cùng.

### 3.3.3. Phân chia dữ liệu

Tập dữ liệu được chia huấn luyện/kiểm định/kiểm thử theo tỷ lệ 70/15/15 theo phương thức phân tầng. Việc chia được thực hiện ở **cấp độ ảnh gốc (group split)** để tránh rò rỉ dữ liệu — đặc biệt vì bộ Roboflow tạo sẵn 3 phiên bản tăng cường từ mỗi ảnh gốc; các phiên bản này phải nằm cùng một tập. Mô hình được huấn luyện trên nhãn xác suất hợp nhất, nhưng đánh giá cuối cùng trên tập gold seed do người gán.

## 3.4. Tiền xử lý và tăng cường dữ liệu

Ảnh được chuẩn hóa về không gian màu và dải giá trị thống nhất, đưa về kích thước đầu vào của mô hình bằng phép co giãn có giữ tỷ lệ khung hình kèm đệm (*letterbox padding*) để tránh méo hình, rồi chuẩn hóa theo trung bình/độ lệch chuẩn của tập huấn luyện. Khác với thông lệ cố định kích thước ở $224\times224$, chúng tôi **xem độ phân giải đầu vào là một siêu tham số cần dò thực nghiệm** (khảo sát các mức đại diện như $224$, $320$, $384$), vì độ hữu dụng của ảnh phụ thuộc mạnh vào chi tiết cục bộ (màu/bề mặt vỏ trái để đánh giá độ chín; triệu chứng nhỏ trên lá/thân để chẩn bệnh) mà nén ảnh quá mạnh có thể xóa mất. Tăng cường dữ liệu mô phỏng biến thiên hiện trường (lật, xoay nhẹ, dịch/thu phóng, nhiễu loạn màu) được áp dụng có kiểm soát để không mâu thuẫn với nhãn.

## 3.5. Kiến trúc mô hình

Vì mục tiêu triển khai trên điện thoại tại hiện trường, chúng tôi ưu tiên backbone tích chập nhẹ dành cho thiết bị biên như **MobileNetV3** hoặc **EfficientNet-Lite**, khởi tạo bằng trọng số tiền huấn luyện trên ImageNet và tinh chỉnh trên dữ liệu dừa. Phần đầu phân loại được thay bằng một lớp fully-connected sinh $K = 5$ đầu ra, mỗi đầu ra qua hàm *sigmoid* độc lập (không dùng *softmax*) để phù hợp với thiết lập đa nhãn. Backbone dùng chung cho cả năm tác vụ theo cơ chế học đa nhiệm, tái sử dụng đặc trưng thị giác cấp thấp và giảm mạnh số tham số so với năm mô hình riêng — yếu tố then chốt cho ràng buộc bộ nhớ/năng lượng của thiết bị di động.

## 3.6. Huấn luyện

Mô hình được huấn luyện bằng hàm mất mát *binary cross-entropy* trung bình trên $K$ nhãn:

$$\mathcal{L} = -\frac{1}{K}\sum_{k=1}^{K}\Big[ w_k\, y_k \log \hat{y}_k + (1 - y_k)\log(1 - \hat{y}_k)\Big],$$

với $w_k$ là trọng số lớp bù mất cân bằng nhãn (đặt tỷ lệ nghịch với tần suất nhãn dương). Khi huấn luyện trên nhãn xác suất mềm từ mô hình nhãn, $y_k$ được thay bằng xác suất tương ứng. Chúng tôi dùng bộ tối ưu AdamW với lịch giảm học suất (*cosine annealing*), dừng sớm theo chỉ số trên tập kiểm định. Ngưỡng quyết định $\tau_k$ cho mỗi tác vụ được hiệu chỉnh trên tập kiểm định bằng cách tối đa hóa F1, thay vì cố định ở $0.5$.

## 3.7. Lựa chọn kích thước đầu vào và triển khai trên thiết bị di động

Việc chọn độ phân giải đầu vào được thực hiện như một bước tối ưu đa mục tiêu, cân bằng giữa chất lượng dự đoán và chi phí suy luận. Với mỗi độ phân giải ứng viên, chúng tôi ghi nhận đồng thời (i) macro-F1 trên tập kiểm định và (ii) chi phí triển khai (độ trễ ms/ảnh, kích thước mô hình MB) đo trên một thiết bị di động đại diện *sau khi* nén, rồi dựng đường cong đánh đổi độ chính xác ↔ độ trễ, chọn điểm cân bằng và **chốt một độ phân giải duy nhất** trước khi đánh giá trên tập kiểm thử. Sau khi chốt cấu hình, mô hình được nén (lượng tử hóa INT8, tùy chọn cắt tỉa) và chuyển sang định dạng suy luận di động (TensorFlow Lite hoặc ONNX Runtime Mobile). Đường cong accuracy–latency vừa là cơ sở chọn cấu hình, vừa là một kết quả trình bày của nghiên cứu.

## 3.8. Chỉ số đánh giá

Do bài toán đa nhãn và mất cân bằng, hiệu năng được đánh giá trên từng tác vụ và tổng hợp bằng: precision, recall, F1 (macro và micro), độ chính xác từng nhãn và AUC-ROC cho mỗi tác vụ; bổ sung *subset accuracy* (đúng đồng thời cả 5 nhãn) và *Hamming loss* ở cấp độ vector nhãn. Về vận hành, chúng tôi chú trọng *recall* của lớp "không phù hợp" cho mỗi tác vụ, vì bỏ sót một ảnh kém (để lọt vào tác vụ hạ nguồn) tốn kém hơn việc yêu cầu chụp lại. Bộ tiền kiểm chất lượng được đánh giá riêng, và hiệu quả triển khai được báo cáo song song qua độ trễ và kích thước mô hình.

## 3.9. Nguy cơ đối với tính hiệu lực (Threats to Validity)

Chúng tôi công bố minh bạch các giới hạn sau cùng biện pháp giảm thiểu:

- **Nhãn proxy sinh theo quy tắc.** Nhãn độ hữu dụng phần lớn suy ra từ mô hình hạ nguồn và heuristic, không phải phán đoán độc lập của con người, nên tiềm ẩn tính vòng lặp. Giảm thiểu: xác thực trên tập gold seed do người gán và báo cáo $\kappa$.
- **Nhiễu do nguồn dữ liệu (shortcut).** Vì nhãn tương quan với nguồn ảnh, mô hình có thể học phân biệt nguồn thay vì độ hữu dụng. Giảm thiểu: báo cáo hiệu năng theo từng nguồn.
- **Tiền xử lý sẵn ở bộ Roboflow (độ chín)** (ảnh đã qua resize stretch, auto-contrast và tăng cường phơi sáng ×3 khi xuất) làm sai lệch tín hiệu chất lượng và tạo ảnh gần trùng. Giảm thiểu: group split theo ảnh gốc; không dùng ảnh đã chuẩn hóa để đánh giá cổng chất lượng.
- **Nhãn đặc thù theo mô hình hạ nguồn.** Định nghĩa "hữu dụng = tác vụ thành công" khiến nhãn phụ thuộc năng lực mô hình hạ nguồn; đổi mô hình có thể đổi nhãn. Khung lại đúng bản chất: mô hình IQA dự đoán *khả năng thành công của tác vụ hạ nguồn*.
- **Lệch phân phối với triển khai thực tế.** Dữ liệu là ảnh dataset đã chuẩn hóa/cận cảnh, khác ảnh điện thoại chụp ngoài đồng. Giảm thiểu: thu thập một tập kiểm thử nhỏ ảnh hiện trường thật (hướng phát triển).
- **Bệnh tách theo required-view.** Bốn bệnh được tách thành các tác vụ riêng theo đối tượng/góc nhìn chẩn đoán (`3_trunk_disease`, `4_crown_disease`, `5_wholetree_decline`) thay vì gộp chung, vì mỗi bệnh cần một loại ảnh khác nhau (bề mặt thân / đỉnh đọt nhìn từ trên xuống / dáng cây từ xa).
- **Tín hiệu `5_wholetree_decline` kém đặc hiệu.** Dấu hiệu suy tàn toàn cây (tán rủ, vàng úa) do nhiều nguyên nhân, nên tác vụ này phù hợp cho sàng lọc bước đầu hơn là chẩn xác; xác nhận bệnh rễ/rụng chồi cần quan sát rễ (ngoài phạm vi ảnh chụp thông thường).
