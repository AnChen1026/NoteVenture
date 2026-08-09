(function () {
  const form = document.getElementById('password-form');
  const messageEl = document.getElementById('message');
  const submitBtn = document.getElementById('submit-btn');
  const bgVideo = document.getElementById('settings-bg-video');

  // 背景影片每次進頁播放；結束後停在最後一幀
  function setupBgVideo() {
    if (!bgVideo) {
      return;
    }

    function freezeLastFrame() {
      bgVideo.pause();
      if (bgVideo.duration && Number.isFinite(bgVideo.duration)) {
        try {
          bgVideo.currentTime = Math.max(0, bgVideo.duration - 0.05);
        } catch (error) {
          // 忽略尚未就緒時的 currentTime 錯誤
        }
      }
    }

    function tryPlay() {
      bgVideo.muted = true;
      bgVideo.setAttribute('playsinline', '');
      bgVideo.setAttribute('webkit-playsinline', '');
      const playPromise = bgVideo.play();
      if (playPromise && typeof playPromise.catch === 'function') {
        playPromise.catch(function () {
          // 自動播放被擋：等使用者第一次點擊再播
        });
      }
    }

    bgVideo.loop = false;
    bgVideo.controls = false;
    bgVideo.muted = true;
    bgVideo.addEventListener('ended', freezeLastFrame);
    bgVideo.addEventListener('loadeddata', tryPlay);

    // 行動裝置／瀏覽器擋 autoplay 時，第一次點畫面再播
    function playOnFirstGesture() {
      tryPlay();
      document.removeEventListener('pointerdown', playOnFirstGesture);
      document.removeEventListener('touchstart', playOnFirstGesture);
    }
    document.addEventListener('pointerdown', playOnFirstGesture, { passive: true });
    document.addEventListener('touchstart', playOnFirstGesture, { passive: true });

    tryPlay();
  }

  setupBgVideo();

  function showMessage(text, type) {
    messageEl.textContent = text || '';
    messageEl.classList.remove('is-error', 'is-ok');
    if (type) {
      messageEl.classList.add(type);
    }
  }

  async function ensureStudentLogin() {
    try {
      const response = await fetch('/api/me', {
        method: 'GET',
        credentials: 'same-origin'
      });

      if (response.status === 401) {
        window.navigateWithTransition('/student/login');
        return false;
      }

      const data = await response.json().catch(function () {
        return null;
      });

      if (!data || data.role !== 'student' || !data.user) {
        window.navigateWithTransition('/student/login');
        return false;
      }
      return true;
    } catch (error) {
      window.navigateWithTransition('/student/login');
      return false;
    }
  }

  form.addEventListener('submit', async function (event) {
    event.preventDefault();

    const oldPassword = document.getElementById('old-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (!oldPassword || !newPassword || !confirmPassword) {
      showMessage('請完整輸入舊密碼與新密碼', 'is-error');
      return;
    }
    if (newPassword !== confirmPassword) {
      showMessage('兩次新密碼不一致', 'is-error');
      return;
    }

    submitBtn.disabled = true;
    showMessage('修改中…', '');

    try {
      const response = await fetch('/api/students/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
          confirm_password: confirmPassword
        })
      });

      const data = await response.json().catch(function () {
        return { message: '伺服器回應格式錯誤' };
      });

      if (!response.ok) {
        showMessage(data.message || '密碼修改失敗', 'is-error');
        return;
      }

      showMessage(data.message || '密碼修改成功', 'is-ok');
      form.reset();
    } catch (error) {
      showMessage('無法連線伺服器', 'is-error');
    } finally {
      submitBtn.disabled = false;
    }
  });

  ensureStudentLogin();
})();
