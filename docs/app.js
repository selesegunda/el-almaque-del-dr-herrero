const $ = s => document.querySelector(s);
const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const categories = ['Guías y protocolos','Artículos científicos','Comunicaciones científicas','Noticias'];
const configuredTopics = ["Colorrectal", "Gástrico y unión gastroesofágica", "Esófago", "Páncreas", "Vías biliares", "Hepatocarcinoma", "Neuroendocrinos", "Neoplasias endocrinas", "Canal anal"];
const state={category:'',limit:40};let data={records:[],runs:[]};
const fmt=d=>{if(!d)return '—';const x=new Date(d);return Number.isNaN(+x)?d:x.toLocaleString('es-ES',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit',timeZone:'Europe/Madrid'})};
function runStatus(r){return r?.issues?.length ? `· ${r.issues.length} fuente(s) con incidencias` : ''}
function render(){
 const all=data.records, runs=data.runs, chosen=$('#run').value;
 const run=runs.find(x=>x.at===chosen);
 const changeMap=new Map((run?.changes||[]).map(x=>[x.key,x.status]));
 const q=$('#search').value.trim().toLowerCase(),topic=$('#topic').value,source=$('#source').value,status=$('#status').value;
 let items=all.filter(x=>(!chosen||changeMap.has(x.key))&&(!state.category||x.category===state.category)&&(!topic||x.topics.includes(topic))&&(!source||x.source===source)&&(!q||[x.title,x.source,x.doi,x.pmid,...x.topics].join(' ').toLowerCase().includes(q)));
 if(status)items=items.filter(x=>(chosen?changeMap.get(x.key):(x.versions.length?'Actualizada':'Nueva'))===status);
 items.sort((a,b)=>categories.indexOf(a.category)-categories.indexOf(b.category)||b.first_seen.localeCompare(a.first_seen));
 const rcount=chosen?run.changes.length:all.length;
 const dailyCount=new Set(runs.filter(x=>x.sources_ok?.length).map(x=>new Date(x.at).toLocaleDateString('sv-SE',{timeZone:'Europe/Madrid'})).filter(x=>x>='2026-11-17'&&x<='2026-11-23')).size;
 $('#metrics').innerHTML=[['Referencias',all.length],['Actualizaciones',all.reduce((n,x)=>n+x.versions.length,0)],['Primera semana',Math.min(7,dailyCount)+'/7'],['Informes guardados',runs.length]].map(([l,n])=>`<div class="metric"><div class="big">${n}</div><div class="small">${l}</div></div>`).join('');
 $('#tabs').innerHTML=[['','Todas'],...categories.map(x=>[x,x])].map(([v,l])=>`<button class="${state.category===v?'active':''}" data-cat="${esc(v)}">${esc(l)} (${(chosen?all.filter(x=>changeMap.has(x.key)):all).filter(x=>!v||x.category===v).length})</button>`).join('');
 $('#statusline').textContent=`${items.length} referencias encontradas · Última consulta: ${runs.length?fmt(runs.at(-1).at):'pendiente'}${runStatus(runs.at(-1))}`;
 $('#records').innerHTML=items.length?items.slice(0,state.limit).map(x=>{
 const st=chosen?changeMap.get(x.key):(x.versions.length?'Actualizada':'Nueva');
 return `<article class="item"><div class="meta">${esc(x.category)} · ${esc(x.source)} · Publicación: ${esc(x.date||'No verificada')}</div><h3>${esc(x.title)}</h3><div class="chips"><span class="chip ${st==='Nueva'?'new':'updated'}">${esc(st)}</span>${x.topics.map(t=>`<span class="chip">${esc(t)}</span>`).join('')}</div>${x.description?`<p class="muted">${esc(x.description)}</p>`:''}<div class="meta">Detectado: ${fmt(x.first_seen)}${x.doi?' · DOI: '+esc(x.doi):''}${x.pmid?' · PMID: '+esc(x.pmid):''}</div><p><a href="${esc(x.publisher_url||x.url)}" target="_blank" rel="noopener noreferrer">Ver publicación original</a> ${x.publisher_url?`· <a href="${esc(x.url)}" target="_blank" rel="noopener noreferrer">Ficha en PubMed</a>`:''}</p>${x.versions.length?`<details><summary>Histórico de cambios registrados (${x.versions.length})</summary><ul>${x.versions.map(v=>`<li>${fmt(v.recorded_at)} — ${esc(v.title)} (${esc(v.date)})</li>`).join('')}</ul></details>`:''}</article>`}).join(''):'<div class="empty">No hay publicaciones para estos filtros. Si es la primera visita, los datos se cargarán tras la primera ejecución del programa.</div>';
 $('#more').hidden=items.length<=state.limit;
 $('#runinfo').innerHTML=run?`<p>${run.new} nuevas · ${run.updated} actualizadas · ${run.seen} referencias examinadas</p>${run.issues?.length?`<p class="issue">Incidencias: ${run.issues.map(x=>esc(x.source)).join(', ')}. Consulta el registro del proyecto para detalles.</p>`:''}`:'';
}
async function main(){try{const [r,h]=await Promise.all([fetch('records.json'),fetch('runs.json')]);if(!r.ok||!h.ok)throw Error('Faltan datos');const obj=await r.json();data.records=Object.values(obj);data.runs=await h.json();}catch(e){$('#statusline').textContent='No se han podido cargar los datos publicados.'}
const topics=[...new Set([...configuredTopics,...data.records.flatMap(x=>x.topics||[])])].sort((a,b)=>a.localeCompare(b,'es'));const sources=[...new Set(data.records.map(x=>x.source))].sort();
$('#topic').innerHTML+=[...topics].map(x=>`<option>${esc(x)}</option>`).join('');$('#source').innerHTML+=[...sources].map(x=>`<option>${esc(x)}</option>`).join('');
$('#run').innerHTML+=data.runs.slice().reverse().map(x=>`<option value="${esc(x.at)}">${fmt(x.at)} · ${x.new} nuevas / ${x.updated} actualizadas</option>`).join('');
['#search','#topic','#source','#status','#run'].forEach(x=>$(x).addEventListener('input',()=>{state.limit=40;render()}));
$('#tabs').addEventListener('click',e=>{const b=e.target.closest('[data-cat]');if(b){state.category=b.dataset.cat;state.limit=40;render()}});
$('#more').addEventListener('click',()=>{state.limit+=40;render()});render();}main();