(function () {
  const listEl = document.getElementById('quest-list');
  const emptyEl = document.getElementById('quest-empty');
  const messageEl = document.getElementById('quest-message');
  const bgVideo = document.getElementById('quest-bg-video');

  // 背景影片每次進頁播放；結束後停在最後一幀（面板一進頁就顯示，不延遲）
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

    bgVideo.loop = false;
    bgVideo.muted = true;
    bgVideo.addEventListener('ended', freezeLastFrame);

    const playPromise = bgVideo.play();
    if (playPromise && typeof playPromise.catch === 'function') {
      playPromise.catch(function () {
        // 自動播放失敗時至少停在 poster
      });
    }
  }

  setupBgVideo();

  const QUEST_TYPE_TEXT = {
    DAILY: '每日任務',
    WEEKLY: '每週任務',
    HIDDEN: '隱藏任務'
  };

  const CONDITION_TEXT = {
    PRACTICE_COUNT: '練習次數',
    PRACTICE_DAYS: '練習天數',
    DISTINCT_SONGS: '不同曲目數',
    CONSECUTIVE_DAYS: '連續練習天數',
    TOTAL_UPLOADS: '累積上傳次數',
    RETURN_AFTER_GAP: '間隔後再練習'
  };

  const STATUS_TEXT = {
    COMPLETED: '已完成',
    ACTIVE: '進行中',
    EXPIRED: '已過期'
  };

  let studentId = null;
  let expandedKey = null;
  let questCache = [];

  function showMessage(text) {
    messageEl.textContent = text || '';
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatExpires(value) {
    if (!value) {
      return '無期限';
    }
    return String(value).replace('T', ' ').slice(0, 19);
  }

  function progressPercent(current, target) {
    if (!target || target <= 0) {
      return 0;
    }
    return Math.min(100, Math.round((current / target) * 100));
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

  function renderQuests(quests) {
    listEl.innerHTML = '';
    emptyEl.hidden = quests.length > 0;

    quests.forEach(function (quest, index) {
      const key = String(index);
      const card = document.createElement('article');
      card.className = 'quest-card';
      if (expandedKey === key) {
        card.classList.add('is-open');
      }

      const typeLabel = QUEST_TYPE_TEXT[quest.quest_type] || quest.quest_type;
      const statusLabel = STATUS_TEXT[quest.quest_status] || quest.quest_status;
      const conditionLabel = CONDITION_TEXT[quest.condition_type] || quest.condition_type;
      const current = quest.progress_value || 0;
      const target = quest.condition_value || 0;
      const percent = progressPercent(current, target);

      card.innerHTML =
        '<button type="button" class="quest-summary" aria-expanded="' +
        (expandedKey === key ? 'true' : 'false') +
        '">' +
        '<span class="quest-summary__name">' + escapeHtml(quest.quest_name) + '</span>' +
        '<span class="quest-summary__meta">' + escapeHtml(typeLabel) + '</span>' +
        '<span class="quest-summary__meta">' + escapeHtml(current + ' / ' + target) + '</span>' +
        '<span class="quest-summary__meta">' + escapeHtml(statusLabel) + '</span>' +
        '</button>' +
        '<div class="quest-detail">' +
        '<p>條件：' + escapeHtml(conditionLabel) + ' ' + escapeHtml(target) + '</p>' +
        '<p>獎勵：經驗 ' + escapeHtml(quest.reward_xp) + '／金幣 ' + escapeHtml(quest.reward_coin) + '</p>' +
        '<p>到期時間：' + escapeHtml(formatExpires(quest.expires_at)) + '</p>' +
        '<div class="progress" aria-hidden="true"><div class="progress__bar" style="width:' + percent + '%"></div></div>' +
        '</div>';

      card.querySelector('.quest-summary').addEventListener('click', function () {
        expandedKey = expandedKey === key ? null : key;
        renderQuests(questCache);
      });

      listEl.appendChild(card);
    });
  }

  async function loadQuests() {
    const response = await fetch('/api/students/' + studentId + '/quests', {
      credentials: 'same-origin'
    });
    const data = await response.json().catch(function () {
      return {};
    });
    if (!response.ok) {
      showMessage(data.message || '無法載入任務');
      return;
    }
    questCache = data.data || [];
    if (!questCache.length && data.message) {
      emptyEl.textContent = data.message;
    } else {
      emptyEl.textContent = '目前沒有任務';
    }
    renderQuests(questCache);
  }

  async function init() {
    try {
      const user = await ensureStudent();
      if (!user) {
        return;
      }
      await loadQuests();
    } catch (error) {
      showMessage('載入任務失敗，請重新登入');
    }
  }

  init();
})();
