/**
 * Horizontal pinned scroll-jacking for .hpin sections.
 *
 * Equivalent of a React useLayoutEffect pattern: we wait for the layout to
 * settle (two rAFs + window 'load') BEFORE measuring the track width and
 * registering the ScrollTrigger pin. This avoids stale/zero widths when
 * fonts, images or CSS are still resolving.
 */
(() => {
  if (typeof window === 'undefined') return;
  if (!window.gsap || !window.ScrollTrigger) {
    console.warn('[hpin] GSAP/ScrollTrigger not loaded');
    return;
  }

  const prefersReduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduce) {
    // Fall back: keep the track as a normal horizontal scroller.
    document.querySelectorAll('.hpin').forEach((s) => s.classList.add('hpin--reduced'));
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  /** Wait until layout is stable. */
  const ready = () =>
    new Promise((resolve) => {
      if (document.readyState === 'complete') {
        // Two animation frames so the browser has flushed layout + paint.
        requestAnimationFrame(() => requestAnimationFrame(resolve));
      } else {
        window.addEventListener('load', () => {
          requestAnimationFrame(() => requestAnimationFrame(resolve));
        }, { once: true });
      }
    });

  /** Build one ScrollTrigger pin per section. */
  const init = () => {
    document.querySelectorAll('[data-hpin]').forEach((section) => {
      const track = section.querySelector('[data-hpin-track]');
      const progress = section.querySelector('[data-hpin-progress]');
      if (!track) return;

      // Safety: only enable on viewports wide enough that horizontal
      // scrolling makes sense. On mobile we keep native horizontal scroll.
      if (window.matchMedia('(max-width: 767px)').matches) {
        section.classList.add('hpin--reduced');
        return;
      }

      const getDistance = () => {
        // distance the track must travel = its scrollWidth minus viewport width
        const overflow = track.scrollWidth - window.innerWidth;
        return Math.max(overflow, 0);
      };

      const tween = gsap.to(track, {
        x: () => -getDistance(),
        ease: 'none',
        scrollTrigger: {
          trigger: section,
          start: 'top top',
          end: () => `+=${getDistance()}`,
          pin: true,
          anticipatePin: 1,
          scrub: 0.6,
          invalidateOnRefresh: true,
          onUpdate: (self) => {
            if (progress) progress.style.transform = `scaleX(${self.progress})`;
          },
        },
      });

      // Refresh once after images inside panels have loaded (their widths
      // can change as background-image is decoded). Robust against slow CDNs.
      const imgs = section.querySelectorAll('img');
      if (imgs.length) {
        let pending = imgs.length;
        imgs.forEach((img) => {
          if (img.complete) {
            if (--pending === 0) ScrollTrigger.refresh();
          } else {
            img.addEventListener('load', () => { if (--pending === 0) ScrollTrigger.refresh(); }, { once: true });
            img.addEventListener('error', () => { if (--pending === 0) ScrollTrigger.refresh(); }, { once: true });
          }
        });
      }

      // Refresh on font load too (Outfit/Manrope may shift widths).
      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(() => ScrollTrigger.refresh());
      }

      return tween;
    });
  };

  ready().then(init);
})();
