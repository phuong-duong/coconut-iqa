#!/usr/bin/env python3
"""Sinh annotate.html (tool gán nhãn gold seed) từ gold_seed_manifest.csv.
Chạy: python3 gold_seed/gen_tool.py   (sau khi đã có manifest)
"""
import csv, json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO, "gold_seed", "gold_seed_manifest.csv")
OUT = os.path.join(REPO, "gold_seed", "annotate.html")

TASKS = [
    ("1_maturity_evaluation", "Độ chín", "cận cảnh TRÁI, rõ màu vỏ"),
    ("2_foliar_disease",      "Bệnh lá", "cận cảnh PHIẾN LÁ"),
    ("3_trunk_disease",       "Bệnh thân", "bề mặt THÂN cây"),
    ("4_crown_disease",       "Bệnh đọt", "ĐỈNH ĐỌT / chồi ngọn"),
    ("5_petiole",             "Tàu lá", "CUỐNG LÁ + độ rủ"),
]

with open(MANIFEST, newline="") as f:
    data = list(csv.DictReader(f))
# đường dẫn ảnh: manifest lưu theo gốc repo; annotate.html nằm trong gold_seed/ -> thêm ../
for r in data:
    r["img"] = "../" + r["path"]

HTML = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gold Seed Annotator — Coconut IQA</title>
<style>
:root{--bg:#0f1115;--card:#1a1d24;--ink:#e8eaed;--mut:#9aa0a8;--line:#2a2e37;
--yes:#22c55e;--no:#ef4444;--skip:#6b7280;--acc:#3b82f6;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;background:var(--card);border-bottom:1px solid var(--line);
padding:10px 16px;display:flex;align-items:center;gap:16px;flex-wrap:wrap;z-index:10}
header b{font-size:16px}
.bar{flex:1;min-width:120px;height:8px;background:var(--line);border-radius:99px;overflow:hidden}
.bar>i{display:block;height:100%;background:var(--acc);width:0}
button{font:inherit;cursor:pointer;border:1px solid var(--line);background:#232733;color:var(--ink);
border-radius:8px;padding:7px 12px}
button:hover{border-color:var(--acc)}
.wrap{display:grid;grid-template-columns:1fr 360px;gap:18px;padding:18px;max-width:1200px;margin:0 auto}
@media(max-width:860px){.wrap{grid-template-columns:1fr}}
.imgbox{background:#000;border:1px solid var(--line);border-radius:12px;display:flex;align-items:center;
justify-content:center;min-height:60vh;overflow:hidden}
.imgbox img{max-width:100%;max-height:78vh;object-fit:contain;cursor:zoom-in}
.side{display:flex;flex-direction:column;gap:12px}
.meta{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.meta .gid{font-size:20px;font-weight:700}
.meta .src{color:var(--mut);font-size:13px;margin-top:2px}
.task{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.task .t{font-weight:600}.task .h{color:var(--mut);font-size:12px;margin:2px 0 8px}
.opts{display:flex;gap:8px}
.opts button{flex:1;border-radius:8px;padding:9px 0;font-weight:600}
.opts button.on-yes{background:var(--yes);border-color:var(--yes);color:#04210f}
.opts button.on-no{background:var(--no);border-color:var(--no);color:#2a0606}
.opts button.on-skip{background:var(--skip);border-color:var(--skip);color:#0b0d10}
.nav{display:flex;gap:8px}.nav button{flex:1;padding:11px 0;font-weight:600}
.nav .next{background:var(--acc);border-color:var(--acc);color:#04122e}
.kbd{color:var(--mut);font-size:12px;padding:0 4px}
.tag{display:inline-block;font-size:11px;padding:1px 7px;border-radius:99px;background:#232733;color:var(--mut);margin-left:6px}
.done{color:var(--yes)}
</style></head><body>
<header>
  <b>Gold Seed Annotator</b>
  <span id="counter" class="tag">0 / 0</span>
  <span id="doneTag" class="tag">đã gán: 0</span>
  <div class="bar"><i id="prog"></i></div>
  <button onclick="jumpNext()">↦ Ảnh chưa gán</button>
  <button onclick="exportCSV()">⬇ Xuất CSV</button>
</header>
<div class="wrap">
  <div class="imgbox"><img id="img" alt="" onclick="window.open(this.src)"></div>
  <div class="side">
    <div class="meta">
      <div class="gid" id="gid">–</div>
      <div class="src" id="src"></div>
    </div>
    <div id="tasks"></div>
    <div class="nav">
      <button onclick="go(-1)">← Trước <span class="kbd">←</span></button>
      <button class="next" onclick="go(1)">Sau → <span class="kbd">Space</span></button>
    </div>
    <div class="meta" style="font-size:12.5px;color:var(--mut)">
      Phím tắt: <b>1–5</b> = Có · <b>Shift+1–5</b> = Không · <b>0</b>+số = Skip ·
      <b>Space/→</b> sau · <b>←</b> trước. Tiến độ tự lưu trong trình duyệt.
    </div>
  </div>
</div>
<script>
const DATA = __DATA__;
const TASKS = __TASKS__;
const KEY = "coconut_gold_seed_v1";
let store = JSON.parse(localStorage.getItem(KEY) || "{}");
let i = 0;

function save(){localStorage.setItem(KEY, JSON.stringify(store));}
function rec(){const id=DATA[i].gold_id; return store[id]||(store[id]={});}
function isDone(id){const v=store[id]; if(!v)return false; return TASKS.every(t=>v[t[0]]!==undefined);}

function buildTasks(){
  const box=document.getElementById("tasks"); box.innerHTML="";
  TASKS.forEach((t,idx)=>{
    const [code,name,hint]=t;
    const el=document.createElement("div"); el.className="task";
    el.innerHTML=`<div class="t">${idx+1}. ${name} <span class="tag">${code}</span></div>
      <div class="h">cần: ${hint}</div>
      <div class="opts">
        <button data-c="${code}" data-v="1">Có</button>
        <button data-c="${code}" data-v="0">Không</button>
        <button data-c="${code}" data-v="skip">?</button></div>`;
    box.appendChild(el);
  });
  box.querySelectorAll("button").forEach(b=>b.onclick=()=>setVal(b.dataset.c,b.dataset.v));
}
function setVal(code,v){rec()[code]=v; save(); render(); refreshStats();}
function render(){
  const d=DATA[i];
  document.getElementById("img").src=d.img;
  document.getElementById("gid").textContent=d.gold_id+"  ("+(i+1)+"/"+DATA.length+")";
  document.getElementById("src").innerHTML="Nguồn: "+d.source+" · GT gốc: <b>"+d.task_native+"</b>"+
     (isDone(d.gold_id)?' <span class="done">✓ đã gán đủ</span>':'');
  const v=store[d.gold_id]||{};
  document.querySelectorAll("#tasks .opts").forEach(o=>{
    o.querySelectorAll("button").forEach(b=>{
      b.className=""; const cur=v[b.dataset.c];
      if(cur!==undefined && cur===b.dataset.v)
        b.className = b.dataset.v==="1"?"on-yes":b.dataset.v==="0"?"on-no":"on-skip";
    });
  });
  document.getElementById("counter").textContent=(i+1)+" / "+DATA.length;
}
function refreshStats(){
  const done=DATA.filter(d=>isDone(d.gold_id)).length;
  document.getElementById("doneTag").textContent="đã gán: "+done;
  document.getElementById("prog").style.width=(100*done/DATA.length)+"%";
}
function go(d){i=(i+d+DATA.length)%DATA.length; render();}
function jumpNext(){const n=DATA.findIndex((d,k)=>k>i&&!isDone(d.gold_id));
  const m=n>=0?n:DATA.findIndex(d=>!isDone(d.gold_id)); if(m>=0){i=m;render();}else alert("Đã gán đủ 5 tác vụ cho cả "+DATA.length+" ảnh!");}
document.addEventListener("keydown",e=>{
  if(e.key===" "||e.key==="ArrowRight"){e.preventDefault();go(1);return;}
  if(e.key==="ArrowLeft"){e.preventDefault();go(-1);return;}
  const n=parseInt(e.key);
  if(n>=1&&n<=5){const code=TASKS[n-1][0]; setVal(code, e.shiftKey?"0":"1");}
});
function exportCSV(){
  const cols=["gold_id","image_id","source","task_native",...TASKS.map(t=>t[0])];
  let out=cols.join(",")+"\\n";
  DATA.forEach(d=>{
    const v=store[d.gold_id]||{};
    const row=[d.gold_id,d.image_id,'"'+d.source+'"',d.task_native,
      ...TASKS.map(t=>{const x=v[t[0]]; return x===undefined||x==="skip"?"":x;})];
    out+=row.join(",")+"\\n";
  });
  const blob=new Blob([out],{type:"text/csv;charset=utf-8"});
  const a=document.createElement("a"); a.href=URL.createObjectURL(blob);
  a.download="gold_seed_labels.csv"; a.click();
}
buildTasks(); refreshStats();
// mở ở ảnh chưa gán đầu tiên
const first=DATA.findIndex(d=>!isDone(d.gold_id)); i=first>=0?first:0; render();
</script></body></html>
"""

html = (HTML
        .replace("__DATA__", json.dumps(
            [{"gold_id": r["gold_id"], "image_id": r["image_id"], "source": r["source"],
              "task_native": r["task_native"], "img": r["img"]} for r in data],
            ensure_ascii=False))
        .replace("__TASKS__", json.dumps(TASKS, ensure_ascii=False)))
with open(OUT, "w") as f:
    f.write(html)
print(f"Đã sinh {OUT} ({len(data)} ảnh)")
