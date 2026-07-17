(() => {
  const header = document.querySelector('[data-sticky-header]');
  if (header) {
    const syncHeader = () => header.classList.toggle('is-condensed', window.scrollY > 48);
    syncHeader();
    window.addEventListener('scroll', syncHeader, { passive: true });
  }

  document.querySelectorAll('[data-comparison-id]').forEach((comparison) => {
  const range = comparison.querySelector('input[type="range"]');
  if (!range) return;
  comparison.classList.add('is-enhanced');
  const sync = () => {
    comparison.style.setProperty('--comparison-position', `${range.value}%`);
    range.setAttribute('aria-valuetext', `${range.value}% after image revealed`);
  };
  range.addEventListener('input', sync);
  sync();
});

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reducedMotion || !('IntersectionObserver' in window)) return;

  const targets = [...document.querySelectorAll('main > section:not(.hero):not(.page-hero)')];
  const pending = new Set(targets);
  targets.forEach((target) => target.classList.add('reveal', 'reveal-pending'));

  const reveal = (target) => {
    if (!pending.delete(target)) return;
    target.classList.remove('reveal-pending');
    target.classList.add('is-visible');
    observer.unobserve(target);
    if (!pending.size) {
      window.removeEventListener('scroll', revealPassed);
      window.removeEventListener('hashchange', revealPassed);
    }
  };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) reveal(entry.target);
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -24px' });
  const revealPassed = () => pending.forEach((target) => {
    if (target.getBoundingClientRect().top < window.innerHeight * 0.92) reveal(target);
  });

  targets.forEach((target) => observer.observe(target));
  revealPassed();
  window.addEventListener('scroll', revealPassed, { passive: true });
  window.addEventListener('hashchange', revealPassed);
})();
