(function () {
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
      }
    } catch (error) {
      window.location.href = '/student/login';
    }
  }

  ensureStudentLogin();
})();
