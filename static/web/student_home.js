(function () {
  async function ensureStudentLogin() {
    try {
      const response = await fetch('/api/me', {
        method: 'GET',
        credentials: 'same-origin'
      });

      if (response.status === 401) {
        window.navigateWithTransition('/student/login');
        return;
      }

      const data = await response.json().catch(function () {
        return null;
      });

      if (!data || data.role !== 'student' || !data.user) {
        window.navigateWithTransition('/student/login');
      }
    } catch (error) {
      window.navigateWithTransition('/student/login');
    }
  }

  async function logoutStudent() {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        credentials: 'same-origin'
      });
    } catch (error) {
      // 即使 API 失敗也導回登入頁
    }
    window.navigateWithTransition('/student/login');
  }

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function () {
      logoutStudent();
    });
  }

  ensureStudentLogin();
})();
