"""Lightweight Oakmore-branded UI served by the API (MVP demo surface).
The Reflex app in /web is the production front end; this makes the MVP clickable now."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

PAGE = """<!doctype html><html><head><meta charset=utf-8>
<title>Oakmore Billing</title><meta name=viewport content="width=device-width,initial-scale=1">
<style>
:root{--navy:#10243A;--amber:#FFB700;--blue:#3470E0}
*{box-sizing:border-box;font-family:-apple-system,Segoe UI,Roboto,sans-serif}
body{margin:0;background:#f6f7f9;color:#1a2330}
.top{background:var(--navy);color:#fff;padding:14px 22px;display:flex;align-items:center;gap:10px}
.top b{color:var(--amber)} .top .mvp{margin-left:auto;opacity:.6;font-size:13px}
.wrap{max-width:920px;margin:22px auto;padding:0 16px}
.row{display:flex;align-items:center;gap:10px;padding:10px 12px;background:#fff;border-bottom:1px solid #eef0f3}
.row:hover{background:#fbfcfe} .spacer{flex:1}
button{background:var(--navy);color:#fff;border:0;border-radius:6px;padding:6px 12px;cursor:pointer}
button.amber{background:var(--amber);color:var(--navy);font-weight:700}
input{padding:8px 10px;border:1px solid #d6dae0;border-radius:6px;width:260px}
.badge{font-size:12px;background:#eef;border-radius:10px;padding:2px 8px}
.card{background:#fff;border:1px solid var(--amber);border-radius:8px;padding:14px;margin-top:14px}
.line{display:flex;gap:12px;padding:5px 0;border-bottom:1px solid #f2f2f2;font-size:14px}
.tot{color:var(--blue);font-size:19px;font-weight:700;margin-bottom:8px}
h2{color:var(--navy)} .mut{color:#8a94a2;font-size:13px}
</style></head><body>
<div class=top><h3 style=margin:0>Oakmore</h3><b>Billing</b><span class=mvp>MVP</span></div>
<div class=wrap id=app></div>
<script>
const API=location.origin, H={'X-Company-Id':'3','content-type':'application/json'};
const app=document.getElementById('app');
async function j(u,o){const r=await fetch(API+u,o);return r.ok?r.json():[]}
async function clients(q=''){
  app.innerHTML='<div class=mut>loading…</div>';
  const cs=await j('/clients?limit=50&q='+encodeURIComponent(q));
  app.innerHTML='<div class=row><input id=q placeholder="Search clients…" value="'+q+'"><button onclick="clients(document.getElementById(\\'q\\').value)">Search</button></div>'+
    cs.map(c=>`<div class=row><span>${c.client_name}</span><span class=spacer></span><span class=badge>${c.client_status||''}</span><button onclick="client(${c.id},'${(c.client_name||'').replace(/'/g,'')}')">Open</button></div>`).join('');
}
async function client(id,name){
  app.innerHTML='<div class=mut>loading…</div>';
  const ms=await j('/clients/'+id+'/members',{headers:H});
  let h=`<div class=row><button onclick=clients()>← Clients</button><span class=spacer></span><h2 style=margin:0>${name}</h2><span class=spacer></span><button class=amber onclick="prev(${id},'${name.replace(/'/g,'')}')">Preview July invoice</button></div>`;
  h+=`<div class=mut style=padding:8px>${ms.length} active members</div>`;
  h+=ms.slice(0,50).map(m=>`<div class=row><span>${m.first_name} ${m.last_name}</span><span class=badge>${m.status}</span><span class=spacer></span><span class=mut>emp fee lines from products</span></div>`).join('');
  h+='<div id=inv></div>'; app.innerHTML=h;
}
async function prev(id,name){
  document.getElementById('inv').innerHTML='<div class=mut>generating…</div>';
  const d=await j('/invoices/preview-lines',{method:'POST',headers:H,body:JSON.stringify({client_id:id,service_month:'2026-07-01'})});
  let h=`<div class=card><div class=tot>Invoice total: $${d.total_fee}</div>`;
  (d.members||[]).forEach(m=>{(m.lines||[]).forEach(l=>{h+=`<div class=line><span class=mut style=width:90px>member ${m.member_id}</span><span style=width:200px>${l.product_code}</span><span class=spacer></span><b>$${l.amount}</b></div>`})});
  h+='</div>'; document.getElementById('inv').innerHTML=h;
}
clients();
</script></body></html>"""

@router.get("/", response_class=HTMLResponse)
async def home() -> str:
    return PAGE
