"""Oakmore Member Manager — SPA (login, CRUD upserts, invoice workflow). Served by the API."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

PAGE = r"""<!doctype html><html lang=en><head><meta charset=utf-8>
<title>Oakmore Member Manager</title><meta name=viewport content="width=device-width,initial-scale=1">
<link rel=preconnect href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap">
<style>
:root{--navy:#0f2440;--navy2:#1b3557;--amber:#f5a300;--blue:#3470E0;--bg:#f6f7f9;--card:#fff;--line:#e7e9ee;--txt:#1c2432;--mut:#6b7688;--good:#127a3a;--goodbg:#e7f6ec;--bad:#c0392b;--badbg:#fdecec;--warn:#a9791a;--warnbg:#fff6df;--r:10px}
*{box-sizing:border-box;font-family:'DM Sans',system-ui,sans-serif}
body{margin:0;background:var(--bg);color:var(--txt)}
button{cursor:pointer;font-family:inherit;font-size:14px;border-radius:8px;border:1px solid transparent;padding:8px 14px}
.btn{background:var(--navy);color:#fff}.btn:hover{background:var(--navy2)}
.btn.amber{background:var(--amber);color:#231a00;font-weight:600}.btn.ghost{background:#fff;color:var(--navy);border-color:var(--line)}.btn.ghost:hover{background:#f3f5f8}
.btn.sm{padding:5px 10px;font-size:13px}
input,select,textarea{font-family:inherit;font-size:14px;padding:9px 11px;border:1px solid #d3d8e0;border-radius:8px;width:100%;background:#fff}
label{font-size:12px;color:var(--mut);display:block;margin:10px 0 4px}
a{color:var(--blue);text-decoration:none;cursor:pointer}
/* login */
#login{position:fixed;inset:0;background:linear-gradient(140deg,#0f2440,#1b3557);display:flex;align-items:center;justify-content:center;z-index:100}
#login .box{background:#fff;border-radius:16px;padding:34px 32px;width:360px;box-shadow:0 20px 60px rgba(0,0,0,.3)}
#login h1{margin:0 0 4px;color:var(--navy);font-size:24px}#login h1 b{color:var(--amber)}
#login .sub{color:var(--mut);font-size:13px;margin-bottom:18px}
#login .err{color:var(--bad);font-size:13px;min-height:18px;margin-top:8px}
/* app */
#app{display:none;min-height:100vh}
#side{position:fixed;top:0;left:0;width:224px;height:100vh;background:var(--navy);color:#c6d0de;padding-top:8px}
#side .brand{padding:16px 20px 14px;color:#fff;font-size:20px;font-weight:700}.brand b{color:var(--amber)}
#side a{display:flex;gap:10px;padding:10px 20px;color:#c6d0de;font-size:14px;border-left:3px solid transparent}
#side a:hover{background:#173052;color:#fff}#side a.on{background:#173052;color:#fff;border-left-color:var(--amber)}
#top{position:fixed;top:0;left:224px;right:0;height:56px;background:#fff;border-bottom:1px solid var(--line);display:flex;align-items:center;padding:0 24px;z-index:20}
#top .who{margin-left:auto;color:var(--mut);font-size:13px;display:flex;gap:12px;align-items:center}
#main{margin-left:224px;padding:80px 28px 40px}
h1{font-size:22px;margin:0 0 4px;color:var(--navy)}.sub{color:var(--mut);font-size:13px;margin-bottom:16px}
.bar{display:flex;gap:10px;align-items:center;margin-bottom:16px;flex-wrap:wrap}.bar input{width:300px}
.cards{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 20px;min-width:150px;box-shadow:0 1px 2px rgba(16,36,64,.04)}
.card .n{font-size:27px;font-weight:700;color:var(--navy)}.card .l{color:var(--mut);font-size:13px;margin-top:2px}
table{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:0 1px 2px rgba(16,36,64,.04)}
th{background:#fbfcfd;text-align:left;font-size:11px;letter-spacing:.03em;color:var(--mut);text-transform:uppercase;padding:10px 14px;border-bottom:1px solid var(--line)}
td{padding:10px 14px;border-bottom:1px solid #eef0f3;font-size:14px}tr:last-child td{border-bottom:0}tbody tr:hover td{background:#fafcff}
.right{text-align:right}.mut{color:var(--mut)}.tot{color:var(--blue);font-weight:700}
.pill{padding:2px 10px;border-radius:20px;font-size:12px;font-weight:500;display:inline-block}
.pill.g{background:var(--goodbg);color:var(--good)}.pill.r{background:var(--badbg);color:var(--bad)}.pill.y{background:var(--warnbg);color:var(--warn)}
.kv{display:grid;grid-template-columns:200px 1fr;gap:8px 16px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px;font-size:14px;max-width:820px}.kv .k{color:var(--mut)}
h3{color:var(--navy);margin:22px 0 10px;font-size:16px}
/* modal */
#modal{position:fixed;inset:0;background:rgba(15,36,64,.45);display:none;align-items:center;justify-content:center;z-index:50}
#modal .box{background:#fff;border-radius:16px;padding:24px;width:520px;max-height:88vh;overflow:auto;box-shadow:0 24px 70px rgba(0,0,0,.3)}
#modal h2{margin:0 0 4px;color:var(--navy);font-size:18px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:0 14px}
.mact{display:flex;gap:10px;justify-content:flex-end;margin-top:20px}
#toast{position:fixed;bottom:22px;right:22px;background:var(--navy);color:#fff;padding:12px 18px;border-radius:10px;display:none;z-index:80;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.section{display:none}.section.on{display:block}
</style></head><body>

<div id=login><div class=box>
 <h1>Oakmore <b>MM</b></h1><div class=sub>Member Manager — sign in</div>
 <label>Email</label><input id=le value="nic@oakmorelabs.com">
 <label>Password</label><input id=lp type=password>
 <div class=err id=lerr></div>
 <button class="btn amber" style="width:100%;margin-top:14px" onclick=doLogin()>Sign in</button>
</div></div>

<div id=app>
 <div id=side>
  <div class=brand>Oakmore <b>MM</b></div>
  <a data-s=dash class=on>Dashboard</a><a data-s=clients>Clients</a><a data-s=invoicing>Invoicing</a>
  <a data-s=runs>Invoice Runs</a><a data-s=brokers>Brokers</a><a data-s=agencies>Agencies</a>
  <a data-s=commissions>Commissions</a><a data-s=products>Products</a>
 </div>
 <div id=top><div class=who><span id=whoami></span><button class="btn ghost sm" onclick=logout()>Sign out</button></div></div>
 <div id=main>
  <div id=dash class="section on"></div><div id=clients class=section></div><div id=invoicing class=section></div>
  <div id=runs class=section></div><div id=brokers class=section></div><div id=agencies class=section></div>
  <div id=commissions class=section></div><div id=products class=section></div>
 </div>
</div>

<div id=modal onclick="if(event.target.id=='modal')closeModal()"><div class=box id=mbox></div></div>
<div id=toast></div>

<script>
const API=location.origin;
let TOKEN=localStorage.oak_token, TENANT=localStorage.oak_tenant||'3', NAME=localStorage.oak_name||'';
const $=id=>document.getElementById(id);
const esc=s=>(''+(s??'')).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money=v=>'$'+Number(v||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});
const num=v=>Number(v||0).toLocaleString();
function H(){return {'X-Company-Id':TENANT,'content-type':'application/json','Authorization':'Bearer '+(TOKEN||'')}}
async function j(u,o){o=o||{};o.headers=Object.assign({},H(),o.headers||{});const r=await fetch(API+u,o);if(!r.ok)return {__err:r.status};return r.json()}
function toast(m){const t=$('toast');t.textContent=m;t.style.display='block';setTimeout(()=>t.style.display='none',2200)}
function pill(s){s=s||'';const c=/ACTIVE|Cleared|FINAL|Completed/i.test(s)?'g':/TERM|Declined|Failed/i.test(s)?'r':'y';return `<span class="pill ${c}">${esc(s)}</span>`}
function modal(html){$('mbox').innerHTML=html;$('modal').style.display='flex'}
function closeModal(){$('modal').style.display='none'}

// ---- auth ----
async function doLogin(){
  const r=await fetch(API+'/auth/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email:$('le').value,password:$('lp').value})});
  if(!r.ok){$('lerr').textContent='Invalid email or password';return}
  const d=await r.json();TOKEN=d.token;TENANT=d.tenant_id;NAME=d.name;
  localStorage.oak_token=TOKEN;localStorage.oak_tenant=TENANT;localStorage.oak_name=NAME;
  startApp();
}
function logout(){localStorage.removeItem('oak_token');location.reload()}
function startApp(){$('login').style.display='none';$('app').style.display='block';$('whoami').textContent=NAME+' · tenant '+TENANT;dash()}
document.querySelectorAll('#side a').forEach(a=>a.onclick=()=>{
  document.querySelectorAll('#side a').forEach(x=>x.classList.remove('on'));a.classList.add('on');
  document.querySelectorAll('.section').forEach(x=>x.classList.remove('on'));const s=a.dataset.s;$(s).classList.add('on');
  ({dash,clients,invoicing,runs,brokers,agencies,commissions,products}[s])();
});

// ---- dashboard ----
async function dash(){const d=await j('/mm/summary');$('dash').innerHTML='<h1>Dashboard</h1><div class=sub>Live tenant data</div><div class=cards>'+
 [['clients','Clients'],['members','Members'],['brokers','Brokers'],['agencies','Agencies'],['invoice_processes','Invoice runs'],['client_invoices','Client invoices'],['payments','Payments'],['commission_runs','Commission runs']]
 .map(([k,l])=>`<div class=card><div class=n>${num(d[k])}</div><div class=l>${l}</div></div>`).join('')+'</div>'}

// ---- clients + members ----
async function clients(q=''){$('clients').innerHTML='<h1>Clients</h1><div class=bar><input id=cq placeholder="Search clients…" value="'+esc(q)+'" onkeydown="if(event.key==\'Enter\')clients(this.value)"><button class=btn onclick="clients(cq.value)">Search</button></div><div id=clist class=mut>loading…</div>';
 const cs=await j('/mm/clients?limit=100&q='+encodeURIComponent(q));
 $('clist').innerHTML='<table><tr><th>Client</th><th>Status</th><th>Lives</th><th>Billing</th><th></th></tr>'+cs.map(c=>`<tr><td><a onclick="client(${c.id})">${esc(c.client_name)}</a></td><td>${pill(c.client_status)}</td><td>${esc(c.lives||'')}</td><td>${esc(c.billing_freq||'')}</td><td class=right><button class="btn ghost sm" onclick="client(${c.id})">Open</button></td></tr>`).join('')+'</table>'}
async function client(id){$('clients').innerHTML='<div class=mut>loading…</div>';const d=await j('/mm/clients/'+id),c=d.client||{};window._c=c;
 let h=`<div class=bar><button class="btn ghost sm" onclick=clients()>← Clients</button><h1 style=margin:0>${esc(c.client_name)}</h1>${pill(c.client_status)}<span style=flex:1></span><button class="btn ghost" onclick="editClient(${id})">Edit client</button><button class="btn amber" onclick="genInvoice(${id})">Generate invoice</button></div>`;
 h+='<div class=kv>'+[['Lives',c.lives],['Billing freq',c.billing_freq],['Payment method',c.payment_method],['Account manager',c.account_manager],['Primary broker',c.broker],['City/State',(c.city||'')+' '+(c.state||'')]].map(([k,v])=>`<div class=k>${k}</div><div>${esc(v||'')}</div>`).join('')+'</div>';
 if(d.fee)h+=`<p class=mut>Client fee — employer ${money(d.fee.employer_fee)} · employee ${money(d.fee.employee_fee)} · premium ${money(d.fee.premium)}</p>`;
 h+=`<div class=bar style=margin-top:14px><h3 style=margin:0>Members (${d.member_count})</h3><span style=flex:1></span><button class="btn sm" onclick="newMember(${id})">+ New member</button></div><div id=mem class=mut>loading…</div>`;
 $('clients').innerHTML=h;const ms=await j('/mm/clients/'+id+'/members');
 $('mem').innerHTML='<table><tr><th>Name</th><th>Type</th><th>Status</th><th>Emp ID</th><th>Deductions</th><th></th></tr>'+ms.slice(0,300).map(m=>`<tr><td><a onclick="member(${m.id},${id})">${esc(m.first_name)} ${esc(m.last_name)}</a></td><td>${esc(m.dependent_type||'')}</td><td>${pill(m.status)}</td><td>${esc(m.client_employee_id||'')}</td><td class=mut>${money(m.pcm_pre_tax)} / ${money(m.simrp_fee_after_tax)}</td><td class=right><button class="btn ghost sm" onclick="editMember(${m.id},${id})">Edit</button> <button class="btn ghost sm" onclick="addStatus(${m.id},${id})">Status</button></td></tr>`).join('')+'</table>'}
async function member(mid,cid){const d=await j('/mm/members/'+mid),m=d.member||{};
 let h=`<div class=bar><button class="btn ghost sm" onclick="client(${cid})">← Client</button><h1 style=margin:0>${esc(m.first_name)} ${esc(m.last_name)}</h1><span style=flex:1></span><button class="btn ghost" onclick="editMember(${mid},${cid})">Edit</button><button class="btn" onclick="addStatus(${mid},${cid})">Add status</button></div>`;
 h+='<div class=kv>'+[['SSN (last4)',m.ssn],['DOB',m.date_of_birth],['Email',m.email],['Type',m.dependent_type],['Emp ID',m.client_employee_id],['PCM pre/after',money(m.pcm_pre_tax)+' / '+money(m.pcm_after_tax)],['Admin/SIMRP',money(m.admin_fee_after_tax)+' / '+money(m.simrp_fee_after_tax)]].map(([k,v])=>`<div class=k>${k}</div><div>${esc(v||'')}</div>`).join('')+'</div>';
 h+='<h3>Status history</h3><table><tr><th>Status</th><th>Effective</th><th>By</th><th>Comment</th></tr>'+(d.status_history||[]).map(x=>`<tr><td>${pill(x.member_status)}</td><td>${esc(x.effective_date)}</td><td class=mut>${esc(x.modified_by||'')}</td><td class=mut>${esc(x.comment||'')}</td></tr>`).join('')+'</table>';
 if((d.dependents||[]).length)h+='<h3>Dependents</h3><table><tr><th>Name</th><th>Type</th></tr>'+d.dependents.map(x=>`<tr><td>${esc(x.first_name)} ${esc(x.last_name)}</td><td>${esc(x.dependent_type)}</td></tr>`).join('')+'</table>';
 $('clients').innerHTML=h}

// ---- upsert modals ----
function field(l,id,v,t){return `<label>${l}</label><input id=${id} value="${esc(v||'')}" ${t?`type=${t}`:''}>`}
function editClient(id){const c=window._c||{};modal(`<h2>Edit client</h2>${field('Name','f_client_name',c.client_name)}<div class=grid2>${field('Status','f_client_status',c.client_status)}${field('Lives','f_lives',c.lives)}${field('Billing freq','f_billing_freq',c.billing_freq)}${field('Payment method','f_payment_method',c.payment_method)}${field('City','f_city',c.city)}${field('State','f_state',c.state)}</div><div class=mact><button class="btn ghost" onclick=closeModal()>Cancel</button><button class="btn amber" onclick="saveClient(${id})">Save</button></div>`)}
async function saveClient(id){const b={};['client_name','client_status','lives','billing_freq','payment_method','city','state'].forEach(k=>{const v=$('f_'+k).value;if(v!=='')b[k]=v});const r=await j('/mm/clients/'+id,{method:'PATCH',body:JSON.stringify(b)});closeModal();toast('Client saved');client(id)}
function editMember(mid,cid){j('/mm/members/'+mid).then(d=>{const m=d.member||{};modal(`<h2>Edit member</h2><div class=grid2>${field('First name','f_first_name',m.first_name)}${field('Last name','f_last_name',m.last_name)}${field('Email','f_email',m.email)}${field('Emp ID','f_client_employee_id',m.client_employee_id)}${field('PCM pre tax','f_pcm_pre_tax',m.pcm_pre_tax)}${field('PCM after tax','f_pcm_after_tax',m.pcm_after_tax)}${field('Admin fee','f_admin_fee_after_tax',m.admin_fee_after_tax)}${field('SIMRP','f_simrp_fee_after_tax',m.simrp_fee_after_tax)}</div><div class=mact><button class="btn ghost" onclick=closeModal()>Cancel</button><button class="btn amber" onclick="saveMember(${mid},${cid})">Save</button></div>`)})}
async function saveMember(mid,cid){const b={};['first_name','last_name','email','client_employee_id','pcm_pre_tax','pcm_after_tax','admin_fee_after_tax','simrp_fee_after_tax'].forEach(k=>{const v=$('f_'+k).value;if(v!=='')b[k]=v});await j('/mm/members/'+mid,{method:'PATCH',body:JSON.stringify(b)});closeModal();toast('Member saved');client(cid)}
function newMember(cid){modal(`<h2>New member</h2><div class=grid2>${field('First name','f_first_name')}${field('Last name','f_last_name')}${field('SSN (last4)','f_ssn')}${field('DOB (YYYY-MM-DD)','f_date_of_birth')}${field('Email','f_email')}${field('Emp ID','f_client_employee_id')}</div><label>Type</label><select id=f_dependent_type><option value=E>Employee</option><option value=S>Spouse</option><option value=C>Child</option></select><div class=mact><button class="btn ghost" onclick=closeModal()>Cancel</button><button class="btn amber" onclick="saveNewMember(${cid})">Create</button></div>`)}
async function saveNewMember(cid){const b={client_id:cid,dependent_type:$('f_dependent_type').value};['first_name','last_name','ssn','date_of_birth','email','client_employee_id'].forEach(k=>{const v=$('f_'+k).value;if(v!=='')b[k]=v});const r=await j('/mm/members',{method:'POST',body:JSON.stringify(b)});if(r.__err){toast('Error creating member');return}closeModal();toast('Member created');client(cid)}
function addStatus(mid,cid){modal(`<h2>Add member status</h2><label>Status</label><select id=f_status><option>ACTIVE</option><option>TERM</option><option>ON LEAVE</option><option>PENDING</option><option>OPTED_OUT</option></select>${field('Effective date (YYYY-MM-DD)','f_eff',new Date().toISOString().slice(0,10))}${field('Comment','f_cm')}<div class=mact><button class="btn ghost" onclick=closeModal()>Cancel</button><button class="btn amber" onclick="saveStatus(${mid},${cid})">Add</button></div>`)}
async function saveStatus(mid,cid){await j('/mm/members/'+mid+'/status',{method:'POST',body:JSON.stringify({member_status:$('f_status').value,effective_date:$('f_eff').value,comment:$('f_cm').value})});closeModal();toast('Status added');member(mid,cid)}

// ---- invoice workflow ----
async function genInvoice(cid){toast('Generating…');const r=await j('/mm/invoices/generate',{method:'POST',body:JSON.stringify({client_id:cid,service_month:'2026-07-01'})});if(r.__err){toast('Generate failed');return}toast('Invoice '+r.id+' — '+money(r.total_fee));document.querySelector('#side a[data-s=invoicing]').click()}
async function invoicing(){$('invoicing').innerHTML='<h1>Invoicing</h1><div class=sub>Generated itemized invoices (products → lines)</div><div id=ivlist class=mut>loading…</div>';
 const iv=await j('/mm/invoices');$('ivlist').innerHTML=(iv.length?'<table><tr><th>#</th><th>Client</th><th>Month</th><th>Status</th><th>Members</th><th>Lines</th><th class=right>Total</th><th></th></tr>'+iv.map(x=>`<tr><td>${x.id}</td><td>${esc(x.client_name)}</td><td>${esc(x.service_month)}</td><td>${pill(x.status)}</td><td>${x.member_count}</td><td>${x.line_count}</td><td class="right tot">${money(x.total_fee)}</td><td class=right><button class="btn ghost sm" onclick="openInvoice(${x.id})">Open</button></td></tr>`).join('')+'</table>':'<p class=mut>No invoices generated yet. Open a client and click “Generate invoice”.</p>')}
async function openInvoice(id){const d=await j('/mm/invoices/'+id),h=d.invoice;
 let out=`<div class=bar><button class="btn ghost sm" onclick=invoicing()>← Invoicing</button><h1 style=margin:0>Invoice #${h.id} — ${esc(h.client_name)}</h1>${pill(h.status)}<span style=flex:1></span>`+(h.status==='DRAFT'?`<button class="btn amber" onclick="finalize(${id})">Finalize</button>`:'')+`</div>`;
 out+=`<p class=mut>${esc(h.service_month)} · ${h.member_count} members · ${h.line_count} lines · total <span class=tot>${money(h.total_fee)}</span></p>`;
 out+='<table><tr><th>Member</th><th>Product</th><th class=right>Qty</th><th class=right>Unit</th><th class=right>Amount</th></tr>'+d.lines.map(l=>`<tr><td class=mut>member ${l.member_id}</td><td>${esc(l.product_code)}</td><td class=right>${l.quantity}</td><td class=right>${money(l.unit_price)}</td><td class="right tot">${money(l.amount)}</td></tr>`).join('')+'</table>';
 $('invoicing').innerHTML=out}
async function finalize(id){await j('/mm/invoices/'+id+'/finalize',{method:'POST'});toast('Invoice finalized');openInvoice(id)}

// ---- runs / brokers / agencies / commissions / products ----
async function runs(){const ps=await j('/mm/invoice-processes');$('runs').innerHTML='<h1>Invoice Runs</h1><div class=sub>Existing Member Manager invoice processes</div><table><tr><th>Run</th><th>Date</th><th>Status</th><th>Client invoices</th><th></th></tr>'+ps.map(p=>`<tr><td>${esc(p.process_name)}</td><td>${esc(p.invoice_date||'')}</td><td>${pill(p.status)}</td><td>${p.client_invoices}</td><td class=right><button class="btn ghost sm" onclick="proc(${p.id},'${esc(p.process_name)}')">Open</button></td></tr>`).join('')+'</table>'}
async function proc(id,name){const cis=await j('/mm/invoice-processes/'+id+'/client-invoices');$('runs').innerHTML=`<div class=bar><button class="btn ghost sm" onclick=runs()>← Runs</button><h1 style=margin:0>${esc(name)}</h1></div><table><tr><th>Client</th><th>Status</th><th>Lines</th><th class=right>Total</th></tr>`+cis.map(ci=>`<tr><td>${esc(ci.client_name)}</td><td>${pill(ci.status)}</td><td>${ci.lines}</td><td class="right tot">${money(ci.total)}</td></tr>`).join('')+'</table>'}
async function brokers(q=''){$('brokers').innerHTML='<h1>Brokers</h1><div class=bar><input id=bq placeholder="Search brokers…" value="'+esc(q)+'"><button class=btn onclick="brokers(bq.value)">Search</button></div><div id=bl class=mut>loading…</div>';const bs=await j('/mm/brokers?limit=200&q='+encodeURIComponent(q));$('bl').innerHTML='<table><tr><th>Broker</th><th>Contact</th><th>Email</th><th>Agency</th><th></th></tr>'+bs.map(b=>`<tr><td>${esc(b.broker_name)}</td><td>${esc((b.first_name||'')+' '+(b.last_name||''))}</td><td class=mut>${esc(b.email||'')}</td><td>${esc(b.agency_name||'')}</td><td class=right><button class="btn ghost sm" onclick="broker(${b.id})">Open</button></td></tr>`).join('')+'</table>'}
async function broker(id){const d=await j('/mm/brokers/'+id),b=d.broker||{};$('brokers').innerHTML=`<div class=bar><button class="btn ghost sm" onclick=brokers()>← Brokers</button><h1 style=margin:0>${esc(b.broker_name)}</h1></div><div class=kv>`+[['Name',(b.first_name||'')+' '+(b.last_name||'')],['Email',b.email],['Payment method',b.payment_method],['City/State',(b.city||'')+' '+(b.state||'')]].map(([k,v])=>`<div class=k>${k}</div><div>${esc(v||'')}</div>`).join('')+`</div><h3>Clients (${d.clients.length})</h3><table><tr><th>Client</th><th class=right>Rate PEPM</th><th>Primary</th></tr>`+d.clients.map(c=>`<tr><td>${esc(c.client_name)}</td><td class=right>${money(c.commission_rate_pepm)}</td><td>${c.is_primary?'yes':''}</td></tr>`).join('')+'</table>'}
async function agencies(){const as=await j('/mm/agencies');$('agencies').innerHTML='<h1>Agencies</h1><table><tr><th>Agency</th><th>Head broker</th><th>Brokers</th></tr>'+as.map(a=>`<tr><td>${esc(a.agency_name)}</td><td>${esc(a.head_broker||'')}</td><td>${a.brokers}</td></tr>`).join('')+'</table>'}
async function commissions(){const [runs,rates]=await Promise.all([j('/mm/commission-runs'),j('/mm/commission-rates?limit=150')]);let h='<h1>Commissions</h1><h3>Runs</h3>'+(runs.length?'<table><tr><th>Run</th><th>Status</th><th class=right>Total</th></tr>'+runs.map(r=>`<tr><td>${esc(r.run_name)}</td><td>${pill(r.run_status)}</td><td class="right tot">${money(r.total)}</td></tr>`).join('')+'</table>':'<p class=mut>No commission runs in this tenant copy.</p>')+'<h3>Commission rates (client ↔ broker)</h3><table><tr><th>Client</th><th>Broker</th><th class=right>Rate PEPM</th></tr>'+rates.map(r=>`<tr><td>${esc(r.client_name)}</td><td>${esc(r.broker_name)}</td><td class=right>${money(r.commission_rate_pepm)}</td></tr>`).join('')+'</table>';$('commissions').innerHTML=h}
async function products(){const ps=await j('/products');$('products').innerHTML='<div class=bar><h1 style=margin:0>Products</h1><span style=flex:1></span><button class="btn amber" onclick=newProduct()>+ New product</button></div><div class=sub>Catalog that drives itemized invoices</div><table><tr><th>Code</th><th>Name</th><th>Category</th><th>Payer</th><th>Model</th></tr>'+(Array.isArray(ps)?ps:[]).map(p=>`<tr><td><code>${esc(p.code)}</code></td><td>${esc(p.name)}</td><td>${esc(p.category)}</td><td>${esc(p.payer)}</td><td>${esc(p.pricing_model)}</td></tr>`).join('')+'</table>'}
function newProduct(){modal(`<h2>New product</h2><div class=grid2>${field('Code','p_code')}${field('Name','p_name')}</div><label>Category</label><select id=p_category><option>CUSTOM</option><option>ADMIN_FEE</option><option>PCM</option><option>SIMRP</option><option>MEDICAL</option><option>SUPP</option></select><label>Payer</label><select id=p_payer><option>EMPLOYER</option><option>EMPLOYEE</option><option>SPLIT</option></select><div class=mact><button class="btn ghost" onclick=closeModal()>Cancel</button><button class="btn amber" onclick=saveProduct()>Create</button></div>`)}
async function saveProduct(){const b={code:$('p_code').value,name:$('p_name').value,category:$('p_category').value,payer:$('p_payer').value,pricing_model:'FLAT'};const r=await j('/products',{method:'POST',body:JSON.stringify(b)});if(r.__err){toast('Error');return}closeModal();toast('Product created');products()}

if(TOKEN){startApp()}
</script></body></html>"""

@router.get("/", response_class=HTMLResponse)
async def home() -> str:
    return PAGE
