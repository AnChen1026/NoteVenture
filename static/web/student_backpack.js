(function () {
  const gridEl = document.getElementById('backpack-grid');
  const messageEl = document.getElementById('backpack-message');
  const SLOT_COUNT = 30;

  let studentId = null;

  function showMessage(text, type) {
    messageEl.textContent = text || '';
    messageEl.classList.remove('is-error');
    if (type) {
      messageEl.classList.add(type);
    }
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  async function ensureStudent() {
    const response = await fetch('/api/me', { credentials: 'same-origin' });
    if (response.status === 401) {
      window.navigateWithTransition('/student/login');
      return null;
    }
    const data = await response.json();
    if (!data || data.role !== 'student' || !data.user) {
      window.navigateWithTransition('/student/login');
      return null;
    }
    studentId = data.user.student_id;
    return data.user;
  }

  function renderSlots(items) {
    gridEl.innerHTML = '';

    for (let i = 0; i < SLOT_COUNT; i += 1) {
      const item = items[i];
      const slot = document.createElement('div');
      slot.className = 'backpack-slot';
      slot.setAttribute('role', 'listitem');

      if (item) {
        slot.classList.add('is-filled');
        slot.innerHTML =
          '<span class="backpack-slot__name">' +
          escapeHtml(item.item_name || '未命名商品') +
          '</span>';
        slot.title = item.item_name || '';
      } else {
        slot.setAttribute('aria-label', '空格子');
      }

      gridEl.appendChild(slot);
    }
  }

  async function loadBackpack() {
    const response = await fetch('/api/students/' + studentId + '/purchases', {
      credentials: 'same-origin'
    });
    const data = await response.json().catch(function () {
      return {};
    });

    if (!response.ok) {
      showMessage(data.message || '無法載入背包', 'is-error');
      renderSlots([]);
      return;
    }

    const allItems = Array.isArray(data.data) ? data.data : [];
    const virtualItems = allItems.filter(function (item) {
      return item && item.item_type === 'VIRTUAL';
    });

    renderSlots(virtualItems.slice(0, SLOT_COUNT));
    showMessage('');
  }

  async function init() {
    try {
      const user = await ensureStudent();
      if (!user) {
        return;
      }
      await loadBackpack();
    } catch (error) {
      showMessage('載入背包失敗，請重新登入', 'is-error');
      renderSlots([]);
    }
  }

  init();
})();
