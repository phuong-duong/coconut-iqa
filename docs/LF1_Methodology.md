# LF1 — correctness của model độ chín

LF1 bỏ phiếu hữu dụng cho tác vụ `1_maturity_evaluation`: ảnh hữu dụng nếu model độ chín hạ nguồn đọc **đúng** mức chín so với ground-truth. Model hạ nguồn là **YOLOv8 detection** (nhãn `coconut-veirf` là bounding box nhiều-trái/ảnh; Mask R-CNN bị loại vì bộ dữ liệu không có mask, Faster R-CNN là phương án dự phòng), huấn luyện **cross-fitting** để tránh rò rỉ, và LF1 **abstain** khi thiếu ground-truth hoặc model không đủ tự tin. Vì correctness trộn lẫn "hữu dụng của ảnh" và "năng lực model", LF1 là **một phiếu yếu**, phải qua kiểm định gold seed mới được tin. Đầu tư cho LF1 giữ ở mức **nhẹ**: nó là *minh chứng nguyên lý* task-driven, còn tín hiệu hữu dụng chủ lực là LF6 (suy giảm có kiểm soát). (Các LF khác dùng lại đúng khung này, chỉ thay tín hiệu.)

## Thực tế dữ liệu (ảnh hưởng độ tin)

`coconut-veirf` v5: 948 ảnh từ **399 ảnh gốc** (Roboflow augment ~2.4×), tổng **1232 box** — dry **227** / green **320** / tender **685**. Lệch **vừa phải** (tender ~56%, green ~26%, dry ~18%): dry/green vẫn đủ dữ liệu để train, nhưng LF1 đáng tin nhất ở `tender` và **abstain nhiều hơn** ở `dry`/`green`. Đây là giới hạn dữ liệu, không phải lỗi phương pháp.

## Ký hiệu và định nghĩa

Cho ảnh $x$: $G(x)$ = tập mức chín thật (nhãn YOLO), $\hat{y}(x)$ = mức chín dự đoán, $c(x)$ = độ tin cậy, $\tau$ = ngưỡng.

$$
\lambda_1(x)=
\begin{cases}
\varnothing \ (\text{abstain}) & \text{nếu } G(x)=\emptyset \ \text{hoặc}\ c(x)<\tau\\[2pt]
1 & \text{nếu } \hat{y}(x)\in G(x)\\[2pt]
0 & \text{ngược lại}
\end{cases}
$$

Correctness so bằng cách ghép cặp box dự đoán ↔ box thật theo IoU rồi so lớp (chặt hơn so cấp ảnh).

## Cross-fitting → không rò rỉ (chứng minh)

Chia **theo ảnh gốc** (gom mọi biến thể augmentation của một ảnh vào cùng fold) thành $K$ fold rời nhau $\{F_1,\dots,F_K\}$, $K=5$. Với $x\in F_k$ dùng model không có fold $k$:
$$\hat{y}(x)=M_{-k}(x),\qquad x\notin \text{train}(M_{-k}).$$
Mỗi ảnh được dự đoán bởi model chưa từng thấy nó (kể cả bản augment của nó) → loại rò rỉ, phủ toàn bộ ảnh. *Lưu ý: chia theo file thay vì theo ảnh gốc sẽ làm bản augment lọt sang holdout = rò rỉ.*

## Tính hợp lệ như tín hiệu yếu (chứng minh)

**Trực giác (correctness = hữu dụng × năng lực).** Gọi $u(x)\in[0,1]$ = xác suất ảnh chứa đủ thông tin độ chín, $m\in[0,1]$ = năng lực model. Vì model chỉ đọc đúng khi thông tin có sẵn:
$$\Pr\big(\lambda_1(x)=1\big)\;\approx\; u(x)\cdot m .$$
Model yếu ($m$ nhỏ) làm correctness tụt **đồng đều**; nhưng $m$ gần như không phụ thuộc từng ảnh nên correctness vẫn **bảo toàn thứ tự** của $u(x)$ — lý do tín hiệu còn dùng được dù model chưa hoàn hảo. Trần thực tế của model độ chín dừa chỉ ~86.3% (Megalingam 2024), tức $m<1$ chắc chắn → **bắt buộc** phải có abstain + kiểm định.

