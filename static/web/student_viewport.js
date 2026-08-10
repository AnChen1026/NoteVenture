(function () {
  var isEmbed = window.self !== window.top;
  if (isEmbed) {
    document.documentElement.classList.add('is-spa-embed');
  }

  // 正式入口改為一頁版：頂層直接開舊路徑時，導到 /student/app
  // iframe 內不導，避免殼層載入 /student/login 時形成迴圈
  if (!isEmbed) {
    var path = window.location.pathname;
    var pathToHash = {
      '/student/login': 'login',
      '/student/home': 'home',
      '/student/practice': 'practice',
      '/student/shop': 'shop',
      '/student/quests': 'quests',
      '/student/pet': 'pet',
      '/student/class': 'class',
      '/student/settings': 'settings',
      '/student/backpack': 'backpack'
    };
    if (pathToHash[path]) {
      window.location.replace('/student/app#' + pathToHash[path]);
      return;
    }
  }

  // ---------- 手機鍵盤：只在收起後重置捲動，不要鎖死像素高度 ----------
  function isTypingField(el) {
    if (!el || !el.tagName) {
      return false;
    }
    var tag = el.tagName.toUpperCase();
    return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || el.isContentEditable;
  }

  function resetScroll() {
    try {
      window.scrollTo(0, 0);
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    } catch (error) {
      // ignore
    }
  }

  function recoverAfterKeyboard() {
    resetScroll();
    // 少數瀏覽器會留下 visualViewport 偏移，再補一次
    window.setTimeout(resetScroll, 50);
    window.setTimeout(resetScroll, 300);
  }

  document.addEventListener('focusout', function (event) {
    if (!isTypingField(event.target)) {
      return;
    }
    // 若焦點立刻移到另一個輸入框，不要重置
    window.setTimeout(function () {
      if (isTypingField(document.activeElement)) {
        return;
      }
      recoverAfterKeyboard();
    }, 0);
  });

  // 直向時顯示「請橫放」遮罩（殼層負責；iframe 內不重複）
  function ensureRotateGate() {
    if (isEmbed || document.getElementById('rotate-gate')) {
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

  // 鎖住外層頁面捲動（內層清單仍可滾）
  function lockPageScroll(event) {
    var target = event.target;
    if (!target || !target.closest) {
      event.preventDefault();
      return;
    }
    if (target.closest('.rotate-gate')) {
      return;
    }
    // 輸入框區域允許瀏覽器處理（鍵盤相關）
    if (isTypingField(target) || target.closest('input, textarea, select, label, .password-form, .login-form')) {
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

  // 全螢幕由殼層處理；iframe 內不重複綁
  if (isEmbed) {
    return;
  }

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
