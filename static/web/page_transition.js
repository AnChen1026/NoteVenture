(function () {
  var LEAVE_MS = 280;
  var leaving = false;

  function getStage() {
    return document.querySelector('.stage') || document.body;
  }

  function playEnter() {
    var stage = getStage();
    stage.classList.add('page-transition');
    // 觸發 reflow，確保動畫會重播
    void stage.offsetWidth;
    stage.classList.add('is-page-enter');
  }

  function navigateWithTransition(url) {
    if (!url) {
      return;
    }

    // 同頁不重播
    if (url === window.location.pathname) {
      return;
    }

    if (leaving) {
      return;
    }
    leaving = true;

    var stage = getStage();
    stage.classList.add('page-transition');
    stage.classList.remove('is-page-enter');
    stage.classList.add('is-page-leave');

    window.setTimeout(function () {
      window.location.href = url;
    }, LEAVE_MS);
  }

  document.addEventListener('DOMContentLoaded', function () {
    playEnter();

    document.addEventListener('click', function (event) {
      var link = event.target.closest('a[href]');
      if (!link) {
        return;
      }

      var href = link.getAttribute('href');
      if (!href || href.charAt(0) === '#') {
        return;
      }
      if (link.target === '_blank' || link.hasAttribute('download')) {
        return;
      }
      // 只攔截學生站內跳轉
      if (href.indexOf('/student/') !== 0) {
        return;
      }

      event.preventDefault();
      navigateWithTransition(href);
    });
  });

  window.navigateWithTransition = navigateWithTransition;
})();
