/* Deliberate page choreography. Content stays usable if transitions are unavailable. */
let studioTransition = null;
let studioNavigation = 0;
const studioReducedMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const studioExamRoute = hash => /(?:#exam|\/exam)\/run/.test(hash);

async function navigateStudio(initial = false) {
  const navigation = ++studioNavigation;
  const hash = location.hash;
  main.removeAttribute('data-route');
  studioTransition?.skipTransition?.();
  main.getAnimations().forEach(animation => animation.cancel());
  if (initial || studioReducedMotion() || studioExamRoute(hash) || document.body.dataset.studioPage === 'exam') {
    await route();
    return;
  }
  // The outgoing snapshot remains on screen until the new lesson is ready.
  if (document.startViewTransition) {
    const transition = document.startViewTransition(async () => {
      if (navigation === studioNavigation) await route();
    });
    studioTransition = transition;
    transition.ready.catch(() => {});
    await transition.updateCallbackDone;
    transition.finished.catch(() => {}).finally(() => {
      if (studioTransition === transition) studioTransition = null;
    });
  } else {
    const leaving = main.animate(
      [{opacity: 1, transform: 'translateY(0)'}, {opacity: 0, transform: 'translateY(-24px)'}],
      {duration: 180, easing: 'ease-in', fill: 'forwards'}
    );
    await leaving.finished.catch(() => {});
    if (navigation !== studioNavigation) return;
    try { await route(); } finally { leaving.cancel(); }
    if (navigation === studioNavigation) main.animate(
      [{opacity: 0, transform: 'translateY(40px)'}, {opacity: 1, transform: 'translateY(0)'}],
      {duration: 550, easing: 'cubic-bezier(.16,1,.3,1)'}
    );
  }
}

function enhanceStudioMotion() {
  const hero = main.querySelector('.studio-hero');
  if (hero && !hero.dataset.choreographed) {
    hero.dataset.choreographed = 'true';
    const title = hero.querySelector('h1');
    title.innerHTML = title.innerHTML.split(/<br\s*\/?>/i).map((line, i) =>
      `<span class="studio-title-clip"><span class="studio-title-line" style="--line-index:${i}">${line}</span></span>`
    ).join('');
    hero.querySelector('.studio-demo')?.classList.add('studio-demo-enter');
  }
  document.querySelectorAll('[data-studio-reveal]').forEach(el => el.removeAttribute('data-studio-reveal'));
  studioMotionObserver?.disconnect();
  if (studioReducedMotion() || studioExamRoute(location.hash)) return;
  studioMotionObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('motion-in-view');
      studioMotionObserver.unobserve(entry.target);
    });
  }, {threshold: .08});
  main.querySelectorAll('.library-card,.studio-path-preview,.studio-exam-banner,.studio-control-group,.studio-mini-map li,.studio-knowledge-node').forEach((el, i) => {
    if (el.classList.contains('motion-in-view')) return;
    el.setAttribute('data-studio-reveal', '');
    el.style.setProperty('--motion-delay', Math.min(i % 4 * 90, 270) + 'ms');
    studioMotionObserver.observe(el);
  });
}
let studioMotionObserver;

function studioCheckpointHTML(base, i) {
  return `<div><strong>${i === 6 ? 'РК-1' : jt('РК-2 и сессия','РК-2 және сессия')}</strong><small>${i === 6 ? jt('После 7-й недели · 30 вопросов','7-аптадан кейін · 30 сұрақ') : jt('Повторение всего курса · 30 / 60 вопросов','Бүкіл курсты қайталау · 30 / 60 сұрақ')}</small></div><a href="${base + (i === 6 ? 'rk1' : 'session')}">${jt('Проверить себя','Өзіңді тексер')} ↗</a>`;
}
