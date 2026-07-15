# LF3 — correctness của model bệnh-thân (classifier bệnh dùng chung)

LF3 bỏ phiếu hữu dụng cho tác vụ `3_trunk_disease`: ảnh hữu dụng nếu model hạ nguồn đọc **đúng** so với ground-truth. Tác vụ trunk chỉ có **một lớp GT** (Stem Bleeding) nên correctness một-lớp suy biến (chỉ đo phát hiện, mang tính vòng lặp) và không có "thân khỏe" làm lớp âm. Cách giải: dùng **một classifier bệnh đa lớp dùng chung** cho cả bốn tác vụ bệnh (foliar/trunk/crown/petiole); lớp âm của trunk chính là các thư mục bệnh **bộ phận khác** — có sẵn dữ liệu. Correctness được xét ở mức **required-view**: ảnh Stem Bleeding hữu dụng cho trunk nếu classifier xếp nó vào đúng *view* trunk (⇔ bề mặt thân hiện đủ rõ để nhận diện). LF3 **abstain** khi thiếu GT trunk hoặc model không đủ tự tin, nên là **phiếu yếu**, phải qua kiểm định gold seed. Cùng classifier này sinh phiếu cho **LF2/LF4/LF5** và cấp anchor cho **LF6** (một model thay cho bốn). (Dùng lại khung LF1, chỉ thay tín hiệu.)

## Thực tế dữ liệu (ảnh hưởng độ tin)

Bốn thư mục bệnh (Mendeley gh56wbsnj5), gán về tác vụ theo required-view:

| Tác vụ (view) | Thư mục GT | Số ảnh |
|---|---|---|
| `2_foliar_disease` | Gray Leaf Spot; Leaf Rot | 2135; 1673 |
| `3_trunk_disease` | Stem Bleeding | 1006 |
| `4_crown_disease` | Bud Rot | 470 |
| `5_petiole` | Bud Root Dropping | 514 |

Lệch lớp **mạnh** (2135 vs 470) → train **class-weighted**; đo tách theo lớp. Ảnh Mendeley **không có augment ×3** (khác Roboflow) → `original_id` = chính nó. Model chạy **offline sinh nhãn** → ưu tiên chính xác, không cần nhẹ (khác model IQA cuối).

## Ký hiệu và định nghĩa

Lớp thư mục $\mathcal{C}=\{\text{gls, leafrot, stembleed, budrot, budroot}\}$. Ánh xạ view $\text{task}(\cdot)$ đưa mỗi lớp về tác vụ của nó (gls, leafrot $\to$ foliar; stembleed $\to$ trunk; …). Cho ảnh $x$: $g(x)\in\mathcal{C}$ = lớp thật (thư mục nguồn), $\hat{y}(x)$ = lớp dự đoán out-of-fold, $c(x)$ = độ tin, $\tau$ = ngưỡng. Miền của LF3 = ảnh có $\text{task}(g(x))=\text{trunk}$.

$$
\lambda_3(x)=
\begin{cases}
\varnothing \ (\text{abstain}) & \text{nếu } \text{task}(g(x))\neq\text{trunk} \ \text{hoặc}\ c(x)<\tau\\[2pt]
1 & \text{nếu } \text{task}(\hat{y}(x))=\text{trunk}\\[2pt]
0 & \text{ngược lại}
\end{cases}
$$

Xét ở mức **view** (không đòi phân biệt bệnh cùng view) vì hữu dụng = *required-view hiện rõ*, không phải chẩn đúng bệnh. Trunk chỉ một thư mục nên view-đúng ⇔ lớp-đúng; với foliar (LF2) tập chấp nhận là {gls, leafrot}.

## Cross-fitting → không rò rỉ (chứng minh)

Chia **theo ảnh gốc** thành $K=5$ fold rời $\{F_1,\dots,F_K\}$ (dùng `fold_of`, md5 `"{seed}:{orig}"` % K, seed=42, chung với LF1/LF6). Với $x\in F_k$ dùng model không có fold $k$:
$$\hat{y}(x)=M_{-k}(x),\qquad x\notin\text{train}(M_{-k}).$$
Mỗi ảnh được dự đoán bởi model chưa từng thấy nó → loại rò rỉ, phủ toàn bộ ảnh. Classifier dùng chung được cross-fit **một lần** trên cả bốn view; mọi LF bệnh đọc cùng bộ dự đoán out-of-fold.

## Tính hợp lệ như tín hiệu yếu (chứng minh)

**Correctness = hữu dụng × năng lực.** Gọi $u(x)$ = xác suất ảnh cho thấy view trunk đủ rõ, $m$ = độ chính xác classifier trên view trunk. Vì model chỉ xếp đúng view khi bộ phận hiện rõ:
$$\Pr\big(\lambda_3(x)=1\big)\approx u(x)\cdot m.$$
$m$ gần như không phụ thuộc từng ảnh → correctness **bảo toàn thứ tự** của $u(x)$ dù $m<1$. Gọi $Y(x)\in\{0,1\}$ = hữu dụng thật, độ chính xác LF3:
$$\alpha_3=\Pr\big(\lambda_3(x)=Y(x)\mid\lambda_3(x)\neq\varnothing\big).$$
Với $\alpha_3>\tfrac12$ và mô hình hóa tương quan giữa các LF, hậu nghiệm $\Pr(Y\mid\lambda_1,\dots,\lambda_{10})$ hội tụ về $Y$. Cổng tin cậy giữ $\alpha_3>\tfrac12$; gold seed cho $\hat\alpha_3$ trực tiếp (kèm Cohen $\kappa$).

