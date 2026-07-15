# Annotation Protocol — Gold Seed (Coconut task-oriented IQA)

Tài liệu hướng dẫn gán nhãn tay cho **300 ảnh gold seed**. Mục tiêu: tạo nhãn "vàng"
do người gán, dùng để (1) hiệu chỉnh label model, (2) báo cáo Cohen's κ, (3) làm tập
kiểm thử cuối cùng. Nhãn ở đây là **chuẩn tham chiếu** — gán cẩn thận, nhất quán.

## 1. Nguyên tắc cốt lõi

**"Hữu dụng" = ảnh có đủ thông tin thị giác để một chuyên gia (hoặc mô hình) THỰC HIỆN ĐƯỢC
tác vụ đó — bất kể kết luận là có bệnh hay khỏe mạnh.**

- Gán theo **required-view**: ảnh có thể hiện đúng đối tượng/góc nhìn mà tác vụ cần không.
- **KHÔNG** đòi ảnh phải chứa triệu chứng bệnh. Một tàu lá khỏe mạnh, thấy rõ, vẫn "hữu
  dụng" cho tác vụ chẩn bệnh lá — vì ta *đánh giá được* là nó khỏe.
- Đây là **đa nhãn**: mỗi ảnh xét **cả 5 tác vụ độc lập**. Một ảnh có thể hữu dụng cho
  nhiều, một, hoặc không tác vụ nào. Đừng vì ảnh lấy từ thư mục "Bud Rot" mà chỉ tick crown
  — nếu ảnh đó cũng thấy rõ thân cây thì trunk cũng = 1.
- Đánh giá **chất lượng thị giác thực tế**, không đoán theo nguồn ảnh.

Quy tắc quyết định mỗi tác vụ: **1** = hữu dụng · **0** = không hữu dụng · **? (skip)** =
không chắc/khó phân xử (để riêng, xử lý sau — nên dùng tiết kiệm).

## 2. Định nghĩa hữu dụng theo từng tác vụ

| Tác vụ | required-view | =1 (hữu dụng) khi | =0 khi |
|--------|---------------|-------------------|--------|
| **1_maturity** — độ chín | Cận cảnh **trái dừa**, thấy rõ màu vỏ | Thấy ≥1 trái đủ rõ màu/bề mặt để phân biệt dry/green/tender | Không có trái, trái quá nhỏ/xa/mờ, bị che, ngược sáng mất màu |
| **2_foliar** — bệnh lá | Cận cảnh **phiến lá / lá chét** | Thấy rõ bề mặt lá đủ để soi đốm/thối/biến màu | Lá quá xa, chỉ thấy tán lá tổng thể, mờ, che khuất |
| **3_trunk** — bệnh thân | Bề mặt **thân cây** | Thấy rõ vỏ/bề mặt thân đủ để soi vết chảy nhựa/tổn thương | Không thấy thân, thân quá xa/mờ, chỉ thấy gốc lẫn cỏ |
| **4_crown** — bệnh đọt | **Đỉnh đọt/ngọn**, ưu tiên nhìn từ trên xuống hoặc thấy rõ chồi ngọn | Thấy rõ vùng đọt/chồi ngọn đủ để soi thối đọt | Chỉ thấy thân/lá dưới, đọt bị che, quá xa |
| **5_petiole** — tàu lá | **Cuống lá / tàu lá** và độ rủ | Thấy rõ tàu lá + tư thế (dựng/rủ/gãy) đủ để đánh giá suy tàn | Không thấy tàu lá rõ ràng, chỉ thấy phiến lá rời, quá xa |

> Lưu ý `5_petiole` là tín hiệu **kém đặc hiệu** (tàu lá suy tàn do nhiều nguyên nhân).
> Vẫn gán theo required-view như trên; giới hạn này sẽ ghi rõ khi báo cáo.

## 3. Tiêu chí chất lượng chung (áp cho mọi tác vụ)

Một tác vụ = **0** nếu vi phạm bất kỳ điều nào khiến *không đánh giá được*:

- **Mờ / rung**: mất chi tiết cần thiết (đường gân lá, ranh giới vết bệnh, màu vỏ trái).
- **Phơi sáng**: quá tối hoặc cháy sáng làm mất thông tin màu/bề mặt của đối tượng.
- **Che khuất**: đối tượng bị vật khác/lá khác che phần cần soi.
- **Khoảng cách/độ phân giải**: đối tượng quá nhỏ trong khung, không đủ pixel.
- **Sai đối tượng**: trong khung không có đối tượng mà tác vụ cần.

Ngưỡng thực dụng: *"Nếu tôi là chuyên gia, ảnh này có đủ để tôi kết luận cho tác vụ đó
không?"* — Có → 1, Không → 0.

## 4. Edge cases (xử lý nhất quán)

- **Nhiều đối tượng, một số rõ một số mờ**: chỉ cần ≥1 đối tượng đủ rõ để làm tác vụ → 1.
- **Ảnh chéo tác vụ** (vd ảnh trái dừa nhưng nền có thân cây): xét từng tác vụ độc lập theo
  những gì *thực sự thấy rõ*. Thân ở nền mà mờ/nhỏ → trunk = 0.
- **Cây khỏe mạnh hoàn toàn**: vẫn = 1 cho tác vụ nào mà đối tượng hiện rõ (ta đánh giá được
  "khỏe"). Đừng gán 0 chỉ vì không có bệnh.
- **Ảnh Roboflow bị resize-stretch + auto-contrast**: đây là đặc điểm dữ liệu, không tính là
  "hỏng"; chỉ đánh giá theo nội dung nhìn thấy.
- **Thật sự lưỡng lự sau khi cân nhắc**: dùng **skip (?)**. Đừng đoán bừa. Cuối đợt xem lại
  các ảnh skip.

## 5. Quy trình gán

1. Mở `annotate.html` bằng trình duyệt (xem file này để biết cách).
2. Với mỗi ảnh: nhìn kỹ, xét lần lượt cả 5 tác vụ, tick 1/0 (hoặc skip nếu quá khó).
3. Tiến độ tự lưu trong trình duyệt; gán làm nhiều buổi được.
4. Gán xong 300 ảnh → bấm **Xuất CSV** → lưu file `gold_seed_labels.csv` vào thư mục
   `gold_seed/`.
5. (Khuyến nghị cho κ) Gán lại một tập con ~50 ảnh sau vài ngày, hoặc nhờ người thứ 2 gán
   độc lập, để đo độ đồng thuận Cohen's κ.

## 6. Ghi chú để báo cáo trong paper (§4.3)

Khi hoàn tất, ghi lại: kích thước gold seed (300), chiến lược lấy mẫu (phân tầng cân bằng
60/tác vụ, cấp ảnh gốc, seed=42), số người gán, thời gian, tỷ lệ skip, và Cohen's κ giữa các
lần/người gán.
