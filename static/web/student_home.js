(function () {
  const welcomeEl = document.getElementById('welcome');

  async function ensureStudentLogin() {
    try {
      const response = await fetch('/api/me', {
        method: 'GET',
        credentials: 'same-origin'
      });

      if (response.status === 401) {
        window.location.href = '/student/login';
        return;
      }

      const data = await response.json().catch(function () {
        return null;
      });

      if (!data || data.role !== 'student' || !data.user) {
        window.location.href = '/student/login';
        return;
      }

      welcomeEl.textContent = data.user.student_name + '，歡迎回到 Melody Town';
    } catch (error) {
      welcomeEl.textContent = '無法確認登入狀態，請重新登入';
      setTimeout(function () {
        window.location.href = '/student/login';
      }, 1200);
    }
  }

  ensureStudentLogin();
})();
