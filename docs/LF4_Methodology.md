# LF4 — correctness của tác vụ bệnh đọt/crown (classifier bệnh dùng chung)

LF4 bỏ phiếu hữu dụng cho tác vụ `4_crown_disease`: ảnh hữu dụng nếu classifier bệnh **dùng chung** xếp ảnh vào đúng *view* crown (⇔ đỉnh đọt/ngọn hiện đủ rõ để đánh giá). Dùng **cùng** classifier out-of-fold với LF2/LF3/LF5 — khung, cross-fitting không rò rỉ, tính hợp lệ tín hiệu yếu và cổng go/no-go **giống hệt LF3**: xem `docs/LF3_Methodology.md`. Đây chỉ là bản đổi *view đích* sang crown.

## Ký hiệu và phiếu

GT = thư mục **Bud Rot** (view crown). Miền của LF4 = ảnh có $\text{task}(g(x))=\text{crown}$. Với $\hat{y}(x)$ = lớp dự đoán out-of-fold, $c(x)$ = độ tin, $\tau$ = ngưỡng (calibrate riêng crown trên gold seed):

$$
\lambda_4(x)=
\begin{cases}
\varnothing & \text{nếu } \text{task}(g(x))\neq\text{crown} \ \text{hoặc}\ c(x)<\tau\\
1 & \text{nếu } \text{task}(\hat{y}(x))=\text{crown}\\
0 & \text{ngược lại}
\end{cases}
$$

## Thực tế dữ liệu & đe dọa tính hợp lệ

Bud Rot chỉ **470 ảnh** — lớp **nhỏ nhất** trong 5 thư mục bệnh → classifier dễ nhầm crown sang view khác, LF4 **abstain nhiều / coverage thấp** nhất. View crown (nhìn từ trên xuống đỉnh đọt) hiếm và khó, khớp quan sát LF7 yếu ở crown (xem `docs/Labeling_Plan.md` §5). Là *proxy góc nhìn* (đọc đúng crown ≈ đọt hiện rõ), không phải chẩn đoán bệnh — cùng cảnh báo như LF3. Train **class-weighted** để bù lệch lớp.

## Đầu ra

`notebooks/lf4_crown.ipynb` đọc `labels/disease_clf/oof_predictions.csv`, áp $\lambda_4$, ghi `labels/votes/lf4_crown.csv` (schema chung `src/utils/lf_io.ipynb`; `lf='lf4_crown'`, `task='4_crown_disease'`; cột extra `pred_class, fold`). Kiểm định (α̂, κ, coverage, calibrate τ, go/no-go) ở notebook so sánh riêng trên gold seed.
