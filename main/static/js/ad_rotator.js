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
    this.bar        = null;

    if (this.slides.length < 2) return;

    // Progress bar — banner only
    if (this.isBanner) {
      this.bar = document.createElement('div');
      this.bar.className = 'ad-progress-bar';
      container.appendChild(this.bar);
    }

    this._bindVisibility();
    this._scheduleNext();
  }

  // ─── Scheduling ────────────────────────────────────────────────

  AdRotator.prototype._scheduleNext = function () {
    if (this.paused) return;
    var self  = this;
    var ms    = (parseInt(this.slides[this.currentIdx].dataset.duration, 10) || 5) * 1000;

    if (this.bar) this._startProgress(ms);

    this.timeoutId = setTimeout(function () { self._advance(); }, ms);
  };

  // ─── Progress bar ──────────────────────────────────────────────

  AdRotator.prototype._startProgress = function (ms) {
    var bar = this.bar;
    bar.classList.remove('ad-progress--running');
    bar.style.removeProperty('width');
    bar.style.setProperty('--ad-duration', ms + 'ms');
    void bar.offsetWidth; // reflow
    bar.classList.add('ad-progress--running');
  };

  AdRotator.prototype._stopProgress = function () {
    if (!this.bar) return;
    var bar = this.bar;
    var w   = getComputedStyle(bar).width;
    var cw  = getComputedStyle(this.container).width;
    bar.classList.remove('ad-progress--running');
    bar.style.width = cw ? (parseFloat(w) / parseFloat(cw) * 100).toFixed(2) + '%' : '0%';
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

    if (this.bar) this._stopProgress();

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
        self._stopProgress();
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
