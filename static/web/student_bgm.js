(function () {
  var STORAGE_KEY = 'na_bgm_enabled';
  var TIME_KEY = 'na_bgm_time';
  var isEmbed = window.self !== window.top;

  // iframe 內頁：不建立 audio，只通知外層殼
  if (isEmbed) {
    document.documentElement.classList.add('is-spa-embed');

    function postToParent(type, extra) {
      var payload = { type: type };
      if (extra) {
        Object.keys(extra).forEach(function (k) {
          payload[k] = extra[k];
        });
      }
      try {
        window.parent.postMessage(payload, window.location.origin);
      } catch (error) {
        // ignore
      }
    }

    window.NoteAdventureBgm = {
      pause: function () { postToParent('na-bgm-pause', { reason: 'practice' }); },
      resume: function () { postToParent('na-bgm-resume'); },
      tryPlay: function () { postToParent('na-bgm-ensure'); },
      isEnabled: function () { return true; }
    };

    // 只在「外層可能被擋自動播放」時請求續播，不要每次點擊狂送
    document.addEventListener('pointerdown', function () {
      postToParent('na-bgm-ensure');
    }, { passive: true, once: true });

    return;
  }

  var audio = document.createElement('audio');
  audio.src = '/assets/material/bgm/bgm.mp3';
  audio.loop = true;
  audio.preload = 'auto';
  audio.volume = 0.32;
  audio.muted = false;
  audio.setAttribute('playsinline', '');
  audio.setAttribute('webkit-playsinline', '');

  var pausedByApp = false;
  var spaLock = false; // 換場期間禁止誤暫停
  var btn = null;

  function isEnabled() {
    var saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved === null) {
      return true;
    }
    return saved === '1';
  }

  function setEnabled(on) {
    sessionStorage.setItem(STORAGE_KEY, on ? '1' : '0');
  }

  function saveTime() {
    try {
      if (audio.currentTime && isFinite(audio.currentTime)) {
        sessionStorage.setItem(TIME_KEY, String(audio.currentTime));
      }
    } catch (error) {
      // ignore
    }
  }

  function restoreTime() {
    var raw = sessionStorage.getItem(TIME_KEY);
    var t = raw ? parseFloat(raw) : 0;
    if (t > 0 && isFinite(t)) {
      try {
        audio.currentTime = t;
      } catch (error) {
        // ignore
      }
    }
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

  // 若已在播就不動 currentTime，避免換頁聽起來像「斷掉重來」
  function ensurePlaying() {
    if (!isEnabled() || pausedByApp) {
      updateButton();
      return Promise.resolve();
    }
    if (!audio.paused) {
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

  function pauseBgm(reason) {
    // 換場期間忽略暫停；只允許琴房錄音等明確原因
    if (spaLock && reason !== 'practice') {
      return;
    }
    pausedByApp = true;
    saveTime();
    audio.pause();
    updateButton();
  }

  function resumeBgm() {
    if (!isEnabled()) {
      return;
    }
    pausedByApp = false;
    ensurePlaying();
  }

  function setSpaLock(locked) {
    spaLock = !!locked;
    if (!spaLock) {
      ensurePlaying();
    }
  }

  function toggleBgm() {
    if (isEnabled() && !audio.paused) {
      setEnabled(false);
      saveTime();
      audio.pause();
      updateButton();
      return;
    }
    setEnabled(true);
    pausedByApp = false;
    ensurePlaying();
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
  restoreTime();

  audio.addEventListener('timeupdate', function () {
    // 節流：約每 2 秒記一次進度
    if (!audio._lastSave || Date.now() - audio._lastSave > 2000) {
      audio._lastSave = Date.now();
      saveTime();
    }
  });

  if (isEnabled()) {
    ensurePlaying();
    audio.addEventListener('canplay', function onReady() {
      restoreTime();
      ensurePlaying();
      audio.removeEventListener('canplay', onReady);
    });
  }

  document.addEventListener('pointerdown', function () {
    if (isEnabled() && audio.paused && !pausedByApp) {
      ensurePlaying();
    }
  }, { passive: true });

  window.NoteAdventureBgm = {
    pause: pauseBgm,
    resume: resumeBgm,
    tryPlay: ensurePlaying,
    ensure: ensurePlaying,
    setSpaLock: setSpaLock,
    isEnabled: isEnabled
  };
})();