Gọi $Y(x)\in\{0,1\}$ = hữu dụng thật; độ chính xác LF1:
$$\alpha_1=\Pr\big(\lambda_1(x)=Y(x)\mid \lambda_1(x)\neq\varnothing\big).$$
Label model ước lượng $\alpha_1$ từ đồng thuận giữa các LF; với $\alpha_1>\tfrac12$ và mô hình hóa tương quan, hậu nghiệm $\Pr(Y\mid \lambda_1,\dots,\lambda_{10})$ hội tụ về $Y$. Cổng tin cậy giữ $\alpha_1>\tfrac12$ (loại phiếu sai-mà-tự-tin); gold seed cho ước lượng trực tiếp $\hat\alpha_1$ (kèm Cohen $\kappa$).

## Cổng go/no-go (quyết định có tin LF1 không)

- $\hat\alpha_1>0.5$ **và** độ phủ (không abstain) đủ → LF1 vào label model với trọng số học được.
- $\hat\alpha_1\le0.5$ **hoặc** abstain quá nhiều → **loại LF1**, dựa vào LF6 + gold seed.

Đo $\hat\alpha_1$, $\kappa$, tỉ lệ abstain **tách theo từng lớp** dry/green/tender (dry/green nhiều khả năng không đạt).

## Cơ sở lý thuyết (nghiên cứu trực tiếp)

- **Hữu dụng = hiệu năng tác vụ hạ nguồn (task amenability).** Saeed et al. định nghĩa khái niệm này và chỉ rõ phép đo phụ thuộc năng lực predictor, xử lý bằng đồng huấn luyện controller — khớp factorization $u(x)\cdot m$. IPMI 2021 (arXiv 2102.07615); Medical Image Analysis 2022 (arXiv 2203.14258).
- **Hợp nhất LF nhiễu hội tụ khi $\alpha>\tfrac12$.** Ratner et al., *Data Programming* (NeurIPS 2016); Snorkel (VLDB 2017).
- **Trần độ chính xác model độ chín dừa ~86.3%.** Megalingam et al., *Integrated fuzzy and deep learning model...*, Neural Computing and Applications 2024 (arXiv/DOI 10.1007/s00521-023-09402-2) — cũng benchmark Mask R-CNN vs YOLOv5 vs Faster R-CNN.

## Mã giả

```
# GĐ1: dự đoán out-of-fold (cross-fitting), chia theo ẢNH GỐC
groups = group_by_original_image(images_maturity)   # gộp bản augment
folds  = split(groups, K=5, seed=42)
for k in 1..K:
    M_k = train_yolov8(train = groups \ folds[k], class_weighted=True)  # không có fold k
    for x in folds[k]:
        pred[x], conf[x] = M_k.predict(x)            # x (và augment của nó) chưa từng thấy

# GĐ2: bỏ phiếu LF1
def LF1(x):
    if G(x) is empty or conf[x] < tau:  return ABSTAIN
    return 1 if iou_match(pred[x], G(x)) else 0

# GĐ3: cổng go/no-go trên gold seed
alpha_hat, kappa, coverage = validate(LF1, gold_seed, human_labels, per_class=True)
use LF1 (trọng số học được)  if alpha_hat > 0.5 and coverage đủ  else drop → dựa LF6
```

## Tái lập & đầu ra

seed=42, K=5 (chia theo ảnh gốc); phiên bản YOLOv8 + siêu tham số + class weighting; ngưỡng $\tau$; định nghĩa correctness (ghép cặp IoU). Kết quả điền cột `1_maturity_evaluation` trong `labels/lf1-5_correctness_manifest.csv`.
