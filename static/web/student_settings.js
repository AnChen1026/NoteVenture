(function () {
  const form = document.getElementById('password-form');
  const messageEl = document.getElementById('message');
  const submitBtn = document.getElementById('submit-btn');

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
