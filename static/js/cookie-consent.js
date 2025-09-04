document.addEventListener('DOMContentLoaded', function(){
  (function(){
    const KEY="cookie_consent_v1";
    function getConsent(){ try{return JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){return{}} }
    function setConsent(v){
      localStorage.setItem(KEY, JSON.stringify(v));
      document.cookie = "cookie_consent="+encodeURIComponent(JSON.stringify(v))+";path=/;max-age="+(3600*24*365);
    }
    function bySel(s,root=document){return root.querySelector(s)}
    function allSel(s,root=document){return Array.from(root.querySelectorAll(s))}
    function show(el){el && el.classList.remove("d-none")}
    function hide(el){el && el.classList.add("d-none")}

    function loadDeferred(category){
      allSel('script[type="text/plain"][data-cookie-category="'+category+'"]').forEach(tag=>{
        const s=document.createElement("script");
        for(const {name,value} of Array.from(tag.attributes)){
          if(name==="type"||name==="data-cookie-category") continue;
          s.setAttribute(name, value);
        }
        s.text = tag.text;
        tag.replaceWith(s);
      });
    }
    function apply(consent){
      if(consent.analytics) loadDeferred("analytics");
      if(consent.marketing) loadDeferred("marketing");
    }

    const bar = bySel("#cookie-consent");
    if(!bar){ return; } // veilig stoppen als include ontbreekt

    const prefs = bySel("#cookie-prefs", bar);
    const btnAccept = bySel('[data-cc="accept"]', bar);
    const btnReject = bySel('[data-cc="reject"]', bar);
    const btnPrefs  = bySel('[data-cc="prefs"]', bar);
    const form = bySel("#cookie-prefs-form", bar);

    const saved = getConsent();
    if(saved && (saved.accepted || saved.rejected || saved.saved)){ apply(saved); }
    else { show(bar); }

    btnAccept?.addEventListener("click", ()=>{
      const v={accepted:true, analytics:true, marketing:true, ts:Date.now()};
      setConsent(v); apply(v); hide(bar);
    });
    btnReject?.addEventListener("click", ()=>{
      const v={rejected:true, analytics:false, marketing:false, ts:Date.now()};
      setConsent(v); hide(bar);
    });
    btnPrefs?.addEventListener("click", ()=>{ prefs?.classList.toggle("d-none"); });

    form?.addEventListener("submit",(e)=>{
      e.preventDefault();
      const v={
        saved:true,
        analytics: bySel("#cc-analytics", bar)?.checked ?? false,
        marketing: bySel("#cc-marketing", bar)?.checked ?? false,
        ts: Date.now()
      };
      setConsent(v); apply(v); hide(bar);
    });
  })();
});
