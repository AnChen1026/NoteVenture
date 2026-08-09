(function () {
  const trackEl = document.querySelector('[data-carousel-track]');
  const dotsEl = document.querySelector('[data-carousel-dots]');
  const AUTO_MS = 3000;

  let programs = [];
  let index = 0;
  let autoTimer = null;

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function updateDots() {
    if (!dotsEl) {
      return;
    }
    const dots = dotsEl.querySelectorAll('.board-dot');
    dots.forEach(function (dot, i) {
      dot.classList.toggle('is-active', i === index);
    });
  }

  function goTo(nextIndex, smooth) {
    if (!trackEl || !programs.length) {
      return;
    }
    if (nextIndex >= programs.length) {
      nextIndex = 0;
    }
    if (nextIndex < 0) {
      nextIndex = programs.length - 1;
    }
    index = nextIndex;
    const width = trackEl.clientWidth;
    trackEl.scrollTo({
      left: width * index,
      behavior: smooth === false ? 'auto' : 'smooth'
    });
    updateDots();
  }

  function stopAuto() {
    if (autoTimer !== null) {
      window.clearInterval(autoTimer);
      autoTimer = null;
    }
  }

  function startAuto() {
    stopAuto();
    if (programs.length <= 1) {
      return;
    }
    autoTimer = window.setInterval(function () {
      goTo(index + 1, true);
    }, AUTO_MS);
  }

  function renderPrograms(items) {
    programs = items || [];
    index = 0;
    stopAuto();

    if (!trackEl || !dotsEl) {
      return;
    }

    trackEl.innerHTML = '';
    dotsEl.innerHTML = '';

    if (!programs.length) {
      const empty = document.createElement('div');
      empty.className = 'board-card';
      empty.innerHTML =
        '<div class="board-card__poster board-card__poster--empty">無資料</div>' +
        '<div class="board-card__body">' +
        '<h2 class="board-card__title">近一個月暫無音樂相關節目</h2>' +
        '</div>';
      trackEl.appendChild(empty);
      return;
    }

    programs.forEach(function (item, i) {
      const card = document.createElement('a');
      card.className = 'board-card';
      card.href = item.url || '#';
      card.target = '_blank';
      card.rel = 'noopener noreferrer';
      card.setAttribute('aria-label', (item.title || '節目') + '，另開兩廳院頁面');

      const dateText = item.start_date === item.end_date
        ? (item.start_date || '')
        : ((item.start_date || '') + ' ~ ' + (item.end_date || ''));

      const posterHtml = item.cover_url
        ? '<img class="board-card__poster" src="' + escapeHtml(item.cover_url) + '" alt="" loading="lazy">'
        : '<div class="board-card__poster board-card__poster--empty">無海報</div>';

      card.innerHTML =
        posterHtml +
        '<div class="board-card__body">' +
        '<h2 class="board-card__title">' + escapeHtml(item.title || '未命名節目') + '</h2>' +
        '<p class="board-card__meta">' + escapeHtml(dateText) +
        (item.category ? ' ｜ ' + escapeHtml(item.category) : '') +
        '</p>' +
        '<p class="board-card__brief">' + escapeHtml(item.brief || '') + '</p>' +
        '</div>';

      trackEl.appendChild(card);

      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'board-dot' + (i === 0 ? ' is-active' : '');
      dot.setAttribute('aria-label', '第 ' + (i + 1) + ' 則');
      dot.addEventListener('click', function () {
        goTo(i, true);
        startAuto();
      });
      dotsEl.appendChild(dot);
    });

    updateDots();
    startAuto();
  }

  function syncIndexFromScroll() {
    if (!trackEl || !programs.length) {
      return;
    }
    const width = trackEl.clientWidth || 1;
    const next = Math.round(trackEl.scrollLeft / width);
    if (next !== index) {
      index = Math.max(0, Math.min(programs.length - 1, next));
      updateDots();
    }
  }

  function renderMessage(title, detail) {
    programs = [];
    stopAuto();
    if (!trackEl || !dotsEl) {
      return;
    }
    trackEl.innerHTML = '';
    dotsEl.innerHTML = '';
    const empty = document.createElement('div');
    empty.className = 'board-card';
    empty.innerHTML =
      '<div class="board-card__poster board-card__poster--empty">看板</div>' +
      '<div class="board-card__body">' +
      '<h2 class="board-card__title">' + escapeHtml(title) + '</h2>' +
      (detail
        ? '<p class="board-card__brief">' + escapeHtml(detail) + '</p>'
        : '') +
      '</div>';
    trackEl.appendChild(empty);
  }

  async function loadPrograms() {
    renderMessage('節目載入中…', '正在向兩廳院取得近一個月音樂節目');
    try {
      const response = await fetch('/api/class/ntch-programs', {
        credentials: 'same-origin'
      });
      const data = await response.json().catch(function () {
        return {};
      });
      if (!response.ok) {
        renderMessage(
          '目前無法取得節目',
          data.message || '請稍後再重新整理頁面'
        );
        return;
      }
      const items = data.data || [];
      if (!items.length) {
        renderMessage('近一個月暫無音樂相關節目', '');
        return;
      }
      renderPrograms(items);
    } catch (error) {
      renderMessage('節目載入失敗', '請確認網路後重新整理');
    }
  }

  if (trackEl) {
    trackEl.addEventListener('scroll', function () {
      window.requestAnimationFrame(syncIndexFromScroll);
    });
    // 滑鼠移入暫停、移出繼續
    trackEl.addEventListener('mouseenter', stopAuto);
    trackEl.addEventListener('mouseleave', startAuto);
  }

  loadPrograms();
})();
