# LF2 — correctness của model bệnh trên lá

LF2 bỏ phiếu hữu dụng cho tác vụ `2_foliar_disease`: ảnh hữu dụng nếu model bệnh-lá hạ nguồn phân **đúng** lớp foliar so với ground-truth (tên thư mục). Ground-truth là hai lớp `Gray Leaf Spot` / `Leaf Rot` (bộ Mendeley `gh56wbsnj5`), nhãn cấp-ảnh nên model hạ nguồn là **classifier ảnh** (khác LF1 dùng detection vì `coconut-veirf` gán box). Backbone chọn **MobileNetV3-Small** (pretrained ImageNet, có sẵn trong torchvision, không thêm phụ thuộc; bài toán 2 lớp chỉ tinh chỉnh đầu phân loại) — nhất quán với backbone nhẹ của mô hình IQA cuối. Huấn luyện **cross-fitting** để tránh rò rỉ; LF2 **abstain** khi model không đủ tự tin. Vì correctness trộn "hữu dụng của ảnh" với "năng lực model", LF2 là **một phiếu yếu**, phải qua kiểm định gold seed mới được tin. (LF2 dùng lại đúng khung LF1, chỉ thay tín hiệu correctness từ detection sang classification.)

## Thực tế dữ liệu (ảnh hưởng độ tin)

Hai lớp foliar: Gray Leaf Spot **2135** ảnh, Leaf Rot **1673** ảnh (tổng **3808**). Lệch nhẹ (~56% / ~44%) → xử lý bằng class weight khi huấn luyện. Ảnh bệnh Mendeley **không có bản augment** (khác `coconut-veirf` augment ×3) → mỗi ảnh là ảnh gốc của chính nó, chia fold theo từng ảnh.

## Ký hiệu và định nghĩa

Cho ảnh $x$: $G(x)\in\{\text{Gray Leaf Spot},\text{Leaf Rot}\}$ = lớp foliar thật (thư mục nguồn), $\hat{y}(x)$ = lớp dự đoán, $c(x)$ = xác suất softmax của lớp dự đoán, $\tau$ = ngưỡng tin cậy.

$$
\lambda_2(x)=
\begin{cases}
\varnothing \ (\text{abstain}) & \text{nếu } c(x)<\tau\\[2pt]
1 & \text{nếu } \hat{y}(x)=G(x)\\[2pt]
0 & \text{nếu } \hat{y}(x)\neq G(x)
\end{cases}
$$

## Cross-fitting → không rò rỉ (chứng minh)

Chia toàn bộ ảnh foliar thành $K$ fold rời nhau $\{F_1,\dots,F_K\}$, $K=5$, gán fold **tất định bằng md5** của mã ảnh (không phụ thuộc `PYTHONHASHSEED`; cùng hàm `fold_of` với `lf6_degradation.ipynb`). Với $x\in F_k$ dùng model không có fold $k$:
$$\hat{y}(x)=M_{-k}(x),\qquad x\notin \text{train}(M_{-k}).$$
Mỗi ảnh được dự đoán bởi model chưa từng thấy nó → loại rò rỉ, phủ toàn bộ ảnh. Ảnh Mendeley không có augment nên không có rủi ro "bản augment lọt sang holdout" như bộ Roboflow; fold theo từng ảnh là đủ.

## Tính hợp lệ như tín hiệu yếu (chứng minh)

**Trực giác (correctness = hữu dụng × năng lực).** Gọi $u(x)\in[0,1]$ = xác suất ảnh thể hiện lá đủ rõ để phân biệt lớp foliar, $m\in[0,1]$ = năng lực model. Model chỉ phân đúng khi thông tin có sẵn:
$$\Pr\big(\lambda_2(x)=1\big)\;\approx\; u(x)\cdot m .$$
Model yếu ($m$ nhỏ) làm correctness tụt **đồng đều** nhưng vẫn **bảo toàn thứ tự** của $u(x)$ (vì $m$ gần như không phụ thuộc từng ảnh) → tín hiệu còn dùng được dù $m<1$. Do $m<1$ chắc chắn → **bắt buộc** có abstain + kiểm định.

