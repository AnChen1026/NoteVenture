(function () {
  const form = document.getElementById('login-form');
  const messageEl = document.getElementById('message');
  const loginBtn = document.getElementById('login-btn');

  function showMessage(text, type) {
    messageEl.textContent = text;
    messageEl.classList.remove('is-error', 'is-ok');
    if (type) {
      messageEl.classList.add(type);
    }
  }

  form.addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
      showMessage('請輸入帳號與密碼', 'is-error');
      return;
    }

    loginBtn.disabled = true;
    showMessage('登入中…', '');

    try {
      const response = await fetch('/api/students/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({ username, password })
      });

      const data = await response.json().catch(function () {
        return { message: '伺服器回應格式錯誤' };
      });

      if (!response.ok) {
        showMessage(data.message || '登入失敗', 'is-error');
        return;
      }

      const name = (data.user && data.user.student_name) || username;
      showMessage('登入成功，' + name + ' 你好！（此頁目前僅預覽登入效果）', 'is-ok');
    } catch (error) {
      showMessage('無法連接伺服器，請確認 Flask 已啟動', 'is-error');
    } finally {
      loginBtn.disabled = false;
    }
  });
})();
