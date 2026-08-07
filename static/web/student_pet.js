(function () {
  const bgEl = document.getElementById('pet-bg');
  const spriteEl = document.getElementById('pet-sprite');

  function applyStageVisual(stageOrder) {
    const order = Number(stageOrder) || 1;
    const clamped = Math.min(Math.max(order, 1), 4);

    if (clamped === 1) {
      bgEl.src = '/assets/material/pet_stage1.png';
      spriteEl.classList.remove('pet-sprite--stage2to4');
      spriteEl.classList.add('pet-sprite--stage1');
    } else {
      bgEl.src = '/assets/material/pet_stage2-4.png';
      spriteEl.classList.remove('pet-sprite--stage1');
      spriteEl.classList.add('pet-sprite--stage2to4');
    }

    spriteEl.src = '/assets/material/pet/pet_id_no' + clamped + '.png';
    spriteEl.alt = '寵物階段 ' + clamped;
  }

  async function ensureStudent() {
    const response = await fetch('/api/me', { credentials: 'same-origin' });
    if (response.status === 401) {
      window.location.href = '/student/login';
      return null;
    }
    const data = await response.json();
    if (!data || data.role !== 'student' || !data.user) {
      window.location.href = '/student/login';
      return null;
    }
    return data.user;
  }

  async function loadPet(studentId) {
    const response = await fetch('/api/students/' + studentId + '/pet', {
      credentials: 'same-origin'
    });
    const data = await response.json().catch(function () {
      return {};
    });

    if (!response.ok) {
      return;
    }

    applyStageVisual((data.data || {}).stage_order);
  }

  async function init() {
    try {
      const user = await ensureStudent();
      if (!user) {
        return;
      }
      await loadPet(user.student_id);
    } catch (error) {
      window.location.href = '/student/login';
    }
  }

  init();
})();
