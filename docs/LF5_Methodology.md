# LF5 — correctness của tác vụ tình trạng tàu lá/petiole (classifier bệnh dùng chung)

LF5 bỏ phiếu hữu dụng cho tác vụ `5_petiole`: ảnh hữu dụng nếu classifier bệnh **dùng chung** xếp ảnh vào đúng *view* petiole (⇔ cuống lá / độ rủ của tàu lá hiện đủ rõ để nhận định). Dùng **cùng** classifier out-of-fold với LF2/LF3/LF4 — khung, cross-fitting không rò rỉ, tính hợp lệ tín hiệu yếu và cổng go/no-go **giống hệt LF3**: xem `docs/LF3_Methodology.md`. Đây chỉ là bản đổi *view đích* sang petiole.

## Ký hiệu và phiếu

GT = thư mục **Bud Root Dropping** (view petiole). Miền của LF5 = ảnh có $\text{task}(g(x))=\text{petiole}$. Với $\hat{y}(x)$ = lớp dự đoán out-of-fold, $c(x)$ = độ tin, $\tau$ = ngưỡng (calibrate riêng petiole trên gold seed):

$$
\lambda_5(x)=
\begin{cases}
\varnothing & \text{nếu } \text{task}(g(x))\neq\text{petiole} \ \text{hoặc}\ c(x)<\tau\\
1 & \text{nếu } \text{task}(\hat{y}(x))=\text{petiole}\\
0 & \text{ngược lại}
\end{cases}
$$

## Thực tế dữ liệu & đe dọa tính hợp lệ

GT = Bud Root Dropping (**514 ảnh**). Hai cảnh báo:
- **Tín hiệu kém đặc hiệu.** Suy tàn tàu lá (độ rủ, vàng úa) do **nhiều nguyên nhân**, nên `5_petiole` phù hợp **sàng lọc bước đầu** hơn là chẩn xác; xác nhận bệnh rễ/rụng chồi cần quan sát rễ (ngoài phạm vi ảnh thường). Xem `docs/Labeling_Plan.md` §5 và `paper/Methodology.md` §3.9.
- **Required-view rất nhạy cách diễn đạt.** Ranh giới petiole (cuống lá) ↔ crown (đọt) ↔ foliar (phiến lá) dễ nhầm, khớp quan sát LF7 yếu nhất ở petiole. Classifier có thể xếp nhầm view → cần cổng tin cậy + calibrate τ trên gold seed.

Là *proxy góc nhìn*, không phải chẩn đoán bệnh — cùng cảnh báo như LF3. Train **class-weighted** để bù lệch lớp.

## Đầu ra

`notebooks/lf5_petiole.ipynb` đọc `labels/disease_clf/oof_predictions.csv`, áp $\lambda_5$, ghi `labels/votes/lf5_petiole.csv` (schema chung `src/utils/lf_io.ipynb`; `lf='lf5_petiole'`, `task='5_petiole'`; cột extra `pred_class, fold`). Kiểm định (α̂, κ, coverage, calibrate τ, go/no-go) ở notebook so sánh riêng trên gold seed.
