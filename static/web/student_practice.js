(function () {
  const songInput = document.getElementById('song-name');
  const recordBtn = document.getElementById('record-btn');
  const recordTimer = document.getElementById('record-timer');
  const previewBox = document.getElementById('preview-box');
  const previewAudio = document.getElementById('preview-audio');
  const durationText = document.getElementById('duration-text');
  const rerecordBtn = document.getElementById('rerecord-btn');
  const uploadBtn = document.getElementById('upload-btn');
  const messageEl = document.getElementById('practice-message');

  let studentId = null;
  let mediaStream = null;
  let mediaRecorder = null;
  let chunks = [];
  let recordedBlob = null;
  let recordedUrl = null;
  let audioDuration = 0;
  let recording = false;
  let timerId = null;
  let startedAt = 0;

  function showMessage(text, type) {
    messageEl.textContent = text || '';
    messageEl.classList.remove('is-error', 'is-ok');
    if (type) {
      messageEl.classList.add(type);
    }
  }

  function formatTime(totalSeconds) {
    const sec = Math.max(0, Math.floor(totalSeconds));
    const m = String(Math.floor(sec / 60)).padStart(2, '0');
    const s = String(sec % 60).padStart(2, '0');
    return m + ':' + s;
  }

  function pickMimeType() {
    const candidates = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus'
    ];
    if (!window.MediaRecorder || !MediaRecorder.isTypeSupported) {
      return '';
    }
    for (let i = 0; i < candidates.length; i += 1) {
      if (MediaRecorder.isTypeSupported(candidates[i])) {
        return candidates[i];
      }
    }
    return '';
  }

  function extensionForMime(mime) {
    if (mime.indexOf('mp4') !== -1) {
      return 'm4a';
    }
    if (mime.indexOf('ogg') !== -1) {
      return 'ogg';
    }
    return 'webm';
  }

  function clearPreviewUrl() {
    if (recordedUrl) {
      URL.revokeObjectURL(recordedUrl);
      recordedUrl = null;
    }
    previewAudio.removeAttribute('src');
    previewAudio.load();
  }

  function resetRecordingState() {
    chunks = [];
    recordedBlob = null;
    audioDuration = 0;
    clearPreviewUrl();
    previewBox.hidden = true;
    rerecordBtn.hidden = true;
    uploadBtn.hidden = true;
    uploadBtn.disabled = true;
    recordTimer.textContent = '00:00';
    recordTimer.classList.remove('is-recording');
    durationText.textContent = '';
    recordBtn.textContent = '開始錄音';
    recordBtn.classList.remove('is-recording');
    recordBtn.disabled = false;
  }

  function stopTimer() {
    if (timerId) {
      clearInterval(timerId);
      timerId = null;
    }
  }

  function startTimer() {
    startedAt = Date.now();
    stopTimer();
    timerId = setInterval(function () {
      const elapsed = (Date.now() - startedAt) / 1000;
      recordTimer.textContent = formatTime(elapsed);
    }, 200);
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

  async function startRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showMessage('此瀏覽器不支援麥克風錄音', 'is-error');
      return;
    }
    if (!window.MediaRecorder) {
      showMessage('此瀏覽器不支援錄音功能', 'is-error');
      return;
    }

    showMessage('請允許使用麥克風…', '');
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (error) {
      showMessage('無法取得麥克風權限', 'is-error');
      return;
    }

    chunks = [];
    const mimeType = pickMimeType();
    try {
      mediaRecorder = mimeType
        ? new MediaRecorder(mediaStream, { mimeType: mimeType })
        : new MediaRecorder(mediaStream);
    } catch (error) {
      showMessage('無法開始錄音', 'is-error');
      stopStream();
      return;
    }

    mediaRecorder.addEventListener('dataavailable', function (event) {
      if (event.data && event.data.size > 0) {
        chunks.push(event.data);
      }
    });

    mediaRecorder.addEventListener('stop', function () {
      stopTimer();
      stopStream();
      recording = false;

      const blobType = mediaRecorder.mimeType || mimeType || 'audio/webm';
      recordedBlob = new Blob(chunks, { type: blobType });
      clearPreviewUrl();
      recordedUrl = URL.createObjectURL(recordedBlob);
      previewAudio.src = recordedUrl;
      previewBox.hidden = false;
      rerecordBtn.hidden = false;
      uploadBtn.hidden = false;

      // 以實際音檔長度為準；讀不到時用計時秒數
      const fallbackSeconds = Math.max(1, Math.round((Date.now() - startedAt) / 1000));
      audioDuration = fallbackSeconds;
      durationText.textContent = '錄音長度：約 ' + audioDuration + ' 秒（讀取精確長度中…）';
      uploadBtn.disabled = true;

      const onMeta = function () {
        if (previewAudio.duration && isFinite(previewAudio.duration) && previewAudio.duration > 0) {
          audioDuration = Math.max(1, Math.round(previewAudio.duration));
        }
        durationText.textContent = '錄音長度：' + audioDuration + ' 秒';
        uploadBtn.disabled = audioDuration <= 0;
        previewAudio.removeEventListener('loadedmetadata', onMeta);
      };
      previewAudio.addEventListener('loadedmetadata', onMeta);
      // 部分瀏覽器 webm 暫時無 duration，給短延遲後仍允許上傳
      setTimeout(function () {
        if (uploadBtn.disabled && recordedBlob) {
          durationText.textContent = '錄音長度：約 ' + audioDuration + ' 秒';
          uploadBtn.disabled = false;
        }
      }, 800);

      recordBtn.textContent = '開始錄音';
      recordBtn.classList.remove('is-recording');
      recordBtn.disabled = false;
      recordTimer.classList.remove('is-recording');
      showMessage('請試聽確認，沒問題再按「確認上傳」', 'is-ok');
    });

    mediaRecorder.start();
    recording = true;
    startTimer();
    recordBtn.textContent = '停止錄音';
    recordBtn.classList.add('is-recording');
    recordTimer.classList.add('is-recording');
    previewBox.hidden = true;
    rerecordBtn.hidden = true;
    uploadBtn.hidden = true;
    uploadBtn.disabled = true;
    showMessage('錄音中…', '');
  }

  function stopStream() {
    if (mediaStream) {
      mediaStream.getTracks().forEach(function (track) {
        track.stop();
      });
      mediaStream = null;
    }
  }

  function stopRecording() {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
      return;
    }
    recordBtn.disabled = true;
    mediaRecorder.stop();
  }

  async function uploadRecording() {
    const songName = String(songInput.value || '').trim();
    if (songName === '') {
      showMessage('請輸入曲目名稱', 'is-error');
      songInput.focus();
      return;
    }
    if (!recordedBlob) {
      showMessage('請先完成錄音', 'is-error');
      return;
    }
    if (audioDuration <= 0) {
      showMessage('錄音時間太短，請重新錄製', 'is-error');
      return;
    }

    uploadBtn.disabled = true;
    rerecordBtn.disabled = true;
    recordBtn.disabled = true;
    showMessage('上傳中…', '');

    const mime = recordedBlob.type || 'audio/webm';
    const filename = 'practice.' + extensionForMime(mime);
    const form = new FormData();
    form.append('song_name', songName);
    form.append('audio_duration', String(audioDuration));
    form.append('audio', recordedBlob, filename);

    try {
      const response = await fetch(
        '/api/students/' + studentId + '/practice-uploads',
        {
          method: 'POST',
          credentials: 'same-origin',
          body: form
        }
      );
      const data = await response.json().catch(function () {
        return { message: '伺服器回應格式錯誤' };
      });

      if (!response.ok) {
        showMessage(data.message || '上傳失敗', 'is-error');
        return;
      }

      let msg = data.message || '練習上傳成功';
      const rewards = data.rewards || [];
      if (rewards.length > 0) {
        const parts = rewards.map(function (r) {
          return (
            r.quest_name +
            '（+' +
            r.reward_xp +
            ' XP、+' +
            r.reward_coin +
            ' 金幣）'
          );
        });
        msg += '；完成任務：' + parts.join('、');
      }
      showMessage(msg, 'is-ok');
      resetRecordingState();
    } catch (error) {
      showMessage('無法連接伺服器', 'is-error');
    } finally {
      uploadBtn.disabled = !recordedBlob;
      rerecordBtn.disabled = false;
      recordBtn.disabled = false;
    }
  }

  recordBtn.addEventListener('click', function () {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  });

  rerecordBtn.addEventListener('click', function () {
    resetRecordingState();
    showMessage('請重新錄音', '');
    startRecording();
  });

  uploadBtn.addEventListener('click', function () {
    uploadRecording();
  });

  async function init() {
    try {
      const user = await ensureStudent();
      if (!user) {
        return;
      }
      resetRecordingState();
      showMessage('輸入曲名後開始錄音，錄完可試聽再上傳', '');
    } catch (error) {
      showMessage('載入琴房失敗，請重新登入', 'is-error');
    }
  }

  init();
})();
