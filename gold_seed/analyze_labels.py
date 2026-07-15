#!/usr/bin/env python3
"""Thống kê gold_seed_labels.csv: hoàn tất, skip, phân bố pos/neg, chồng nhãn,
cross-task, cảnh báo lệch. Chạy: python3 gold_seed/analyze_labels.py"""
import csv, os
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(REPO, "gold_seed", "gold_seed_labels.csv")
TASKS = ["1_maturity_evaluation","2_foliar_disease","3_trunk_disease","4_crown_disease","5_petiole"]
SHORT = {"1_maturity_evaluation":"maturity","2_foliar_disease":"foliar",
         "3_trunk_disease":"trunk","4_crown_disease":"crown","5_petiole":"petiole"}

rows = list(csv.DictReader(open(F)))
n = len(rows)
def val(r,t):  # "" = skip
    return r[t].strip()

# hoàn tất & skip
fully = sum(1 for r in rows if all(val(r,t)!="" for t in TASKS))
skip_cells = sum(1 for r in rows for t in TASKS if val(r,t)=="")
print(f"Tổng ảnh: {n} | gán đủ 5 tác vụ: {fully} | ô skip: {skip_cells}/{n*5} "
      f"({100*skip_cells/(n*5):.1f}%)")

print("\n== Phân bố nhãn từng tác vụ ==")
print(f"{'tác vụ':<10}{'pos(1)':>8}{'neg(0)':>8}{'skip':>7}{'%pos':>8}")
for t in TASKS:
    c = Counter(val(r,t) for r in rows)
    pos,neg,sk = c.get("1",0),c.get("0",0),c.get("",0)
    denom = pos+neg
    print(f"{SHORT[t]:<10}{pos:>8}{neg:>8}{sk:>7}{(100*pos/denom if denom else 0):>7.1f}%")

print("\n== Số nhãn dương / ảnh (đa nhãn) ==")
per = Counter(sum(1 for t in TASKS if val(r,t)=="1") for r in rows)
for k in sorted(per): print(f"  {k} tác vụ dương: {per[k]} ảnh")

print("\n== Positive theo nguồn (kiểm shortcut) ==")
by_src = defaultdict(lambda: defaultdict(int)); src_n=Counter()
for r in rows:
    src_n[r["task_native"]]+=1
    for t in TASKS:
        if val(r,t)=="1": by_src[r["task_native"]][t]+=1
print(f"{'nguồn(GT)':<10}" + "".join(f"{SHORT[t]:>9}" for t in TASKS))
for src in TASKS:
    print(f"{SHORT[src]:<10}" + "".join(f"{by_src[src][t]:>9}" for t in TASKS)
          + f"   (n={src_n[src]})")

print("\n== Correctness native (ảnh có =1 cho đúng tác vụ gốc của nó) ==")
for src in TASKS:
    same = [r for r in rows if r["task_native"]==src]
    pos = sum(1 for r in same if val(r,src)=="1")
    print(f"  {SHORT[src]:<9}: {pos}/{len(same)} = {100*pos/len(same):.0f}% hữu dụng cho tác vụ gốc")

print("\n== Cảnh báo ==")
warned=False
for t in TASKS:
    c=Counter(val(r,t) for r in rows); pos,neg=c.get("1",0),c.get("0",0)
    if min(pos,neg)<10:
        print(f"  ⚠ {SHORT[t]}: lớp thiểu số chỉ {min(pos,neg)} mẫu (<10) → F1/AUC nhiễu.")
        warned=True
if skip_cells/(n*5) > 0.1:
    print(f"  ⚠ tỷ lệ skip {100*skip_cells/(n*5):.1f}% > 10% → xem lại tiêu chí."); warned=True
if not warned: print("  Không có cảnh báo nghiêm trọng.")
