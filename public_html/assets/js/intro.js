
(() => {
  const intro=document.querySelector('.bl-intro');
  if(!intro)return;
  const sessionKey='brightonlive-intro-seen';
  let seen=false;
  try{seen=sessionStorage.getItem(sessionKey)==='1'}catch(e){}
  if(seen){intro.hidden=true;return}
  document.body.classList.add('intro-open');
  const close=()=>{
    intro.classList.add('is-leaving');document.body.classList.remove('intro-open');
    try{sessionStorage.setItem(sessionKey,'1')}catch(e){}
    setTimeout(()=>{intro.hidden=true},950);
  };
  intro.querySelectorAll('[data-intro-enter],[data-intro-skip]').forEach(el=>el.addEventListener('click',close));
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!intro.hidden)close()});
})();