Gọi $Y(x)\in\{0,1\}$ = hữu dụng thật; độ chính xác LF2:
$$\alpha_2=\Pr\big(\lambda_2(x)=Y(x)\mid \lambda_2(x)\neq\varnothing\big).$$
Label model ước lượng $\alpha_2$ từ đồng thuận giữa các LF; với $\alpha_2>\tfrac12$ và mô hình hóa tương quan, hậu nghiệm $\Pr(Y\mid \lambda_1,\dots,\lambda_{10})$ hội tụ về $Y$. Cổng tin cậy giữ $\alpha_2>\tfrac12$ (loại phiếu sai-mà-tự-tin); gold seed cho ước lượng trực tiếp $\hat\alpha_2$ (kèm Cohen $\kappa$).

## Cổng go/no-go (quyết định có tin LF2 không)

- $\hat\alpha_2>0.5$ **và** độ phủ (không abstain) đủ → LF2 vào label model với trọng số học được.
- $\hat\alpha_2\le0.5$ **hoặc** abstain quá nhiều → **loại LF2**, dựa vào LF6 + gold seed.

Đo $\hat\alpha_2$, $\kappa$, tỉ lệ abstain **tách theo từng lớp** Gray Leaf Spot / Leaf Rot.

## Cơ sở lý thuyết (nghiên cứu trực tiếp)

- **Hữu dụng = hiệu năng tác vụ hạ nguồn (task amenability).** Saeed et al. — IPMI 2021 (arXiv 2102.07615); Medical Image Analysis 2022 (arXiv 2203.14258). Khớp factorization $u(x)\cdot m$.
- **Hợp nhất LF nhiễu hội tụ khi $\alpha>\tfrac12$.** Ratner et al., *Data Programming* (NeurIPS 2016); Snorkel (VLDB 2017).
- **Backbone nhẹ MobileNetV3.** Howard et al., *Searching for MobileNetV3*, ICCV 2019 (arXiv 1905.02244).
- **Nguồn ground-truth foliar.** Coconut Tree Disease Dataset, Mendeley Data `gh56wbsnj5` (Gray Leaf Spot, Leaf Rot).

## Mã giả

```
# GĐ1: dự đoán out-of-fold (cross-fitting), fold tất định theo mã ảnh
folds = {x: md5(seed:x) mod K for x in images_foliar}   # ảnh Mendeley: 1 ảnh = 1 ảnh gốc
for k in 1..K:
    M_k = train_classifier(train = images[fold != k], class_weighted=True)  # không có fold k
    for x in images[fold == k]:
        pred[x], conf[x] = M_k.predict(x)               # x chưa từng thấy

# GĐ2: bỏ phiếu LF2
def LF2(x):
    if conf[x] < tau:            return ABSTAIN
    return 1 if pred[x] == G(x) else 0

# GĐ3: cổng go/no-go trên gold seed
alpha_hat, kappa, coverage = validate(LF2, gold_seed, human_labels, per_class=True)
use LF2 (trọng số học được)  if alpha_hat > 0.5 and coverage đủ  else drop → dựa LF6
```

## Tái lập & đầu ra

seed=42, K=5 (fold md5 theo mã ảnh); kiến trúc MobileNetV3-Small + siêu tham số (imgsz, epochs, batch, lr) + class weighting; early-stopping theo val loss trên val split nội bộ (`VAL_FRAC` tách phân tầng từ K−1 fold train, không đụng fold OOF), giữ trọng số tốt nhất; ngưỡng $\tau$; định nghĩa correctness (khớp lớp dự đoán ↔ lớp thư mục). Kết quả ghi `labels/votes/lf2_foliar.csv` theo schema chung (`src/utils/lf_io.ipynb`).
