const $=id=>document.getElementById(id);
const svgNS="http://www.w3.org/2000/svg";
const el=(name,attributes={})=>{const node=document.createElementNS(svgNS,name);for(const [k,v] of Object.entries(attributes))node.setAttribute(k,v);return node};
const money=n=>"CHF "+n.toLocaleString("en-GB");
let data,state,project=([lon,lat])=>[35+(lon-35)*20,20+(-lat-10)*21];
function reset(){state={day:0,budget:150000,people:0,happiness:60,stock:[],distributed:[],action:null,picks:[],sg:"We have completed seasonal readiness. Please explain why we are moving supplies.",feedback:"",finished:false};render()}
function dateAt(n){return new Date(Date.UTC(2008,2,4+n)).toLocaleDateString("en-GB",{day:"numeric",month:"long",year:"numeric",timeZone:"UTC"})}
function draw(){
const lines=$("tracks"),pins=$("pins");lines.replaceChildren();pins.replaceChildren();
data.tracks.forEach((track,i)=>{
const coords=track.map(p=>project(p));
const path=coords.map((p,j)=>(j?"L":"M")+p.join(" ")).join(" ");
lines.append(el("path",{d:path,fill:"none",stroke:i===3?"#da8a37":"#548aa6","stroke-width":i===3?3:1.45,"stroke-opacity":i===3?1:.55}));
const pos=coords[Math.min(state.day,coords.length-1)];
lines.append(el("circle",{cx:pos[0],cy:pos[1],r:i===3?4:2.3,fill:i===3?"#da8a37":"#548aa6",stroke:"white","stroke-width":.6}));
});
data.hubs.forEach(([id,name,lon,lat])=>{
const [x,y]=project([lon,lat]);
pins.append(el("circle",{cx:x,cy:y,r:state.stock.includes(id)?7:5,fill:state.stock.includes(id)?"#217969":"#c74a43",stroke:"white","stroke-width":1.9}));
const label=el("text",{x:x+(x>260?-10:10),y:y-9,"text-anchor":x>260?"end":"start","font-size":11,"font-weight":700,fill:"#304e5a",stroke:"#e1eef3","stroke-width":3,"paint-order":"stroke"});
label.textContent=name;pins.append(label);
});
}
function render(){
$("budget").textContent=money(state.budget);$("people").textContent=state.people.toLocaleString("en-GB");
$("happiness").textContent=(state.happiness>=75?"😄":state.happiness>=60?"🙂":state.happiness>=40?"😐":"😟")+" "+state.happiness+"/100";
$("sg").textContent="“"+state.sg+"”";$("date").textContent=dateAt(state.day);
$("brief").textContent="Issued 4 March 2008, 00 UTC. This 11-member ensemble projects a cyclone crossing northern Madagascar around 6 March. The members then diverge sharply over the Mozambique Channel; some curve southeast again. Today is "+dateAt(state.day)+". The forecast itself has not been reinitialized.";
$("source").textContent="The tracks are from WATTCH data. The display advances the forecast valid-day marker, not the forecast initialization.";
document.querySelectorAll("[data-action]").forEach(b=>b.classList.toggle("selected",b.dataset.action===state.action));
$("locations").hidden=!(state.action==="preposition"||state.action==="distribute");
$("hubs").replaceChildren();
if(!$("locations").hidden)for(const [id,name] of data.hubs){
const b=document.createElement("button");b.type="button";b.textContent=(state.picks.includes(id)?"✓ ":"")+name;b.classList.toggle("selected",state.picks.includes(id));
b.addEventListener("click",()=>{state.picks=state.picks.includes(id)?state.picks.filter(x=>x!==id):[...state.picks,id];render()});$("hubs").append(b);
}
let eligible=state.action==="preposition"?state.picks.filter(id=>!state.stock.includes(id)):state.action==="distribute"?state.picks.filter(id=>state.stock.includes(id)&&!state.distributed.includes(id)):[];
let cost=eligible.length*(state.action==="preposition"?20000:state.action==="distribute"?8000:0);
$("cost").textContent=state.action==="monitor"?"No expenditure.":state.action==="preposition"?"Cost for newly positioned hubs: "+money(cost)+".":state.action==="distribute"?"Cost for stocked hubs not yet distributed: "+money(cost)+".":"Select one of the three actions.";
$("feedback").textContent=state.feedback;
$("next").textContent=state.finished?"Play again":state.day===10?"Finish scenario":"Confirm and advance one day";
$("next").disabled=!state.finished&&(!state.action||(state.action!=="monitor"&&eligible.length===0)||cost>state.budget);
draw();
}
function advance(){
if(state.finished){reset();return}
const option=state.action,selected=state.picks;
if(option==="preposition"){
const fresh=selected.filter(id=>!state.stock.includes(id));state.stock.push(...fresh);state.budget-=20000*fresh.length;
state.happiness=Math.max(0,state.happiness-2*fresh.length);
state.sg="Why have we spent "+money(20000*fresh.length)+" positioning supplies in "+fresh.map(id=>data.hubs.find(h=>h[0]===id)[1]).join(", ")+"? Were those locations really at risk?";
}else if(option==="distribute"){
const fresh=selected.filter(id=>state.stock.includes(id)&&!state.distributed.includes(id));state.distributed.push(...fresh);
state.budget-=8000*fresh.length;
state.people+=fresh.length*400;
state.happiness=Math.min(100,state.happiness+4*fresh.length);
state.sg="We have distributed kits. How confident are we that those are the right intervention areas?";
}else{
state.sg="We're monitoring. What forecast development would change your decision?";
}
state.action=null;state.picks=[];state.feedback="";
if(state.day===10){
state.finished=true;
const hit="N",overspend=state.stock.filter(x=>x!==hit).length;
const successful=state.distributed.includes(hit);
state.happiness=Math.max(0,Math.min(100,state.happiness+(successful?15:-12)-overspend*2));
state.sg=successful?"The northern intervention reached people. But why did we incur costs in the other areas?":"We had impacts in the north and we need to explain whether our choices were proportionate.";
state.feedback="Simulation review: a northern intervention area was affected. This outcome is an illustrative game result, not an observation reconstructed from WATTCH. Estimated people reached are gameplay values.";
}else state.day++;
render();
}
async function coastline(){
try{
const [d3,topo,{default:world}]=await Promise.all([import("https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm"),import("https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/+esm"),import("https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json/+esm")]);
const country=topo.feature(world,world.objects.countries).features.find(f=>String(f.id)==="450"||f.properties?.name==="Madagascar");
if(!country)return;
const p=d3.geoMercator().fitExtent([[155,20],[345,443]],country);project=pt=>p(pt);
$("land").replaceChildren(el("path",{d:d3.geoPath(p)(country),fill:"#dbe4d5",stroke:"#799781","stroke-width":2}));
render();
}catch(err){
$("land").replaceChildren(el("path",{d:"M255 31Q273 27 281 58L288 105 300 159 299 216 279 272 263 316 231 390 200 443 191 425 204 380 212 338 219 292 214 245 219 203 209 155 221 101 216 69Z",fill:"#dbe4d5",stroke:"#799781","stroke-width":2}));
render();
}}
document.querySelectorAll("[data-action]").forEach(b=>b.addEventListener("click",()=>{state.action=b.dataset.action;state.picks=[];render()}));
$("next").addEventListener("click",advance);$("restart").addEventListener("click",reset);
try{const r=await fetch("data/jokwe.json");if(!r.ok)throw Error("Forecast data unavailable");data=await r.json();reset();coastline();}
catch(err){$("brief").textContent="Unable to load the forecast JSON: "+err.message;$("feedback").textContent="Run from a web server rather than opening index.html directly."}