**Đe dọa tính hợp lệ (ghi rõ khi báo cáo).** Classifier phân biệt các view chủ yếu theo **bộ phận/góc nhìn**, nên "đọc đúng trunk" ≈ "ảnh cho thấy rõ thân" — đúng thứ cần cho usability, nhưng là *proxy góc nhìn*, không phải chẩn đoán bệnh. Ảnh nền/nhầm bộ phận có thể bị model tự tin sai → cổng tin cậy + gold seed để chặn.

## Cổng go/no-go (quyết định có tin LF3 không)

- $\hat\alpha_3>0.5$ **và** độ phủ (không abstain) đủ → LF3 vào label model với trọng số học được.
- $\hat\alpha_3\le0.5$ **hoặc** abstain quá nhiều → **loại LF3**, dựa vào LF6 + gold seed.

Đo $\hat\alpha_3$, $\kappa$, tỉ lệ abstain trên phần gold seed thuộc view trunk. Ngưỡng $\tau$ calibrate riêng cho trunk (không tái dùng ngưỡng tác vụ khác).

## Cơ sở lý thuyết (nghiên cứu trực tiếp)

- **Hữu dụng = hiệu năng tác vụ hạ nguồn (task amenability).** Saeed et al., IPMI 2021 (arXiv 2102.07615); Medical Image Analysis 2022 (arXiv 2203.14258) — phép đo phụ thuộc năng lực predictor, khớp factorization $u(x)\cdot m$.
- **Hợp nhất LF nhiễu hội tụ khi $\alpha>\tfrac12$.** Ratner et al., *Data Programming* (NeurIPS 2016); Snorkel (VLDB 2017).
- **Dữ liệu bệnh:** Mendeley Data gh56wbsnj5 (nguồn 4 thư mục bệnh). Trần độ chính xác classifier chưa cố định → xác lập bằng gold seed, không giả định $m=1$.

## Mã giả

```
# GĐ1: classifier bệnh DÙNG CHUNG, dự đoán out-of-fold (chia theo ẢNH GỐC)
imgs   = disease_images(folders = [gls, leafrot, stembleed, budrot, budroot])
groups = group_by_original_image(imgs)          # ảnh Mendeley: orig = chính nó
folds  = split(groups, K=5, seed=42)            # fold_of dùng chung LF1/LF6
for k in 1..K:
    M_k = train_classifier(train = groups \ folds[k], class_weighted=True)  # không có fold k
    for x in folds[k]:
        pred[x], conf[x] = M_k.predict(x)
save oof(pred, conf) -> labels/disease_clf/oof_predictions.csv   # LF2/3/4/5 cùng đọc

# GĐ2: bỏ phiếu LF3 (view = trunk)
def LF3(x):
    if task(g[x]) != trunk or conf[x] < tau:  return ABSTAIN
    return 1 if task(pred[x]) == trunk else 0

# GĐ3: cổng go/no-go trên gold seed (phần view trunk)
alpha_hat, kappa, coverage = validate(LF3, gold_seed_trunk, human_labels)
use LF3 (trọng số học được)  if alpha_hat > 0.5 and coverage đủ  else drop → dựa LF6
```

## Kế hoạch triển khai

1. **Classifier dùng chung (bước/notebook riêng)** — cross-fit 4 view (5 thư mục), class-weighted, **placeholder-first** (chưa có model → abstain hết → file rỗng, pipeline vẫn chạy). Kiến trúc: transfer nhẹ (MobileNetV3 / EfficientNet-Lite / timm), chọn + lý do ghi ở doc, không narrate trong notebook. Đầu ra: `labels/disease_clf/oof_predictions.csv` (`image_id, pred, conf, fold`).
2. **LF3** `notebooks/lf3_trunk.ipynb` — đọc oof, lọc ảnh view trunk, áp công thức $\lambda_3$, ghi `labels/votes/lf3_trunk.csv` (schema chung `src/utils/lf_io.ipynb`; `lf='lf3_trunk'`, `task='3_trunk_disease'`; cột extra `pred, conf, fold`).
3. **Tái dùng** — LF2/LF4/LF5 đọc **cùng** oof, đổi view đích (foliar/crown/petiole) → mỗi LF một file `labels/votes/lf<N>_*.csv`.
4. **LF6** đọc các file votes để chọn anchor (đúng & `conf>TAU_HIGH`) thay vì re-infer tại delta=0.
5. **Kiểm định** — sau khi mọi LF xong, notebook so sánh riêng đo $\hat\alpha$, $\kappa$, coverage theo từng view trên gold seed; calibrate $\tau$; áp cổng go/no-go. (Không nhét so sánh vào notebook LF3.)

**Nút thắt & đòn bẩy:** classifier dùng chung là điều kiện tiên quyết cho LF2–5 và anchor LF6; làm một lần, mở khóa bốn LF correctness cùng lúc.

## Tái lập & đầu ra

seed=42, K=5 (chia theo ảnh gốc, `fold_of` chung); kiến trúc classifier + siêu tham số + class weighting; ngưỡng $\tau$ (calibrate riêng view trunk); ánh xạ $\text{task}(\cdot)$ lớp→view. Đầu ra: `labels/votes/lf3_trunk.csv`; dự đoán dùng chung: `labels/disease_clf/oof_predictions.csv`.
