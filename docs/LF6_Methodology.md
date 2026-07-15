# LF6 — điểm gãy dưới suy giảm có kiểm soát

LF6 bỏ phiếu hữu dụng cho **mọi tác vụ** bằng cách trả lời câu hỏi nhân quả: *giữ nguyên nội dung ảnh, chất lượng phải tệ tới mức nào thì tác vụ hạ nguồn mới hỏng?* Ta lấy **ảnh anchor** (ảnh mà model hạ nguồn làm đúng, tự tin cao — tức hữu dụng gần chắc chắn), rồi **suy giảm có kiểm soát** theo từng trục lỗi chụp thật (mờ, phơi sáng, phân giải/nén, che khuất, cân bằng trắng), tăng dần cường độ $\delta$ cho tới khi tác vụ **thất bại**. Điểm chuyển 1→0 đó là **điểm gãy** $\delta^\*$. Ảnh suy giảm nhẹ hơn điểm gãy → phiếu `1`; nặng hơn → phiếu `0`. Vì chỉ đổi chất lượng còn nội dung/khung hình giữ nguyên, thay đổi thành–bại **quy được về đúng trục chất lượng** (phản-thực): đây là điều LF1–LF5 không làm được, nên LF6 là **tín hiệu chủ lực, mạnh về nhân quả**. LF6 và LF1–LF5 **bù nhau**: correctness đo *nội dung/khung hình có đúng không*, LF6 đo *chất lượng có đủ không* — hai nửa của "hữu dụng". LF6 **abstain** khi ảnh gốc không phải anchor, hoặc trục suy giảm không liên quan tác vụ. (LF6 dùng lại đúng khung cross-fitting của LF1, chỉ thay tín hiệu.)

## Thực tế dữ liệu (ảnh hưởng độ tin)

LF6 cần **anchor**, mà anchor lấy từ correctness LF1–LF5 — hiện năm cột nhãn còn trống (model hạ nguồn còn là stub), nên LF6 chạy được **sau khi** có model hạ nguồn. Anchor dồi dào ở `tender` (685 box) và các lớp bệnh lớn (Gray Leaf Spot 2.135, Leaf Rot 1.673, Stem Bleeding 1.006), **thưa** ở Bud Rot (470) và Bud Root Dropping (514). Cảnh báo quan trọng: ảnh độ chín (Roboflow) **đã bị tiền xử lý sẵn** (resize stretch, auto-contrast, tăng phơi sáng ×3). Suy giảm trục phơi sáng/tương phản/nén trên anchor độ chín là **nhiễu loạn trên nền đã méo** → với `1_maturity_evaluation`, LF6 chỉ dùng trục **chưa bị nguồn làm hỏng** (mờ, che khuất, phân giải), **abstain** trên phơi sáng/tương phản. Đây là giới hạn nguồn, không phải lỗi phương pháp.

## Ký hiệu và định nghĩa

Cho tác vụ $t$, tập trục $a\in\mathcal{A}=\{\text{blur, exposure, resolution/nén, occlusion, white-balance}\}$. Toán tử suy giảm $D_a(x,\delta)$ áp lỗi trục $a$ cường độ $\delta\ge 0$, với $D_a(x,0)=x$ và **đơn điệu theo $\delta$** (lớn hơn = tệ hơn). Anchor của tác vụ $t$:
$$A_t=\{x:\ \lambda^{\text{corr}}_t(x)=1\ \wedge\ c(x)>\tau_{\text{high}}\}\quad(\text{dùng dự đoán out-of-fold}).$$
Chỉ báo thành công tác vụ trên ảnh suy giảm $x'=D_a(x,\delta)$: $s_t(x')\in\{0,1\}$ (model đọc đúng như định nghĩa correctness của tác vụ). **Điểm gãy** trên bao đơn điệu:
$$\delta^\*_a(x,t)=\min\{\delta:\ \bar s_t(D_a(x,\delta))=0\},\qquad \bar s_t(D_a(x,\delta))=\min_{\delta'\le\delta}s_t(D_a(x,\delta')).$$
$\bar s_t$ là **bao tích lũy** (một khi hỏng thì coi như hỏng ở mọi $\delta$ lớn hơn) → khử nhiễu răng cưa, cho **một** điểm gãy duy nhất. Phiếu LF6 trên ảnh suy giảm $x'=D_a(x,\delta)$:

