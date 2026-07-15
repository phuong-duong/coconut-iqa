# LF2 — correctness của model bệnh-lá (classifier bệnh dùng chung)

LF2 bỏ phiếu hữu dụng cho tác vụ `2_foliar_disease`: ảnh hữu dụng nếu model hạ nguồn đọc **đúng view** so với ground-truth. View foliar có **hai lớp GT** (Gray Leaf Spot, Leaf Rot); một classifier foliar 2-lớp riêng chỉ đo phân biệt hai bệnh cùng view (không có lớp âm ngoài-view), mang tính vòng lặp. Cách giải: dùng **một classifier bệnh đa lớp dùng chung** cho cả bốn tác vụ bệnh (foliar/trunk/crown/petiole); lớp âm của foliar chính là các thư mục bệnh **bộ phận khác** — có sẵn dữ liệu. Correctness được xét ở mức **required-view**: ảnh foliar hữu dụng nếu classifier xếp nó vào đúng *view* foliar (⇔ phiến lá hiện đủ rõ để nhận diện), **không đòi phân biệt** gls↔leafrot. LF2 **abstain** khi thiếu GT foliar hoặc model không đủ tự tin, nên là **phiếu yếu**, phải qua kiểm định gold seed. Cùng classifier này sinh phiếu cho **LF3/LF4/LF5** và cấp anchor cho **LF6** (một model thay cho bốn). (Dùng lại khung LF1/LF3, chỉ đổi view đích.)

## Thực tế dữ liệu (ảnh hưởng độ tin)

Bốn thư mục bệnh (Mendeley gh56wbsnj5), gán về tác vụ theo required-view:

| Tác vụ (view) | Thư mục GT | Số ảnh |
|---|---|---|
| `2_foliar_disease` | Gray Leaf Spot; Leaf Rot | 2135; 1673 |
| `3_trunk_disease` | Stem Bleeding | 1006 |
| `4_crown_disease` | Bud Rot | 470 |
| `5_petiole` | Bud Root Dropping | 514 |

Foliar là view **nhiều mẫu nhất** (3808/5798). Lệch lớp giữa các view mạnh (2135 vs 470) → classifier train **class-weighted**; đo tách theo lớp. Ảnh Mendeley **không có augment ×3** (khác Roboflow) → `original_id` = chính nó. Model chạy **offline sinh nhãn** → ưu tiên chính xác, không cần nhẹ (khác model IQA cuối).

## Kiến trúc classifier (dùng chung, xem docs/LF3_Methodology.md)

Classifier bệnh đa lớp **dùng chung** (EfficientNet-B0, 5 lớp `gls, leafrot, stembleed, budrot, budroot`, class-weighted), chi tiết chọn kiến trúc + lý do ở `docs/LF3_Methodology.md`. Triển khai: `notebooks/disease_classifier.ipynb` → `labels/disease_clf/oof_predictions.csv`. LF2 chỉ **đọc** file oof này, không tự train.

## Ký hiệu và định nghĩa

Lớp thư mục $\mathcal{C}=\{\text{gls, leafrot, stembleed, budrot, budroot}\}$. Ánh xạ view $\text{task}(\cdot)$ đưa mỗi lớp về tác vụ của nó (gls, leafrot $\to$ foliar; stembleed $\to$ trunk; …). Cho ảnh $x$: $g(x)\in\mathcal{C}$ = lớp thật (thư mục nguồn), $\hat{y}(x)$ = lớp dự đoán out-of-fold, $c(x)$ = độ tin, $\tau$ = ngưỡng. Miền của LF2 = ảnh có $\text{task}(g(x))=\text{foliar}$.

$$
\lambda_2(x)=
\begin{cases}
\varnothing \ (\text{abstain}) & \text{nếu } \text{task}(g(x))\neq\text{foliar} \ \text{hoặc}\ c(x)<\tau\\[2pt]
1 & \text{nếu } \text{task}(\hat{y}(x))=\text{foliar}\\[2pt]
0 & \text{ngược lại}
\end{cases}
$$

Xét ở mức **view** vì hữu dụng = *required-view hiện rõ*, không phải chẩn đúng bệnh. Tập chấp nhận của foliar là {gls, leafrot}: dự đoán rơi vào một trong hai ⇒ view-đúng, dù không phân biệt đúng gls↔leafrot.

## Cross-fitting → không rò rỉ (chứng minh)

Chia **theo ảnh gốc** thành $K=5$ fold rời $\{F_1,\dots,F_K\}$ (dùng `fold_of`, md5 `"{seed}:{orig}"` % K, seed=42, chung với LF1/LF6). Với $x\in F_k$ dùng model không có fold $k$:
$$\hat{y}(x)=M_{-k}(x),\qquad x\notin\text{train}(M_{-k}).$$
Mỗi ảnh được dự đoán bởi model chưa từng thấy nó → loại rò rỉ, phủ toàn bộ ảnh. Classifier dùng chung được cross-fit **một lần** trên cả bốn view; mọi LF bệnh đọc cùng bộ dự đoán out-of-fold.

