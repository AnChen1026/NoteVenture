(function () {
  // 直向時顯示「請橫放」遮罩（各學生頁共用，自動插入）
  function ensureRotateGate() {
    if (document.getElementById('rotate-gate')) {
      return;
    }
    var gate = document.createElement('div');
    gate.id = 'rotate-gate';
    gate.className = 'rotate-gate';
    gate.setAttribute('role', 'dialog');
    gate.setAttribute('aria-live', 'polite');
    gate.setAttribute('aria-label', '請將裝置橫向放置');
    gate.innerHTML =
      '<div class="rotate-gate__icon" aria-hidden="true"></div>' +
      '<p class="rotate-gate__title">請將裝置橫放</p>' +
      '<p class="rotate-gate__hint">手機或平板請轉成橫向後，即可操作 Melody Town</p>';
    document.body.appendChild(gate);
  }

  ensureRotateGate();

  // 鎖住外層頁面捲動（內層 .item-list / .quest-list 仍可滾）
  function lockPageScroll(event) {
    var target = event.target;
    if (!target || !target.closest) {
      event.preventDefault();
      return;
    }
    // 橫放提示層本身不擋
    if (target.closest('.rotate-gate')) {
      return;
    }
    var scrollable = target.closest(
      '.item-list, .quest-list, .practice-panel, .settings-panel, .shop-panel, .quest-panel, .class-board'
    );
    if (scrollable) {
      return;
    }
    event.preventDefault();
  }

  document.addEventListener('touchmove', lockPageScroll, { passive: false });

  // 雙擊舞台嘗試全螢幕（iOS Safari 常不支援，失敗就略過）
  var lastTap = 0;
  var stage = document.querySelector('.stage');
  if (!stage) {
    return;
  }

  stage.addEventListener('dblclick', function () {
    toggleFullscreen();
  });

  stage.addEventListener('touchend', function (event) {
    var now = Date.now();
    if (now - lastTap < 300) {
      event.preventDefault();
      toggleFullscreen();
      lastTap = 0;
    } else {
      lastTap = now;
    }
  }, { passive: false });

  function toggleFullscreen() {
    var el = document.documentElement;
    try {
      if (!document.fullscreenElement && !document.webkitFullscreenElement) {
        if (el.requestFullscreen) {
          el.requestFullscreen();
        } else if (el.webkitRequestFullscreen) {
          el.webkitRequestFullscreen();
        }
      } else if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      }
    } catch (error) {
      // 行動瀏覽器不支援時略過
    }
  }
})();
