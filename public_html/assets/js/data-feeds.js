(() => {
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[c]));

  async function getJSON(url) {
    const res = await fetch(url, {cache:"no-store"});
    if (!res.ok) throw new Error(`${url}: ${res.status}`);
    return res.json();
  }

  function sourceStatus(record) {
    const sources = record.sources || [];
    const checked = record.verification_status === "publication_ready" || sources.length > 0;
    if (!checked) return "";
    const dates = sources.map(s => s.retrieved_at).filter(Boolean).sort();
    const date = dates.length ? dates[dates.length-1].slice(0,10) : "";
    return `<span class="data-check">Source checked${date ? ` · ${esc(date)}` : ""}</span>`;
  }

  async function renderDirectory() {
    const root=document.querySelector("[data-directory-feed]");
    if(!root) return;
    try {
      const payload=await getJSON("assets/data/directory.v1.json");
      const records=payload.records||[];
      if(!records.length) {
        root.innerHTML=`<div class="feed-empty"><strong>BrightonLive directory build in progress.</strong><span>Only publication-safe records will appear here.</span></div>`;
        return;
      }
      root.innerHTML=records.slice(0,48).map(r=>`
        <article class="live-card">
          <div class="live-card__kicker">${esc(r.category||"Local")}</div>
          <h3>${esc(r.name)}</h3>
          ${r.address ? `<p>${esc(r.address)}${r.postcode ? ` · ${esc(r.postcode)}`:""}</p>`:""}
          <div class="live-card__links">
            ${r.website ? `<a href="${esc(r.website)}" target="_blank" rel="noopener">Website</a>`:""}
            ${r.latitude != null && r.longitude != null ? `<a href="https://www.openstreetmap.org/?mlat=${encodeURIComponent(r.latitude)}&mlon=${encodeURIComponent(r.longitude)}#map=18/${encodeURIComponent(r.latitude)}/${encodeURIComponent(r.longitude)}" target="_blank" rel="noopener">Map</a>`:""}
          </div>
          ${sourceStatus(r)}
        </article>`).join("");
    } catch(err) {
      root.innerHTML=`<div class="feed-empty"><strong>Directory feed unavailable.</strong><span>The presentation site remains usable while the governed feed is rebuilt.</span></div>`;
    }
  }

  async function renderEvents() {
    const root=document.querySelector("[data-events-feed]");
    if(!root) return;
    try {
      const payload=await getJSON("assets/data/events.v1.json");
      let records=payload.records||[];
      records.sort((a,b)=>String(a.start||"").localeCompare(String(b.start||"")));
      if(!records.length) {
        root.innerHTML=`<div class="feed-empty"><strong>BrightonLive event feed is being assembled.</strong><span>Events appear only after source/date/location checks pass.</span></div>`;
        return;
      }
      root.innerHTML=records.slice(0,60).map(r=>{
        const date=r.start ? new Date(r.start) : null;
        const dateText=date && !Number.isNaN(date.valueOf()) ?
          new Intl.DateTimeFormat("en-GB",{weekday:"short",day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"}).format(date) : "";
        return `<article class="event-row">
          <div class="event-row__date">${esc(dateText)}</div>
          <div><div class="live-card__kicker">${esc(r.category||"Event")}</div><h3>${esc(r.title)}</h3>
          <p>${esc(r.venue||"Brighton & Hove")}</p>
          <div class="live-card__links">${r.website ? `<a href="${esc(r.website)}" target="_blank" rel="noopener">Details</a>`:""}${r.booking_url ? `<a href="${esc(r.booking_url)}" target="_blank" rel="noopener">Tickets</a>`:""}</div>
          ${sourceStatus(r)}</div>
        </article>`;
      }).join("");
    } catch(err) {
      root.innerHTML=`<div class="feed-empty"><strong>Event feed unavailable.</strong><span>Use the source links above while the governed feed is rebuilt.</span></div>`;
    }
  }

  document.addEventListener("DOMContentLoaded",()=>{renderDirectory();renderEvents();});
})();
