(function () {
  var STORAGE_KEY = 'na_bgm_enabled';
  var audio = document.createElement('audio');
  audio.src = '/assets/material/bgm/bgm.mp3';
  audio.loop = true;
  audio.preload = 'auto';
  audio.volume = 0.32;
  // 提高自動播放成功率（仍可能被行動瀏覽器擋下）
  audio.muted = false;
  audio.setAttribute('playsinline', '');
  audio.setAttribute('webkit-playsinline', '');

  var pausedByApp = false;
  var btn = null;

  function isEnabled() {
    var saved = sessionStorage.getItem(STORAGE_KEY);
    // 預設開啟；只有使用者明確關掉才是 '0'
    if (saved === null) {
      return true;
    }
    return saved === '1';
  }

  function setEnabled(on) {
    sessionStorage.setItem(STORAGE_KEY, on ? '1' : '0');
  }

  function updateButton() {
    if (!btn) {
      return;
    }
    var on = isEnabled() && !audio.paused;
    btn.classList.toggle('is-off', !on);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.title = on ? '關閉背景音樂' : '開啟背景音樂';
    btn.setAttribute('aria-label', on ? '關閉背景音樂' : '開啟背景音樂');
    btn.textContent = on ? '♪' : '🔇';
  }

  function tryPlay() {
    if (!isEnabled() || pausedByApp) {
      updateButton();
      return Promise.resolve();
    }
    audio.muted = false;
    return audio.play().then(function () {
      updateButton();
    }).catch(function () {
      updateButton();
    });
  }

  function pauseBgm() {
    pausedByApp = true;
    audio.pause();
    updateButton();
  }

  function resumeBgm() {
    if (!isEnabled()) {
      return;
    }
    pausedByApp = false;
    tryPlay();
  }

  function toggleBgm() {
    if (isEnabled() && !audio.paused) {
      setEnabled(false);
      audio.pause();
      updateButton();
      return;
    }
    setEnabled(true);
    pausedByApp = false;
    tryPlay();
  }

  function ensureUi() {
    var stage = document.querySelector('.stage');
    if (!stage || document.getElementById('bgm-toggle')) {
      return;
    }
    btn = document.createElement('button');
    btn.id = 'bgm-toggle';
    btn.type = 'button';
    btn.className = 'bgm-toggle is-off';
    btn.textContent = '🔇';
    btn.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      toggleBgm();
    });
    stage.appendChild(btn);
    updateButton();
  }

  ensureUi();

  // 一進頁就嘗試播放（桌機有時成功；手機多半仍需一次點擊）
  if (isEnabled()) {
    tryPlay();
    audio.addEventListener('canplay', function onReady() {
      tryPlay();
      audio.removeEventListener('canplay', onReady);
    });
  }

  // 被擋時：使用者第一次點畫面任意處就開始播（登入、地圖熱區都算）
  document.addEventListener('pointerdown', function () {
    if (isEnabled() && audio.paused && !pausedByApp) {
      tryPlay();
    }
  }, { passive: true });

  window.NoteAdventureBgm = {
    pause: pauseBgm,
    resume: resumeBgm,
    isEnabled: isEnabled
  };
})();