## Tính hợp lệ như tín hiệu yếu (chứng minh)

**Correctness = hữu dụng × năng lực.** Gọi $u(x)$ = xác suất ảnh cho thấy view foliar đủ rõ, $m$ = độ chính xác classifier trên view foliar. Vì model chỉ xếp đúng view khi bộ phận hiện rõ:
$$\Pr\big(\lambda_2(x)=1\big)\approx u(x)\cdot m.$$
$m$ gần như không phụ thuộc từng ảnh → correctness **bảo toàn thứ tự** của $u(x)$ dù $m<1$. Gọi $Y(x)\in\{0,1\}$ = hữu dụng thật, độ chính xác LF2:
$$\alpha_2=\Pr\big(\lambda_2(x)=Y(x)\mid\lambda_2(x)\neq\varnothing\big).$$
Với $\alpha_2>\tfrac12$ và mô hình hóa tương quan giữa các LF, hậu nghiệm $\Pr(Y\mid\lambda_1,\dots,\lambda_{10})$ hội tụ về $Y$. Cổng tin cậy giữ $\alpha_2>\tfrac12$; gold seed cho $\hat\alpha_2$ trực tiếp (kèm Cohen $\kappa$).

**Đe dọa tính hợp lệ (ghi rõ khi báo cáo).** Classifier phân biệt các view chủ yếu theo **bộ phận/góc nhìn**, nên "đọc đúng foliar" ≈ "ảnh cho thấy rõ lá" — đúng thứ cần cho usability, nhưng là *proxy góc nhìn*, không phải chẩn đoán bệnh. Vì ảnh foliar Mendeley đều là cận cảnh lá rõ, view-đúng gần như luôn xảy ra (tín hiệu **gần đơn cực, dương**) → LF2 phân biệt hữu dụng/vô dụng yếu; negative quanh ranh giới phải cậy **LF6 (suy giảm có kiểm soát)**, và độ tin chốt trên gold seed.

## Cổng go/no-go (quyết định có tin LF2 không)

- $\hat\alpha_2>0.5$ **và** độ phủ (không abstain) đủ → LF2 vào label model với trọng số học được.
- $\hat\alpha_2\le0.5$ **hoặc** abstain quá nhiều → **loại LF2**, dựa vào LF6 + gold seed.

Đo $\hat\alpha_2$, $\kappa$, tỉ lệ abstain trên phần gold seed thuộc view foliar. Ngưỡng $\tau$ calibrate riêng cho foliar (không tái dùng ngưỡng tác vụ khác).

## Cơ sở lý thuyết (nghiên cứu trực tiếp)

- **Hữu dụng = hiệu năng tác vụ hạ nguồn (task amenability).** Saeed et al., IPMI 2021 (arXiv 2102.07615); Medical Image Analysis 2022 (arXiv 2203.14258) — phép đo phụ thuộc năng lực predictor, khớp factorization $u(x)\cdot m$.
- **Hợp nhất LF nhiễu hội tụ khi $\alpha>\tfrac12$.** Ratner et al., *Data Programming* (NeurIPS 2016); Snorkel (VLDB 2017).
- **Dữ liệu bệnh:** Mendeley Data gh56wbsnj5 (nguồn 4 thư mục bệnh). Trần độ chính xác classifier chưa cố định → xác lập bằng gold seed, không giả định $m=1$.

## Mã giả

```
# GĐ1: classifier bệnh DÙNG CHUNG, dự đoán out-of-fold (xem disease_classifier.ipynb / LF3)
save oof(pred, conf) -> labels/disease_clf/oof_predictions.csv   # LF2/3/4/5 cùng đọc

# GĐ2: bỏ phiếu LF2 (view = foliar)
def LF2(x):
    if task(g[x]) != foliar or conf[x] < tau:  return ABSTAIN
    return 1 if task(pred[x]) == foliar else 0

# GĐ3: cổng go/no-go trên gold seed (phần view foliar)
alpha_hat, kappa, coverage = validate(LF2, gold_seed_foliar, human_labels)
use LF2 (trọng số học được)  if alpha_hat > 0.5 and coverage đủ  else drop → dựa LF6
```

## Tái lập & đầu ra

seed=42, K=5 (chia theo ảnh gốc, `fold_of` chung); classifier + siêu tham số + class weighting (xem `docs/LF3_Methodology.md`); ngưỡng $\tau$ (calibrate riêng view foliar); ánh xạ $\text{task}(\cdot)$ lớp→view. Đầu ra: `labels/votes/lf2_foliar.csv` (schema chung `src/utils/lf_io.ipynb`; `lf='lf2_foliar'`, `task='2_foliar_disease'`; cột extra `pred_class, fold`); dự đoán dùng chung: `labels/disease_clf/oof_predictions.csv`.