$$
\lambda_6(x';t,a)=
\begin{cases}
\varnothing\ (\text{abstain}) & x\notin A_t\ \text{hoặc}\ a\notin \mathcal{A}(t)\ \text{hoặc}\ |\delta-\delta^\*_a(x,t)|<\varepsilon\\[2pt]
1 & \delta<\delta^\*_a(x,t)\\[2pt]
0 & \delta\ge \delta^\*_a(x,t)
\end{cases}
$$

$\mathcal{A}(t)$ = trục liên quan tác vụ $t$ (loại phơi sáng/tương phản khỏi độ chín). $\varepsilon$ = **cổng biên**: bỏ phiếu quanh điểm gãy vì đó là nơi nhiễu nhãn tập trung.

## Cross-fitting → không rò rỉ (chứng minh)

Hai nguồn rò rỉ, chặn cả hai:
1. **Model chấm lại phải out-of-fold.** Với $x\in F_k$, chấm thành–bại bằng $M_{-k}$ (model không có fold $k$): $s_t(D_a(x,\delta))=\text{success}\big(M_{-k}(D_a(x,\delta)),G(x)\big)$. Nếu dùng model từng thấy $x$, nó "nhớ" nội dung và tỏ ra bền giả tạo → điểm gãy bị đẩy lệch.
2. **Biến thể suy giảm thừa hưởng nhóm của ảnh gốc.** Mọi $D_a(x,\delta)$ (và bản augment Roboflow của $x$) nằm **cùng fold/split với $x$** khi chia theo ảnh gốc. Nếu để ảnh suy giảm của $x$ lọt sang holdout = gần-trùng rò rỉ.

Kết hợp: mỗi ảnh suy giảm được chấm bởi model chưa từng thấy ảnh gốc của nó, và không ảnh suy giảm nào vượt ranh giới split → điểm gãy đo được là **out-of-fold thật**.

## Tính hợp lệ như tín hiệu yếu (chứng minh)

**Cô lập nhân quả.** Giữ nội dung ảnh $x$ cố định, chỉ đổi $\delta$ trên một trục:
$$s_t(D_a(x,\delta_2))-s_t(D_a(x,\delta_1))\ \text{chỉ do } (\delta_2-\delta_1)\ \text{gây ra}.$$
Vì $x$ là anchor (hữu dụng ở $\delta=0$), việc tác vụ hỏng khi $\delta$ tăng **buộc phải** do chất lượng tụt — đúng nghĩa "ảnh hết đủ thông tin". Đây là lý do LF6 mạnh hơn correctness thuần: correctness trộn "hữu dụng × năng lực model" ($u(x)\cdot m$), còn LF6 **khóa nội dung**, cho quan hệ $\text{chất lượng}\to\text{thành bại}$ gần như thuần.

**Đơn điệu ⇒ một điểm gãy ⇒ độ chính xác cao.** Thêm mờ/nén không bao giờ *tăng* thông tin, nên $s_t$ (sau lấy bao $\bar s_t$) đơn điệu không tăng theo $\delta$ → tồn tại **một** điểm gãy. Do đó phiếu ở xa điểm gãy gần như chắc đúng (nhẹ = còn dùng, cực nặng = hỏng); nhiễu nhãn dồn vào lân cận $\delta^\*$, đã bị cổng biên $\varepsilon$ hớt đi. Gọi $Y(x')$ = hữu dụng thật, độ chính xác LF6:
$$\alpha_6=\Pr\big(\lambda_6=Y\mid \lambda_6\neq\varnothing\big).$$
Cô lập nhân quả + cổng biên đẩy $\alpha_6$ lên cao ($\gg\tfrac12$); với $\alpha_6>\tfrac12$, hợp nhất weak-supervision hội tụ về $Y$ (Ratner/Snorkel). Gold seed cho $\hat\alpha_6$ trực tiếp (kèm Cohen $\kappa$).

**Độ bền điểm gãy.** Đo $\delta^\*$ trên nhiều fold cross-fit (và tùy chọn nhiều model/TTA). Nếu $\delta^\*$ tản mạn lớn giữa các fold → nới $\varepsilon$ hoặc abstain (điểm gãy không đáng tin cho ảnh đó).

## Cạm bẫy tương quan

LF6 sinh **nhiều phiếu tương quan** trên cùng ảnh gốc (nhiều $\delta$, nhiều trục) và **cùng nhìn tín hiệu chất lượng** như mọi heuristic mờ/phơi sáng (vd LF7, tiền kiểm Tầng 1). Không coi các phiếu này độc lập: để label model **mô hình hóa tương quan** (nhóm theo ảnh gốc và theo trục), nếu không sẽ đếm trùng bằng chứng và tự tin giả.

## Cổng go/no-go (quyết định có tin LF6 không)

- $\hat\alpha_6>0.5$ **và** điểm gãy đủ bền (tản mạn giữa fold nhỏ) → LF6 vào label model với trọng số học được; kỳ vọng đây là **trụ chính**.
- $\hat\alpha_6\le0.5$ **hoặc** điểm gãy loạn → siết $\varepsilon$/loại trục xấu, hoặc bỏ trục đó.

Đo $\hat\alpha_6$, $\kappa$, độ phủ **tách theo từng tác vụ × từng trục** (độ chín thiếu trục phơi sáng; Bud Rot/Bud Root Dropping ít anchor nên phủ hẹp).

## Cơ sở lý thuyết (nghiên cứu trực tiếp)

- **Điều kiện ảnh xấu làm hỏng tác vụ thị giác (bằng chứng nhân quả trục chất lượng).** Tran, Ta, Nguyen, *Evaluating YOLOv11 for Traffic Object Detection Under Adverse Weather Conditions*, FDSE 2025 Part II, tr. 300–314 (DOI 10.1007/978-981-95-4724-1_21) — khớp trực tiếp ý "suy giảm → detection thất bại". Bổ trợ độ bền phân loại: Nguyen et al., *Robust ResNet-Based Models for Skin Lesion Detection*, cùng tuyển tập, tr. 268–282 (DOI 10.1007/978-981-95-4724-1_19).
- **Hữu dụng = hiệu năng tác vụ hạ nguồn (task amenability).** Saeed et al., IPMI 2021 (arXiv 2102.07615); Medical Image Analysis 2022 (arXiv 2203.14258) — LF6 là phép đo task-amenability *phản-thực* dọc trục chất lượng.
- **Hợp nhất LF nhiễu hội tụ khi $\alpha>\tfrac12$.** Ratner et al., *Data Programming* (NeurIPS 2016); Snorkel (VLDB 2017).

## Mã giả

```
# GĐ1: chọn anchor (ảnh model làm ĐÚNG, out-of-fold, tự tin cao)
for t in tasks:
    A_t = { x : lambda_corr_t(x)==1 and conf_oof[x] > tau_high }

# GĐ2: suy giảm có kiểm soát + dò điểm gãy (bao đơn điệu)
axes = {blur, exposure, resolution/nen, occlusion, white_balance}
for t in tasks:
  for x in A_t:
    for a in axes_relevant(t):                 # loai exposure/contrast khoi maturity
      s = []
      for delta in grid(a):                    # 0 = goc, tang dan
          xp = D_a(x, delta)
          s.append( success( M_minus_fold(x)(xp), G(x) ) )   # model out-of-fold cham lai
      s_bar = cummin(s)                         # bao don dieu: hong roi coi nhu hong
      delta_star[a] = first delta where s_bar == 0     # else = +inf (khong hong)

# GĐ3: bo phieu LF6 tren cac anh suy giam
def LF6(x, t, a, delta):
    if x not in A_t or a not in axes_relevant(t):      return ABSTAIN
    d_star = delta_star[a]
    if abs(delta - d_star) < eps:                      return ABSTAIN   # cong bien
    return 1 if delta < d_star else 0

# GĐ4: cong go/no-go tren gold seed
alpha_hat, kappa, coverage = validate(LF6, gold_seed, per_task=True, per_axis=True)
use LF6 (trong so hoc duoc) if alpha_hat > 0.5 and break_stable else siet eps / bo truc
```

## Tái lập & đầu ra

seed=42, K=5 (chia theo ảnh gốc; ảnh suy giảm thừa hưởng nhóm của ảnh gốc); thư viện + **lưới tham số từng trục** $\text{grid}(a)$; $\tau_{\text{high}}$ chọn anchor; cổng biên $\varepsilon$; định nghĩa bao đơn điệu $\bar s$ và điểm gãy; định nghĩa `success` theo đúng correctness của từng tác vụ; danh sách $\mathcal{A}(t)$ (trục loại khỏi độ chín). LF6 sinh ảnh mới nên ghi ra manifest riêng `labels/lf6_degradation_manifest.csv` (cột: `base_image, task, axis, delta, delta_star, vote`), tách khỏi `lf1-5_correctness_manifest.csv`.
