#!/usr/bin/env python3
"""Lấy mẫu phân tầng gold seed (300 ảnh) cho Coconut task-oriented IQA.

Nguyên tắc:
- Cân bằng ~60 ảnh/tác vụ (5 tác vụ) -> 300 ảnh. Macro-F1 là metric chính nên
  mỗi tác vụ cần đủ mẫu test; lấy theo tỷ lệ sẽ khiến crown/petiole quá ít.
- Nguồn Roboflow (maturity) có x3 bản augment cùng ảnh gốc -> DEDUPE ở cấp ảnh
  gốc (chống rò rỉ / trùng lặp trong tập test), rồi mới lấy mẫu.
- Seed cố định để tái lập được.

Chạy: python3 gold_seed/sample_gold_seed.py   (từ thư mục gốc repo)
"""
import csv, os, random, re, sys
from collections import defaultdict

SEED = 42
PER_TASK = 60
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO, "labels", "lf1-5_correctness_manifest.csv")
OUT = os.path.join(REPO, "gold_seed", "gold_seed_manifest.csv")

# nguồn -> tác vụ gốc (nơi ảnh có ground-truth)
SOURCE_TASK = {
    "disease/Gray Leaf Spot": "2_foliar_disease",
    "disease/Leaf Rot":       "2_foliar_disease",
    "disease/Stem Bleeding":  "3_trunk_disease",
    "disease/Bud Rot":        "4_crown_disease",
    "disease/Bud Root Dropping": "5_petiole",
}

def task_of(source):
    if source.startswith("coconut-veirf-v5"):
        return "1_maturity_evaluation"
    return SOURCE_TASK.get(source)

def original_id(image_id, source):
    """Gộp x3 augment Roboflow về ảnh gốc: '010_jpg.rf.<hash>' -> '010'."""
    if source.startswith("coconut-veirf-v5"):
        return re.split(r"_jpg", image_id, maxsplit=1)[0]
    return image_id  # ảnh bệnh không có augment

def main():
    rng = random.Random(SEED)
    rows = []
    with open(MANIFEST, newline="") as f:
        for r in csv.DictReader(f):
            r["task_native"] = task_of(r["source"])
            rows.append(r)

    # gom theo tác vụ; với maturity gom theo ảnh gốc rồi chọn 1 đại diện/ảnh gốc
    by_task = defaultdict(list)
    for r in rows:
        if r["task_native"]:
            by_task[r["task_native"]].append(r)

    selected = []
    for task in ["1_maturity_evaluation", "2_foliar_disease", "3_trunk_disease",
                 "4_crown_disease", "5_petiole"]:
        pool = by_task[task]
        if task == "1_maturity_evaluation":
            groups = defaultdict(list)
            for r in pool:
                groups[original_id(r["image_id"], r["source"])].append(r)
            keys = sorted(groups)
            rng.shuffle(keys)
            chosen_keys = keys[:PER_TASK]
            picked = [sorted(groups[k], key=lambda x: x["image_id"])[0] for k in chosen_keys]
        else:
            picked = pool[:]
            rng.shuffle(picked)
            picked = picked[:PER_TASK]
        for r in picked:
            selected.append(r)
        print(f"{task}: pool={len(pool)} -> chọn {len(picked)}"
              f"{' (ảnh gốc)' if task=='1_maturity_evaluation' else ''}")

    # xác minh file tồn tại
    missing = [r for r in selected if not os.path.exists(os.path.join(REPO, r["path"]))]
    if missing:
        print(f"CẢNH BÁO: {len(missing)} file không thấy trên đĩa (có thể do đồng bộ cloud).",
              file=sys.stderr)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cols = ["gold_id", "image_id", "source", "task_native", "path"]
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i, r in enumerate(selected, 1):
            w.writerow({
                "gold_id": f"G{i:03d}",
                "image_id": r["image_id"],
                "source": r["source"],
                "task_native": r["task_native"],
                "path": r["path"],
            })
    print(f"\nTổng: {len(selected)} ảnh -> {OUT}")

if __name__ == "__main__":
    main()
