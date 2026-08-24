document.addEventListener('DOMContentLoaded',()=>{
 if(!document.getElementById('map')||typeof L==='undefined')return;
 const map=L.map('map',{scrollWheelZoom:false}).setView([50.8234,-0.1406],14);
 L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
  maxZoom:19,attribution:'&copy; OpenStreetMap contributors'
 }).addTo(map);

 const safe=(v)=>String(v??'').replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));

 async function addReferences(){
   try{
    const res=await fetch('assets/data/reference-places.v1.json',{cache:'no-store'});
    if(!res.ok)return;
    const payload=await res.json();
    (payload.records||[]).forEach(p=>{
      L.circleMarker([p.latitude,p.longitude],{radius:7,color:'#102833',weight:2,fillColor:'#efbe50',fillOpacity:.95})
       .addTo(map)
       .bindPopup(`<strong>${safe(p.name)}</strong><br><span>${safe(p.category)}</span><br><small>Source checked · ${safe(p.retrieved_at)}</small><br><a href="${safe(p.source_url)}" target="_blank" rel="noopener">${safe(p.source_owner)} →</a>`);
    });
   }catch(e){}
 }

 async function addGeoJSON(url,fill,label){
   try{
    const res=await fetch(url,{cache:'no-store'}); if(!res.ok)return;
    const gj=await res.json();
    L.geoJSON(gj,{
      pointToLayer:(feature,latlng)=>L.circleMarker(latlng,{radius:7,color:'#102833',weight:2,fillColor:fill,fillOpacity:.95}),
      onEachFeature:(feature,layer)=>{
        const p=feature.properties||{};
        const title=p.name||p.title||label;
        const source=(p.sources||[])[0];
        const detail=p.website||p.source_url||source?.source_url||'';
        const checked=source?.retrieved_at ? `<br><small>Source checked · ${safe(source.retrieved_at).slice(0,10)}</small>` : '';
        layer.bindPopup(`<strong>${safe(title)}</strong><br><span>${safe(p.category||label)}</span>${checked}${detail?`<br><a href="${safe(detail)}" target="_blank" rel="noopener">Details/source →</a>`:''}`);
      }
    }).addTo(map);
   }catch(e){}
 }

 addReferences();
 addGeoJSON('assets/data/directory.v1.geojson','#49c9cb','Directory');
 addGeoJSON('assets/data/events.v1.geojson','#ef6b61','Event');
});
