(function () {
  'use strict';

  var FADE_MS = 600; // must match the CSS transition duration

  function AdRotator(container) {
    var type = container.dataset.adRotator;
    this.container  = container;
    this.slides     = Array.prototype.slice.call(
      container.querySelectorAll(type === 'banner' ? '.ad-banner-slide' : '.ad-grid-slide')
    );
    this.currentIdx = parseInt(container.dataset.adInitial, 10) || 0;
    this.timeoutId  = null;
    this.paused     = false;

    if (this.slides.length < 2) return; // single ad — nothing to rotate

    this._bindVisibility();
    this._scheduleNext();
  }

  AdRotator.prototype._scheduleNext = function () {
    if (this.paused) return;
    var self     = this;
    var duration = (parseInt(this.slides[this.currentIdx].dataset.duration, 10) || 5) * 1000;
    this.timeoutId = setTimeout(function () { self._advance(); }, duration);
  };

  AdRotator.prototype._advance = function () {
    var slides  = this.slides;
    var nextIdx = (this.currentIdx + 1) % slides.length;
    var current = slides[this.currentIdx];
    var next    = slides[nextIdx];

    // Prepare incoming slide: add active class (makes it position:relative)
    // but override opacity to 0 first so the CSS transition fires from 0→1
    next.style.opacity = '0';
    next.classList.add('ad-slide--active');
    next.setAttribute('aria-hidden', 'false');

    // Force a reflow so the browser registers the opacity:0 before removing it
    void next.offsetWidth;

    // Remove the inline override — CSS transition takes over (0 → 1)
    next.style.opacity = '';

    // After the fade completes, demote the outgoing slide
    var self = this;
    setTimeout(function () {
      current.classList.remove('ad-slide--active');
      current.setAttribute('aria-hidden', 'true');
      self.currentIdx = nextIdx;
      self._scheduleNext();
    }, FADE_MS);
  };

  AdRotator.prototype._bindVisibility = function () {
    var self = this;
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        clearTimeout(self.timeoutId);
        self.paused = true;
      } else {
        self.paused = false;
        self._scheduleNext();
      }
    });
  };

  function init() {
    document.querySelectorAll('[data-ad-rotator]').forEach(function (el) {
      new AdRotator(el);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

}());
