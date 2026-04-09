(function () {
  'use strict';

  // Match the longest CSS @keyframes durations
  var BANNER_ANIM_MS = 750;
  var GRID_ENTER_MS  = 650;
  var GRID_EXIT_MS   = 500;

  function AdRotator(container) {
    var type = container.dataset.adRotator;
    this.isBanner   = type === 'banner';
    this.container  = container;
    this.slides     = Array.prototype.slice.call(
      container.querySelectorAll(this.isBanner ? '.ad-banner-slide' : '.ad-grid-slide')
    );
    this.currentIdx = parseInt(container.dataset.adInitial, 10) || 0;
    this.timeoutId  = null;
    this.animating  = false;
    this.paused     = false;

    if (this.slides.length < 2) return;

    this._bindVisibility();
    this._scheduleNext();
  }

  // ─── Scheduling ────────────────────────────────────────────────

  AdRotator.prototype._scheduleNext = function () {
    if (this.paused) return;
    var self  = this;
    var ms    = (parseInt(this.slides[this.currentIdx].dataset.duration, 10) || 5) * 1000;

    this.timeoutId = setTimeout(function () { self._advance(); }, ms);
  };

  // ─── Transition ────────────────────────────────────────────────

  AdRotator.prototype._advance = function () {
    if (this.animating) return;
    this.animating = true;

    var slides   = this.slides;
    var nextIdx  = (this.currentIdx + 1) % slides.length;
    var current  = slides[this.currentIdx];
    var next     = slides[nextIdx];
    var isBanner = this.isBanner;
    var enterMs  = isBanner ? BANNER_ANIM_MS : GRID_ENTER_MS;
    var exitMs   = isBanner ? BANNER_ANIM_MS : GRID_EXIT_MS;
    var totalMs  = Math.max(enterMs, exitMs);
    var self     = this;

    // Lock container height so it doesn't collapse during the animation overlap
    var containerH = this.container.offsetHeight;
    this.container.style.height = containerH + 'px';

    // 1 — Demote current slide into exit animation
    current.classList.remove('ad-slide--active');
    current.classList.add('ad-slide--exit');
    current.setAttribute('aria-hidden', 'true');

    // 2 — Launch entrance on incoming slide simultaneously (overlapping cross)
    next.classList.add('ad-slide--enter');
    next.setAttribute('aria-hidden', 'false');

    // 3 — Settle incoming slide into stable active state
    setTimeout(function () {
      next.classList.remove('ad-slide--enter');
      next.classList.add('ad-slide--active');
    }, enterMs);

    // 4 — Clean up exiting slide, release locked height, schedule next
    setTimeout(function () {
      current.classList.remove('ad-slide--exit');
      current.setAttribute('aria-hidden', 'true');
      self.container.style.height = ''; // restore natural height
      self.currentIdx = nextIdx;
      self.animating  = false;
      self._scheduleNext();
    }, totalMs);
  };

  // ─── Page Visibility ───────────────────────────────────────────

  AdRotator.prototype._bindVisibility = function () {
    var self = this;
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        clearTimeout(self.timeoutId);
        self.paused = true;
      } else {
        self.paused = false;
        if (!self.animating) self._scheduleNext();
      }
    });
  };

  // ─── Boot ──────────────────────────────────────────────────────

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
