(function () {
  var frame = document.getElementById('spa-frame');
  if (!frame) {
    return;
  }

  var PATH_TO_HASH = {
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

  var HASH_TO_PATH = {
    login: '/student/login',
    home: '/student/home',
    practice: '/student/practice',
    shop: '/student/shop',
    quests: '/student/quests',
    pet: '/student/pet',
    class: '/student/class',
    settings: '/student/settings',
    backpack: '/student/backpack'
  };

  function pathFromHash() {
    var key = (window.location.hash || '').replace(/^#/, '');
    return HASH_TO_PATH[key] || '/student/login';
  }

  function syncHashFromFrame() {
    try {
      var path = frame.contentWindow.location.pathname;
      var key = PATH_TO_HASH[path];
      if (key) {
        var next = '#' + key;
        if (window.location.hash !== next) {
          history.replaceState(null, '', next);
        }
      }
    } catch (error) {
      // 跨域時略過
    }
  }

  // 初次：依網址 hash 開對應頁
  frame.src = pathFromHash();

  frame.addEventListener('load', function () {
    syncHashFromFrame();
    try {
      frame.contentDocument.documentElement.classList.add('is-spa-embed');
    } catch (error) {
      // ignore
    }
  });

  window.addEventListener('hashchange', function () {
    var path = pathFromHash();
    try {
      if (frame.contentWindow.location.pathname !== path) {
        frame.src = path;
      }
    } catch (error) {
      frame.src = path;
    }
  });

  // 內頁通知：BGM 暫停／恢復／嘗試播放
  window.addEventListener('message', function (event) {
    if (event.origin !== window.location.origin) {
      return;
    }
    var data = event.data || {};
    if (!window.NoteAdventureBgm) {
      return;
    }
    if (data.type === 'na-bgm-pause') {
      window.NoteAdventureBgm.pause();
    } else if (data.type === 'na-bgm-resume') {
      window.NoteAdventureBgm.resume();
    } else if (data.type === 'na-bgm-tryplay' && typeof window.NoteAdventureBgm.tryPlay === 'function') {
      window.NoteAdventureBgm.tryPlay();
    }
  });
})();

