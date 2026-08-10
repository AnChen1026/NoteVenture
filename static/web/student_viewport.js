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

  // ---------- 手機鍵盤：避免畫面被往上壓縮後不歸位 ----------
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
      if (window.visualViewport) {
        // iOS 鍵盤常留下 visualViewport offset
        window.scrollTo(0, 0);
      }
    } catch (error) {
      // ignore
    }
  }

  function refreshLayoutSize(force) {
    // 打字中（鍵盤多半開著）不要用縮小後的高度重算舞台，否則會「壓扁」
    if (!force && isTypingField(document.activeElement)) {
      resetScroll();
      return;
    }
    var h = window.innerHeight;
    var w = window.innerWidth;
    if (h > 0) {
      document.documentElement.style.setProperty('--layout-h', h + 'px');
    }
    if (w > 0) {
      document.documentElement.style.setProperty('--layout-w', w + 'px');
    }
    resetScroll();
  }

  // 先寫入一版穩定高度
  refreshLayoutSize(true);

  window.addEventListener('orientationchange', function () {
    window.setTimeout(function () {
      refreshLayoutSize(true);
    }, 250);
  });

  window.addEventListener('resize', function () {
    refreshLayoutSize(false);
  });

  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', function () {
      refreshLayoutSize(false);
    });
    window.visualViewport.addEventListener('scroll', function () {
      // 鍵盤把 visual viewport 推走時，立刻拉回
      resetScroll();
    });
  }

  document.addEventListener('focusin', function (event) {
    if (isTypingField(event.target)) {
      resetScroll();
    }
  });

  document.addEventListener('focusout', function () {
    // 鍵盤收起後稍等再重算，讓 innerHeight 恢復
    window.setTimeout(function () {
      refreshLayoutSize(true);
    }, 80);
    window.setTimeout(function () {
      refreshLayoutSize(true);
    }, 320);
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
      // ignore
    }
  }
})();
