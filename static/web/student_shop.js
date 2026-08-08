(function () {
  const coinEl = document.getElementById('coin-value');
  const listEl = document.getElementById('item-list');
  const emptyEl = document.getElementById('shop-empty');
  const messageEl = document.getElementById('shop-message');

  const TYPE_TEXT = {
    VIRTUAL: '虛擬商品',
    PHYSICAL: '實體商品'
  };

  let studentId = null;
  let expandedId = null;

  function showMessage(text, type) {
    messageEl.textContent = text || '';
    messageEl.classList.remove('is-error', 'is-ok');
    if (type) {
      messageEl.classList.add(type);
    }
  }

  function stockText(stock) {
    if (stock === null || stock === undefined) {
      return '不限量';
    }
    return String(stock);
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
    coinEl.textContent = data.user.total_coin;
    return data.user;
  }

  function renderItems(items) {
    listEl.innerHTML = '';
    emptyEl.hidden = items.length > 0;

    items.forEach(function (item) {
      const card = document.createElement('article');
      card.className = 'item-card';
      card.dataset.itemId = String(item.item_id);
      if (expandedId === item.item_id) {
        card.classList.add('is-open');
      }

      const typeLabel = TYPE_TEXT[item.item_type] || item.item_type;
      const desc = item.description && String(item.description).trim()
        ? item.description
        : '（沒有商品說明）';

      card.innerHTML =
        '<button type="button" class="item-summary" aria-expanded="' +
        (expandedId === item.item_id ? 'true' : 'false') +
        '">' +
        '<span class="item-summary__name">' + escapeHtml(item.item_name) + '</span>' +
        '<span class="item-summary__meta">' + escapeHtml(typeLabel) + '</span>' +
        '<span class="item-summary__meta">' + escapeHtml(item.price) + ' 金幣</span>' +
        '<span class="item-summary__meta">' + escapeHtml(stockText(item.stock)) + '</span>' +
        '</button>' +
        '<div class="item-detail">' +
        '<p class="item-detail__desc">' + escapeHtml(desc) + '</p>' +
        '<button type="button" class="buy-btn">購買</button>' +
        '</div>';

      const summaryBtn = card.querySelector('.item-summary');
      const buyBtn = card.querySelector('.buy-btn');

      summaryBtn.addEventListener('click', function () {
        if (expandedId === item.item_id) {
          expandedId = null;
        } else {
          expandedId = item.item_id;
        }
        renderItems(items);
      });

      buyBtn.addEventListener('click', function () {
        purchaseItem(item.item_id, buyBtn);
      });

      listEl.appendChild(card);
    });
  }

  async function loadItems() {
    const response = await fetch('/api/students/' + studentId + '/shop-items', {
      credentials: 'same-origin'
    });
    const data = await response.json().catch(function () {
      return {};
    });
    if (!response.ok) {
      showMessage(data.message || '無法載入商品', 'is-error');
      return;
    }
    renderItems(data.data || []);
  }

  async function purchaseItem(itemId, buyBtn) {
    buyBtn.disabled = true;
    showMessage('購買中…', '');

    try {
      const response = await fetch('/api/shop-items/' + itemId + '/purchase', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json().catch(function () {
        return { message: '伺服器回應格式錯誤' };
      });

      if (!response.ok) {
        showMessage(data.message || '購買失敗', 'is-error');
        return;
      }

      if (typeof data.total_coin === 'number') {
        coinEl.textContent = data.total_coin;
      }
      showMessage(data.message || 'is-ok', '購買成功');
      expandedId = null;
      await loadItems();
    } catch (error) {
      showMessage('無法連接伺服器', 'is-error');
    } finally {
      buyBtn.disabled = false;
    }
  }

  async function init() {
    try {
      const user = await ensureStudent();
      if (!user) {
        return;
      }
      await loadItems();
    } catch (error) {
      showMessage('載入商店失敗，請重新登入', 'is-error');
    }
  }

  init();
})();
