"""Oakmore Member Manager — full multi-section SPA served by the API."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

PAGE = r"""<!doctype html><html><head><meta charset=utf-8>
<title>Oakmore Member Manager</title><meta name=viewport content="width=device-width,initial-scale=1">
<style>
:root{--navy:#10243A;--amber:#FFB700;--blue:#3470E0;--line:#e7eaee;--mut:#7a8494}
*{box-sizing:border-box;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif}
body{margin:0;background:#f4f6f8;color:#17202e;display:flex;min-height:100vh}
#side{width:220px;background:var(--navy);color:#cdd6e2;flex-shrink:0;position:sticky;top:0;height:100vh}
#side .brand{padding:18px 20px;color:#fff;font-size:20px;font-weight:700}
#side .brand b{color:var(--amber)}
#side a{display:block;padding:11px 20px;color:#cdd6e2;text-decoration:none;cursor:pointer;font-size:14px}
#side a:hover,#side a.on{background:#1c3550;color:#fff;border-left:3px solid var(--amber)}
#main{flex:1;padding:22px 28px;overflow:auto}
h1{font-size:22px;margin:0 0 16px;color:var(--navy)}
.bar{display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap}
input,select{padding:8px 10px;border:1px solid #ccd2da;border-radius:7px;font-size:14px}
input{width:280px}
button{background:var(--navy);color:#fff;border:0;border-radius:7px;padding:8px 13px;cursor:pointer;font-size:14px}
button.amber{background:var(--amber);color:var(--navy);font-weight:700}
button.ghost{background:#fff;color:var(--navy);border:1px solid #ccd2da}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}
th{background:#fafbfc;text-align:left;font-size:12px;color:var(--mut);text-transform:uppercase;padding:9px 12px;border-bottom:1px solid var(--line)}
td{padding:9px 12px;border-bottom:1px solid var(--line);font-size:14px}
tr:hover td{background:#fafcff}
.badge{font-size:12px;background:#eef2f7;border-radius:10px;padding:2px 9px}
.cards{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:18px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;min-width:150px}
.card .n{font-size:26px;font-weight:800;color:var(--navy)} .card .l{color:var(--mut);font-size:13px}
.kv{display:grid;grid-template-columns:180px 1fr;gap:6px 14px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px;font-size:14px;max-width:760px}
.kv .k{color:var(--mut)}
.right{text-align:right}.mut{color:var(--mut)}.link{color:var(--blue);cursor:pointer}
.pill{padding:2px 9px;border-radius:10px;font-size:12px} .pill.g{background:#e6f6ec;color:#1a7f3c} .pill.r{background:#fdecec;color:#c0392b} .pill.y{background:#fff5db;color:#a9791a}
.tot{color:var(--blue);font-weight:800}
.section{display:none} .section.on{display:block}
</style></head><body>
<div id=side>
 <div class=brand>Oakmore <b>MM</b></div>
 <a data-s=dash class=on>Dashboard</a><a data-s=clients>Clients</a><a data-s=invoices>Invoices</a>
 <a data-s=brokers>Brokers</a><a data-s=agencies>Agencies</a><a data-s=commissions>Commissions</a>
 <a data-s=products>Products</a>
</div>
<div id=main>
 <div id=dash class="section on"></div>
 <div id=clients class=section></div>
 <div id=invoices class=section></div>
 <div id=brokers class=section></div>
 <div id=agencies class=section></div>
 <div id=commissions class=section></div>
 <div id=products class=section></div>
</div>
<script>
const API=location.origin, H={'X-Company-Id':'3','content-type':'application/json'};
const $=id=>document.getElementById(id);
async function j(u,o){o=o||{};o.headers=Object.assign({},H,o.headers||{});const r=await fetch(API+u,o);return r.ok?r.json():(r.status+' error')}
const esc=s=>(''+ (s??'')).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money=v=>'$'+Number(v||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});
function statusPill(s){s=s||'';const c=/ACTIVE/i.test(s)?'g':/TERM|Declined|Failed/i.test(s)?'r':'y';return `<span class="pill ${c}">${esc(s)}</span>`}
document.querySelectorAll('#side a').forEach(a=>a.onclick=()=>{
  document.querySelectorAll('#side a').forEach(x=>x.classList.remove('on'));a.classList.add('on');
  document.querySelectorAll('.section').forEach(x=>x.classList.remove('on'));
  const s=a.dataset.s;$(s).classList.add('on');({dash,clients,invoices,brokers,agencies,commissions,products}[s])();
});

async function dash(){
  const d=await j('/mm/summary');
  $('dash').innerHTML='<h1>Dashboard</h1><div class=cards>'+
   [['clients','Clients'],['members','Members'],['brokers','Brokers'],['agencies','Agencies'],
    ['invoice_processes','Invoice runs'],['client_invoices','Client invoices'],['payments','Payments'],['commission_runs','Commission runs']]
   .map(([k,l])=>`<div class=card><div class=n>${Number(d[k]||0).toLocaleString()}</div><div class=l>${l}</div></div>`).join('')+'</div>'+
   '<p class=mut>Live tenant data. Click a section on the left.</p>';
}

async function clients(q=''){
  $('clients').innerHTML='<h1>Clients</h1><div class=bar><input id=cq placeholder="Search clients…" value="'+esc(q)+'"><button onclick="clients(cq.value)">Search</button></div><div id=clist class=mut>loading…</div>';
  const cs=await j('/mm/clients?limit=100&q='+encodeURIComponent(q));
  $('clist').innerHTML='<table><tr><th>Client</th><th>Status</th><th>Lives</th><th>Billing</th><th>Account Mgr</th><th></th></tr>'+
   cs.map(c=>`<tr><td>${esc(c.client_name)}</td><td>${statusPill(c.client_status)}</td><td>${esc(c.lives||'')}</td><td>${esc(c.billing_freq||'')}</td><td>${esc(c.account_manager||'')}</td><td class=right><button class=ghost onclick="client(${c.id})">Open</button></td></tr>`).join('')+'</table>';
}
async function client(id){
  $('clients').innerHTML='<div class=mut>loading…</div>';
  const d=await j('/mm/clients/'+id), c=d.client||{};
  let h=`<div class=bar><button class=ghost onclick=clients()>← Clients</button><h1 style=margin:0>${esc(c.client_name)}</h1>${statusPill(c.client_status)}<span class=spacer></span><button class=amber onclick="invoicePrev(${id})">Preview invoice</button></div>`;
  h+='<div class=kv>'+[['Lives',c.lives],['Billing freq',c.billing_freq],['Payment method',c.payment_method],['Account manager',c.account_manager],['Primary broker',c.broker],['City/State',(c.city||'')+' '+(c.state||'')],['Contract eff.',c.contract_effective_date]].map(([k,v])=>`<div class=k>${k}</div><div>${esc(v||'')}</div>`).join('')+'</div>';
  if(d.fee)h+=`<p class=mut>Client fee: employer ${money(d.fee.employer_fee)} · employee ${money(d.fee.employee_fee)} · premium ${money(d.fee.premium)}</p>`;
  if(d.brokers&&d.brokers.length)h+='<h3>Brokers</h3><table><tr><th>Broker</th><th>Rate PEPM</th><th>Primary</th></tr>'+d.brokers.map(b=>`<tr><td>${esc(b.broker_name)}</td><td>${money(b.commission_rate_pepm)}</td><td>${b.is_primary?'yes':''}</td></tr>`).join('')+'</table>';
  h+=`<h3 style=margin-top:18px>Members (${d.member_count})</h3><div id=mem class=mut>loading…</div><div id=inv></div>`;
  $('clients').innerHTML=h;
  const ms=await j('/mm/clients/'+id+'/members');
  $('mem').innerHTML='<table><tr><th>Name</th><th>Type</th><th>Status</th><th>Emp ID</th><th>Deductions (pcm/simrp/admin)</th><th></th></tr>'+
   ms.slice(0,300).map(m=>`<tr><td>${esc(m.first_name)} ${esc(m.last_name)}</td><td>${esc(m.dependent_type||'')}</td><td>${statusPill(m.status)}</td><td>${esc(m.client_employee_id||'')}</td><td class=mut>${money(m.pcm_pre_tax)} / ${money(m.simrp_fee_after_tax)} / ${money(m.admin_fee_after_tax)}</td><td class=right><button class=ghost onclick="member(${m.id},${id})">View</button></td></tr>`).join('')+'</table>';
}
async function member(mid,cid){
  const d=await j('/mm/members/'+mid), m=d.member||{};
  let h=`<div class=bar><button class=ghost onclick="client(${cid})">← Client</button><h1 style=margin:0>${esc(m.first_name)} ${esc(m.last_name)}</h1></div>`;
  h+='<div class=kv>'+[['SSN (last4)',m.ssn],['DOB',m.date_of_birth],['Email',m.email],['Type',m.dependent_type],['Client dept',m.client_dept],['Emp ID',m.client_employee_id],['PCM pre/after',money(m.pcm_pre_tax)+' / '+money(m.pcm_after_tax)],['Admin / SIMRP',money(m.admin_fee_after_tax)+' / '+money(m.simrp_fee_after_tax)]].map(([k,v])=>`<div class=k>${k}</div><div>${esc(v||'')}</div>`).join('')+'</div>';
  h+='<h3>Status history</h3><table><tr><th>Status</th><th>Effective</th><th>By</th><th>Comment</th></tr>'+(d.status_history||[]).map(x=>`<tr><td>${statusPill(x.member_status)}</td><td>${esc(x.effective_date)}</td><td class=mut>${esc(x.modified_by||'')}</td><td class=mut>${esc(x.comment||'')}</td></tr>`).join('')+'</table>';
  if(d.dependents&&d.dependents.length)h+='<h3>Dependents</h3><table><tr><th>Name</th><th>Type</th></tr>'+d.dependents.map(x=>`<tr><td>${esc(x.first_name)} ${esc(x.last_name)}</td><td>${esc(x.dependent_type)}</td></tr>`).join('')+'</table>';
  $('clients').innerHTML=h;
}
async function invoicePrev(id){
  $('inv').innerHTML='<div class=mut>generating itemized invoice…</div>';
  const d=await j('/invoices/preview-lines',{method:'POST',body:JSON.stringify({client_id:id,service_month:'2026-07-01'})});
  if(typeof d==='string'){$('inv').innerHTML='<p class=mut>'+d+'</p>';return}
  let h=`<h3>July invoice (product lines) — <span class=tot>${money(d.total_fee)}</span> · ${d.members.length} billed · ${d.members.reduce((a,m)=>a+m.lines.length,0)} lines</h3><table><tr><th>Member</th><th>Product</th><th class=right>Amount</th></tr>`;
  d.members.slice(0,200).forEach(m=>m.lines.forEach(l=>h+=`<tr><td class=mut>member ${l.member_id}</td><td>${esc(l.product_code)}</td><td class="right tot">${money(l.amount)}</td></tr>`));
  $('inv').innerHTML=h+'</table>';
}

async function invoices(){
  $('invoices').innerHTML='<h1>Invoice runs</h1><div id=iplist class=mut>loading…</div>';
  const ps=await j('/mm/invoice-processes');
  $('iplist').innerHTML='<table><tr><th>Run</th><th>Invoice date</th><th>Status</th><th>Client invoices</th><th></th></tr>'+
   ps.map(p=>`<tr><td>${esc(p.process_name)}</td><td>${esc(p.invoice_date||'')}</td><td>${statusPill(p.status)}</td><td>${p.client_invoices}</td><td class=right><button class=ghost onclick="proc(${p.id},'${esc(p.process_name)}')">Open</button></td></tr>`).join('')+'</table>';
}
async function proc(id,name){
  $('invoices').innerHTML='<div class=mut>loading…</div>';
  const cis=await j('/mm/invoice-processes/'+id+'/client-invoices');
  $('invoices').innerHTML=`<div class=bar><button class=ghost onclick=invoices()>← Runs</button><h1 style=margin:0>${esc(name)}</h1></div>`+
   '<table><tr><th>Client</th><th>Status</th><th>Lines</th><th class=right>Total</th><th></th></tr>'+
   cis.map(ci=>`<tr><td>${esc(ci.client_name)}</td><td>${statusPill(ci.status)}</td><td>${ci.lines}</td><td class="right tot">${money(ci.total)}</td><td class=right><button class=ghost onclick="cinv(${ci.id},'${esc(ci.client_name)}')">Lines</button></td></tr>`).join('')+'</table>';
}
async function cinv(id,name){
  const ls=await j('/mm/client-invoices/'+id+'/lines');
  $('invoices').innerHTML=`<div class=bar><button class=ghost onclick=invoices()>← Runs</button><h1 style=margin:0>${esc(name)} — invoice lines</h1></div>`+
   '<table><tr><th>Member</th><th>Emp ID</th><th>Service month</th><th class=right>Employer</th><th class=right>Employee</th><th class=right>Total</th></tr>'+
   ls.map(l=>`<tr><td>${esc(l.first_name)} ${esc(l.last_name)}</td><td>${esc(l.client_employee_id||'')}</td><td>${esc(l.service_month||'')}</td><td class=right>${money(l.employer_fee)}</td><td class=right>${money(l.employee_fee)}</td><td class="right tot">${money(l.total_fee)}</td></tr>`).join('')+'</table>';
}

async function brokers(q=''){
  $('brokers').innerHTML='<h1>Brokers</h1><div class=bar><input id=bq placeholder="Search brokers…" value="'+esc(q)+'"><button onclick="brokers(bq.value)">Search</button></div><div id=blist class=mut>loading…</div>';
  const bs=await j('/mm/brokers?limit=200&q='+encodeURIComponent(q));
  $('blist').innerHTML='<table><tr><th>Broker</th><th>Contact</th><th>Email</th><th>Agency</th><th></th></tr>'+
   bs.map(b=>`<tr><td>${esc(b.broker_name)}</td><td>${esc((b.first_name||'')+' '+(b.last_name||''))}</td><td class=mut>${esc(b.email||'')}</td><td>${esc(b.agency_name||'')}</td><td class=right><button class=ghost onclick="broker(${b.id})">Open</button></td></tr>`).join('')+'</table>';
}
async function broker(id){
  const d=await j('/mm/brokers/'+id),b=d.broker||{};
  $('brokers').innerHTML=`<div class=bar><button class=ghost onclick=brokers()>← Brokers</button><h1 style=margin:0>${esc(b.broker_name)}</h1></div>`+
   '<div class=kv>'+[['Name',(b.first_name||'')+' '+(b.last_name||'')],['Email',b.email],['Phone',b.phone_mobile||b.phone_business],['Payment method',b.payment_method],['City/State',(b.city||'')+' '+(b.state||'')]].map(([k,v])=>`<div class=k>${k}</div><div>${esc(v||'')}</div>`).join('')+'</div>'+
   `<h3>Clients (${d.clients.length})</h3><table><tr><th>Client</th><th>Rate PEPM</th><th>Primary</th></tr>`+d.clients.map(c=>`<tr><td>${esc(c.client_name)}</td><td>${money(c.commission_rate_pepm)}</td><td>${c.is_primary?'yes':''}</td></tr>`).join('')+'</table>';
}
async function agencies(){
  $('agencies').innerHTML='<h1>Agencies</h1><div id=alist class=mut>loading…</div>';
  const as=await j('/mm/agencies');
  $('alist').innerHTML='<table><tr><th>Agency</th><th>Head broker</th><th>Brokers</th></tr>'+
   as.map(a=>`<tr><td>${esc(a.agency_name)}</td><td>${esc(a.head_broker||'')}</td><td>${a.brokers}</td></tr>`).join('')+'</table>';
}
async function commissions(){
  const [runs,rates]=await Promise.all([j('/mm/commission-runs'),j('/mm/commission-rates?limit=100')]);
  let h='<h1>Commissions</h1><h3>Runs</h3>';
  h+= runs.length?('<table><tr><th>Run</th><th>Period</th><th>Status</th><th>Lines</th><th class=right>Total</th></tr>'+runs.map(r=>`<tr><td>${esc(r.run_name)}</td><td>${esc(r.period_start_date)} → ${esc(r.period_end_date)}</td><td>${statusPill(r.run_status)}</td><td>${r.lines}</td><td class="right tot">${money(r.total)}</td></tr>`).join('')+'</table>'):'<p class=mut>No commission runs in this tenant copy.</p>';
  h+='<h3 style=margin-top:18px>Commission rates (client ↔ broker)</h3><table><tr><th>Client</th><th>Broker</th><th class=right>Rate PEPM</th><th>Primary</th></tr>'+rates.map(r=>`<tr><td>${esc(r.client_name)}</td><td>${esc(r.broker_name)}</td><td class=right>${money(r.commission_rate_pepm)}</td><td>${r.is_primary?'yes':''}</td></tr>`).join('')+'</table>';
  $('commissions').innerHTML=h;
}
async function products(){
  const ps=await j('/products');
  $('products').innerHTML='<h1>Products</h1><p class=mut>Catalog that drives itemized invoices.</p><table><tr><th>Code</th><th>Name</th><th>Category</th><th>Payer</th><th>Model</th><th>Prorate</th></tr>'+
   (Array.isArray(ps)?ps:[]).map(p=>`<tr><td><code>${esc(p.code)}</code></td><td>${esc(p.name)}</td><td>${esc(p.category)}</td><td>${esc(p.payer)}</td><td>${esc(p.pricing_model)}</td><td>${p.prorate?'yes':''}</td></tr>`).join('')+'</table>';
}
dash();
</script></body></html>"""

@router.get("/", response_class=HTMLResponse)
async def home() -> str:
    return PAGE
