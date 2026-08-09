(function () {
  var STORAGE_KEY = 'na_bgm_enabled';
  var isEmbed = window.self !== window.top;

  // iframe 內頁：不播自己的 BGM，改通知外層殼
  if (isEmbed) {
    document.documentElement.classList.add('is-spa-embed');

    function postToParent(type) {
      try {
        window.parent.postMessage({ type: type }, window.location.origin);
      } catch (error) {
        // ignore
      }
    }

    window.NoteAdventureBgm = {
      pause: function () { postToParent('na-bgm-pause'); },
      resume: function () { postToParent('na-bgm-resume'); },
      tryPlay: function () { postToParent('na-bgm-tryplay'); },
      isEnabled: function () { return true; }
    };

    // 使用者點內頁時，請外層嘗試開始播（解鎖 autoplay）
    document.addEventListener('pointerdown', function () {
      postToParent('na-bgm-tryplay');
    }, { passive: true });

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

  if (isEnabled()) {
    tryPlay();
    audio.addEventListener('canplay', function onReady() {
      tryPlay();
      audio.removeEventListener('canplay', onReady);
    });
  }

  document.addEventListener('pointerdown', function () {
    if (isEnabled() && audio.paused && !pausedByApp) {
      tryPlay();
    }
  }, { passive: true });

  window.NoteAdventureBgm = {
    pause: pauseBgm,
    resume: resumeBgm,
    tryPlay: tryPlay,
    isEnabled: isEnabled
  };
})();
