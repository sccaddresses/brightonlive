
(() => {
  const body=document.body, menu=document.querySelector('.menu-toggle'), nav=document.querySelector('.site-nav');
  if(menu&&nav){
    menu.addEventListener('click',()=>{
      const open=body.classList.toggle('menu-open');
      menu.setAttribute('aria-expanded',String(open));
    });
    nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{body.classList.remove('menu-open');menu.setAttribute('aria-expanded','false')}));
  }
  document.querySelectorAll('[data-year]').forEach(el=>el.textContent=new Date().getFullYear());
})();
