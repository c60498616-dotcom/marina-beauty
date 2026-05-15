/* МАРИНА БЬЮТИ — kinetic layer */
(() => {
  const prefersReduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Scroll reveal via IntersectionObserver */
  const revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !prefersReduce) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('is-visible');
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('is-visible'));
  }

  /* Hero parallax */
  if (!prefersReduce) {
    const parallax = document.querySelectorAll('.hero-parallax');
    let ticking = false;
    window.addEventListener(
      'scroll',
      () => {
        if (!ticking) {
          window.requestAnimationFrame(() => {
            const y = window.scrollY;
            parallax.forEach((el) => {
              el.style.transform = `translate3d(0, ${y * 0.18}px, 0) scale(1.04)`;
            });
            ticking = false;
          });
          ticking = true;
        }
      },
      { passive: true }
    );
  }

  /* Highlight active nav based on filename */
  const file = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  document.querySelectorAll('a[data-route]').forEach((a) => {
    if (a.getAttribute('data-route').toLowerCase() === file) {
      a.setAttribute('aria-current', 'page');
    }
  });
})();
