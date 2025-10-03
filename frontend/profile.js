// Конфигурация
const API_BASE = '';

// DOM элементы
const welcomeMessage = document.getElementById('welcomeMessage');
const contentEl = document.getElementById('content');
const logoutBtn = document.getElementById('logoutBtn');

// Глобальные данные
let currentUser = null;
let currentMissionIdForReport = null;

// Функция выхода
async function logout() {
  try {
    await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    window.location.href = 'login.html';
  } catch (err) {
    console.error('Ошибка при выходе:', err);
    alert('Не удалось выйти из аккаунта');
  }
}

// Получение данных пользователя
async function fetchUserData() {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      credentials: 'include',
    });
    if (!res.ok) {
      if (res.status === 401) {
        alert('Сессия истекла. Пожалуйста, войдите снова.');
        window.location.href = 'login.html';
        return;
      }
      throw new Error('Не удалось загрузить профиль');
    }
    const user = await res.json();
    currentUser = user;
    renderProfile(user);
  } catch (err) {
    console.error('Ошибка загрузки профиля:', err);
    contentEl.innerHTML = `<p style="color: red;">Ошибка: ${err.message}</p>`;
  }
}

// Основная функция рендеринга
function renderProfile(user) {
  const { first_name, last_name, email, role } = user;
  welcomeMessage.textContent = `Привет, ${first_name} ${last_name}!`;

  let html = '';

  // Общая информация
  html += `
    <div class="section">
      <h2>Ваш профиль</h2>
      <p><strong>Email:</strong> ${email}</p>
      <p><strong>Роль:</strong> ${role}</p>
    </div>
  `;

  // Рендер в зависимости от роли
  if (role === 'TRAVELER') {
    html += renderTravelerContent(user);
  } else if (role === 'HOTEL_OWNER') {
    html += renderHotelOwnerContent(user);
  } else if (role === 'ADMIN') {
    html += renderAdminContent(user);
  }

  contentEl.innerHTML = html;

  // Навешиваем обработчики после рендеринга
  attachEventListeners();
}

// === TRAVELER ===
function renderTravelerContent(user) {
  console.log('Рендеринг профиля путешественника');
  
  // Проверим статус заявки
  let hasApprovedRequest = false;
  try {
    // Мы не можем здесь проверить статус без запроса, поэтому...
    // Вместо этого будем всегда показывать блок "Доступные миссии" для теста
    hasApprovedRequest = true; // ← ВРЕМЕННО для теста!
  } catch (e) {}

  let html = '';

  // Подача заявки
  html += `
    <div class="section" id="requestsSection">
      <h2>Заявка на участие</h2>
      <button class="btn" id="submitRequestBtn">Подать заявку</button>
      <button class="btn btn-outline" id="checkRequestBtn">Проверить статус</button>
      <div id="requestStatus"></div>
    </div>
  `;

  // ВСЕГДА показываем миссии для теста
  html += `
    <div class="section" id="missionsSection">
      <h2>Доступные миссии</h2>
      <button class="btn" id="loadAvailableMissions">Загрузить миссии</button>
      <div id="availableMissionsList"></div>
    </div>
  `;

  // Мои миссии
  html += `
    <div class="section">
      <h2>Мои миссии</h2>
      <button class="btn" id="loadMyMissions">Обновить список</button>
      <div id="myMissionsList"></div>
    </div>
  `;

  // Аналитика
  html += `
    <div class="section">
      <h2>Аналитика</h2>
      <button class="btn" id="loadAnalytics">Показать аналитику</button>
      <div id="analyticsData"></div>
    </div>
  `;

  return html;
}

// === HOTEL_OWNER ===
function renderHotelOwnerContent(user) {
  let html = '';

  // Управление отелями
  html += `
    <div class="section">
      <h2>Мои отели</h2>
      <button class="btn" id="addHotelBtn">Добавить отель</button>
      <button class="btn btn-outline" id="loadHotelsBtn">Мои отели</button>
      <div id="hotelsList"></div>
    </div>
  `;

  // Аналитика по отелям
  html += `
    <div class="section">
      <h2>Аналитика</h2>
      <button class="btn" id="loadHotelAnalytics">Загрузить аналитику</button>
      <div id="hotelAnalyticsData"></div>
    </div>
  `;

  return html;
}

// === ADMIN ===
function renderAdminContent(user) {
  let html = '';

  // Заявки
  html += `
    <div class="section">
      <h2>Заявки на участие</h2>
      <button class="btn" id="loadPendingRequests">Обновить</button>
      <div id="pendingRequestsList"></div>
    </div>
  `;

  // Аналитика
  html += `
    <div class="section">
      <h2>Аналитика</h2>
      <button class="btn" id="loadAdminAnalytics">Аналитика по пользователям</button>
      <button class="btn" id="loadHotelAdminAnalytics">Аналитика по отелям</button>
      <div id="adminAnalyticsData"></div>
    </div>
  `;

  // Критерии оценки
  html += `
    <div class="section">
      <h2>Критерии оценки</h2>
      <button class="btn" id="loadCriteria">Загрузить критерии</button>
      <div id="criteriaList"></div>
    </div>
  `;

  return html;
}

// Навешивание обработчиков событий
function attachEventListeners() {
  logoutBtn.addEventListener('click', logout);

  const user = currentUser;

  // === TRAVELER ===
  if (user.role === 'TRAVELER') {
    document.getElementById('submitRequestBtn')?.addEventListener('click', submitParticipationRequest);
    document.getElementById('checkRequestBtn')?.addEventListener('click', checkMyRequest);
    document.getElementById('loadAvailableMissions')?.addEventListener('click', loadAvailableMissions);
    document.getElementById('loadMyMissions')?.addEventListener('click', loadMyMissions);
    document.getElementById('loadAnalytics')?.addEventListener('click', loadTravelerAnalytics);
  }

  // === HOTEL_OWNER ===
  if (user.role === 'HOTEL_OWNER') {
    document.getElementById('addHotelBtn')?.addEventListener('click', () => alert('Форма добавления отеля — в разработке'));
    document.getElementById('loadHotelsBtn')?.addEventListener('click', loadHotels);
    document.getElementById('loadHotelAnalytics')?.addEventListener('click', loadHotelAnalytics);
  }

  // === ADMIN ===
  if (user.role === 'ADMIN') {
    document.getElementById('loadPendingRequests')?.addEventListener('click', loadPendingRequests);
    document.getElementById('loadAdminAnalytics')?.addEventListener('click', loadAdminUserAnalytics);
    document.getElementById('loadHotelAdminAnalytics')?.addEventListener('click', loadAdminHotelAnalytics);
    document.getElementById('loadCriteria')?.addEventListener('click', loadCriteria);
  }
}

// === API-функции для TRAVELER ===
async function submitParticipationRequest() {
  try {
    const res = await fetch(`${API_BASE}/requests/`, {
      method: 'POST',
      credentials: 'include',
    });
    if (res.ok) {
      alert('Заявка успешно подана!');
      checkMyRequest(); // ← сразу проверяем статус
    } else {
      const err = await res.json();
      alert('Ошибка: ' + (err.detail || 'Неизвестная ошибка'));
    }
  } catch (e) {
    alert('Ошибка сети');
  }
}

async function checkMyRequest() {
  try {
    const res = await fetch(`${API_BASE}/requests/me`, {
      credentials: 'include',
    });
    const data = await res.json();
    const statusMap = {
      'pending': 'Ожидает рассмотрения',
      'approved': 'Одобрена',
      'rejected': 'Отклонена'
    };
    document.getElementById('requestStatus').innerHTML = `
      <p><strong>Статус заявки:</strong> 
        <span class="status-badge status-${data.status}">${statusMap[data.status] || data.status}</span>
      </p>
      <p><small>Подана: ${new Date(data.submitted_at).toLocaleString()}</small></p>
    `;
    
    // Если заявка одобрена — перерендерим профиль, чтобы показать миссии
    if (data.status === 'approved') {
      renderProfile(currentUser);
    }
  } catch (e) {
    document.getElementById('requestStatus').innerHTML = '<p>Заявка не найдена</p>';
  }
}

async function loadAvailableMissions() {
  try {
    const res = await fetch(`${API_BASE}/mission/available-missions`, {
      credentials: 'include',
    });
    const hotels = await res.json();
    let html = '<h3>Доступные миссии:</h3>';
    
    if (hotels.length === 0) {
      html += '<p>Нет доступных миссий в вашем городе/стране.</p>';
    } else {
      hotels.forEach(h => {
        html += `
          <div class="mission-card">
            <h4>${h.hotel.name}</h4>
            <p><strong>Адрес:</strong> ${h.hotel.address}</p>
            <p><strong>Город:</strong> ${h.hotel.city}, ${h.hotel.country}</p>
            ${h.has_mission ? 
              `<p><span class="status-badge status-${h.mission_status || 'assigned'}">
                Миссия: ${h.mission_status || 'Назначена'}
              </span></p>` : 
              `<button class="btn" onclick="assignMission(${h.hotel.id})">
                Назначить миссию
              </button>`
            }
          </div>
        `;
      });
    }
    document.getElementById('availableMissionsList').innerHTML = html;
  } catch (e) {
    console.error('Ошибка загрузки миссий:', e);
    document.getElementById('availableMissionsList').innerHTML = 
      '<p class="error">Не удалось загрузить список миссий</p>';
  }
}

// Глобальная функция для назначения миссии (нужна для onclick)
window.assignMission = async function(hotelId) {
  if (!confirm('Назначить миссию для этого отеля?')) return;
  
  try {
    // Отправляем hotel_id как query-параметр
    const url = new URL('/mission/assign_mission', window.location.origin);
    url.searchParams.append('hotel_id', hotelId);

    const res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
    });
    
    if (res.ok) {
      alert('Миссия успешно назначена!');
      loadAvailableMissions();
      loadMyMissions();
    } else {
      const err = await res.json().catch(() => ({}));
      alert('Ошибка: ' + (err.detail || 'Не удалось назначить миссию'));
    }
  } catch (e) {
    console.error('Ошибка назначения миссии:', e);
    alert('Ошибка сети');
  }
};

async function loadMyMissions() {
  try {
    const res = await fetch(`${API_BASE}/mission/my-missions`, {
      credentials: 'include',
    });
    const missions = await res.json();
    let html = '';
    
    if (missions.length === 0) {
      html = '<p>У вас пока нет миссий.</p>';
    } else {
      missions.forEach(m => {
        const deadline = m.deadline ? new Date(m.deadline).toLocaleDateString() : '—';
        html += `
          <div class="mission-card">
            <h4>Миссия #${m.id} — ${m.hotel.name}</h4>
            <p><strong>Статус:</strong> 
              <span class="status-badge status-${m.status}">${formatStatus(m.status)}</span>
            </p>
            <p><strong>Дедлайн:</strong> ${deadline}</p>
            ${m.status === 'assigned' ? 
              `<button class="btn" onclick="startMission(${m.id})">
                Начать миссию
              </button>` : ''
            }
            ${m.status === 'in_progress' ? 
              `<button class="btn" onclick="openReportForm(${m.id})">
                Создать отчёт
              </button>` : ''
            }
          </div>
        `;
      });
    }
    document.getElementById('myMissionsList').innerHTML = html;
  } catch (e) {
    console.error('Ошибка загрузки миссий:', e);
    document.getElementById('myMissionsList').innerHTML = 
      '<p class="error">Не удалось загрузить миссии</p>';
  }
}

// Вспомогательная функция для отображения статуса
function formatStatus(status) {
  const statusMap = {
    'assigned': 'Назначена',
    'in_progress': 'В работе',
    'completed': 'Завершена',
    'report_pending': 'Завершена',
    'approved': 'Одобрена'
  };
  return statusMap[status] || status;
}

// Глобальные функции для миссий
window.startMission = async function(missionId) {
  if (!confirm('Начать выполнение миссии?')) return;
  
  try {
    // Отправляем mission_id как query-параметр
    const url = new URL('/mission/start-mission', window.location.origin);
    url.searchParams.append('mission_id', missionId);

    const res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
    });
    
    if (res.ok) {
      alert('Миссия начата!');
      loadMyMissions();
    } else {
      const err = await res.json().catch(() => ({}));
      alert('Ошибка: ' + (err.detail || 'Не удалось начать миссию'));
    }
  } catch (e) {
    console.error('Ошибка старта миссии:', e);
    alert('Ошибка сети');
  }
};

// Открытие формы отчёта
window.openReportForm = async function(missionId) {
  currentMissionIdForReport = missionId;

  // Загружаем критерии оценки
  let criteria = [];
  try {
    const res = await fetch(`${API_BASE}/analytics/criteria`, { credentials: 'include' });
    if (res.ok) {
      criteria = await res.json();
    }
  } catch (e) {
    console.warn('Не удалось загрузить критерии:', e);
  }

  // Формируем HTML формы
  let criteriaHtml = '';
  if (criteria.length > 0) {
    criteria.forEach((c, idx) => {
      criteriaHtml += `
        <div class="criteria-item">
          <h4>${c.name} ${c.is_required ? '(обязательно)' : ''}</h4>
          ${c.description ? `<p class="criteria-desc">${c.description}</p>` : ''}
          <label>Оценка (1–10):</label>
          <input type="number" min="1" max="10" name="score_${c.id}" required="${c.is_required}" class="score-input" />
          <label>Комментарий:</label>
          <textarea name="comment_${c.id}" placeholder="Опционально"></textarea>
        </div>
      `;
    });
  } else {
    criteriaHtml = '<p>Нет критериев оценки. Обратитесь к администратору.</p>';
  }

  const modalHtml = `
    <div id="reportModal" class="modal">
      <div class="modal-content">
        <span class="close">&times;</span>
        <h2>Отправить отчёт по миссии #${missionId}</h2>
        
        <form id="reportForm">
          <div class="form-group">
            <label for="overallComment">Общий комментарий (опционально):</label>
            <textarea id="overallComment" name="overall_comment" rows="3"></textarea>
          </div>

          <div class="form-group">
            <h3>Оценки по критериям</h3>
            ${criteriaHtml}
          </div>

          <div class="form-group">
            <label for="reportPhotos">Фотографии (опционально):</label>
            <input type="file" id="reportPhotos" name="photos" multiple accept="image/*" />
            <small>Можно выбрать несколько файлов</small>
          </div>

          <button type="submit" class="btn">Отправить отчёт</button>
        </form>
      </div>
    </div>
  `;

  // Добавляем модалку в DOM
  document.body.insertAdjacentHTML('beforeend', modalHtml);

  // Навешиваем обработчики
  document.querySelector('#reportModal .close').onclick = () => {
    document.getElementById('reportModal').remove();
  };

  document.getElementById('reportForm').onsubmit = handleReportSubmit;
};

// Обработка отправки формы отчёта
async function handleReportSubmit(e) {
  e.preventDefault();

  const formData = new FormData();
  formData.append('mission_id', currentMissionIdForReport);

  // Общий комментарий
  const overallComment = document.getElementById('overallComment').value;
  if (overallComment) {
    formData.append('overall_comment', overallComment);
  }

  // Собираем оценки
  const scores = [];
  const scoreInputs = document.querySelectorAll('.score-input');
  let hasRequiredMissing = false;

  scoreInputs.forEach(input => {
    const criterionId = input.name.split('_')[1];
    const score = input.value.trim();
    const comment = document.querySelector(`[name="comment_${criterionId}"]`)?.value || '';

    const isRequired = input.hasAttribute('required');

    if (isRequired && (!score || score < 1 || score > 10)) {
      hasRequiredMissing = true;
    }

    if (score && score >= 1 && score <= 10) {
      scores.push({
        criterion_id: parseInt(criterionId),
        score: parseInt(score),
        comment: comment || null
      });
    }
  });

  if (hasRequiredMissing) {
    alert('Пожалуйста, заполните все обязательные оценки (1–10).');
    return;
  }

  if (scores.length === 0) {
    alert('Добавьте хотя бы одну оценку.');
    return;
  }

  formData.append('scores_json', JSON.stringify(scores));

  // Фото
  const photoInput = document.getElementById('reportPhotos');
  if (photoInput.files.length > 0) {
    for (let file of photoInput.files) {
      formData.append('photos', file);
    }
  }

  // Отправка
  try {
    const response = await fetch(`${API_BASE}/reports/submit`, {
      method: 'POST',
      credentials: 'include',
      body: formData, // не указываем Content-Type — браузер сам установит boundary
    });

    if (response.ok) {
      const result = await response.json();
      alert(`Отчёт отправлен! ID: ${result.report_id}`);
      document.getElementById('reportModal').remove();
      loadMyMissions(); // обновляем список миссий
    } else {
    const error = await response.json().catch(() => ({}));
    let message = error.detail || 'Не удалось отправить отчёт';
    
    // Специальная обработка дубликата
    if (response.status === 500 && message.includes('duplicate key')) {
        message = 'Отчёт для этой миссии уже отправлен!';
    }
  
  alert('Ошибка: ' + message);
}
  } catch (err) {
    console.error('Ошибка отправки отчёта:', err);
    alert('Ошибка сети. Проверьте подключение.');
  }
}

async function loadTravelerAnalytics() {
  try {
    const res = await fetch('/analytics/traveler', { credentials: 'include' });
    const data = await res.json();

    let html = `
      <div class="analytics-card">
        <h3>Ваша аналитика</h3>
        <p><strong>Всего миссий:</strong> ${data.total_missions}</p>
        <p><strong>Завершено:</strong> ${data.completed_missions}</p>
        <p><strong>Средний балл:</strong> ${data.average_score !== null ? `${data.average_score} / 10` : '—'}</p>
    `;

    if (data.badges && data.badges.length > 0) {
      html += `<p><strong>Награды:</strong> ${data.badges.join(', ')}</p>`;
    }

    html += `</div>`;
    document.getElementById('analyticsData').innerHTML = html;
  } catch (e) {
    console.error('Ошибка загрузки вашей аналитики:', e);
    document.getElementById('analyticsData').innerHTML = '<p class="error">Ошибка загрузки</p>';
  }
}

// === HOTEL_OWNER ===
async function loadHotels() {
  try {
    const res = await fetch(`${API_BASE}/hotel/all-hotels`, {
      credentials: 'include',
    });
    const hotels = await res.json();
    let html = '';
    hotels.forEach(h => {
      html += `
        <div class="hotel-card">
          <h4>${h.name}</h4>
          <p>${h.address}, ${h.city}, ${h.country}</p>
          <button class="btn btn-outline">Редактировать</button>
          <button class="btn" style="background:#ef4444;" onclick="deleteHotel(${h.id})">Удалить</button>
        </div>
      `;
    });
    document.getElementById('hotelsList').innerHTML = html || '<p>Отелей нет</p>';
  } catch (e) {
    document.getElementById('hotelsList').innerHTML = '<p>Ошибка загрузки</p>';
  }
}

window.deleteHotel = async function(hotelId) {
  if (!confirm('Удалить отель?')) return;
  try {
    const res = await fetch(`${API_BASE}/hotel/delete-hotel?id=${hotelId}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    if (res.status === 204) {
      alert('Отель удалён');
      loadHotels();
    }
  } catch (e) {
    alert('Ошибка');
  }
};

async function loadHotelAnalytics() {
  try {
    // Сначала получим список отелей, чтобы выбрать первый (или добавить выбор)
    const hotelsRes = await fetch('/hotel/all-hotels', { credentials: 'include' });
    const hotels = await hotelsRes.json();
    
    if (hotels.length === 0) {
      document.getElementById('hotelAnalyticsData').innerHTML = '<p>У вас нет отелей</p>';
      return;
    }

    // Берём первый отель (в реальности можно добавить выпадающий список)
    const hotelId = hotels[0].id;
    const res = await fetch(`/analytics/hotels/${hotelId}`, { credentials: 'include' });
    const data = await res.json();

    let html = `
      <div class="analytics-card">
        <h3>Аналитика отеля: <strong>${data.hotel_name}</strong></h3>
        <p><strong>Всего инспекций:</strong> ${data.total_inspections}</p>
        <p><strong>Последняя инспекция:</strong> ${new Date(data.last_inspection_date).toLocaleDateString()}</p>
    `;

    if (data.criteria_stats && data.criteria_stats.length > 0) {
      html += `
        <h4>Статистика по критериям:</h4>
        <div class="criteria-stats">
      `;
      data.criteria_stats.forEach(stat => {
        html += `
          <div class="stat-item">
            <h5>${stat.criterion}</h5>
            <p>${stat.description}</p>
            <p><strong>Средняя оценка:</strong> ${stat.average_score} / 10</p>
            <p><strong>Отзывов:</strong> ${stat.total_reviews}</p>
          </div>
        `;
      });
      html += `</div>`;
    } else {
      html += `<p>Нет данных по критериям</p>`;
    }

    html += `</div>`;
    document.getElementById('hotelAnalyticsData').innerHTML = html;
  } catch (e) {
    console.error('Ошибка загрузки аналитики отеля:', e);
    document.getElementById('hotelAnalyticsData').innerHTML = '<p class="error">Ошибка загрузки аналитики</p>';
  }
}

// === ADMIN ===
async function loadPendingRequests() {
  try {
    const res = await fetch(`${API_BASE}/requests/pending`, {
      credentials: 'include',
    });
    const requests = await res.json();
    let html = '';
    requests.forEach(r => {
      html += `
        <div class="request-card">
          <p><strong>Заявка #${r.id}</strong> от ${new Date(r.submitted_at).toLocaleString()}</p>
          <span class="status-badge status-${r.status}">${r.status}</span>
          <br><br>
          <button class="btn" onclick="approveRequest(${r.id})">Одобрить</button>
          <button class="btn" style="background:#ef4444;" onclick="rejectRequest(${r.id})">Отклонить</button>
        </div>
      `;
    });
    document.getElementById('pendingRequestsList').innerHTML = html || '<p>Нет заявок</p>';
  } catch (e) {
    document.getElementById('pendingRequestsList').innerHTML = '<p>Ошибка загрузки</p>';
  }
}

window.approveRequest = async function(requestId) {
  try {
    const res = await fetch(`${API_BASE}/requests/approve`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ request_id: requestId, action: 'approve' }),
    });
    if (res.ok) {
      alert('Заявка одобрена');
      loadPendingRequests();
    }
  } catch (e) {
    alert('Ошибка');
  }
};

window.rejectRequest = async function(requestId) {
  try {
    const res = await fetch(`${API_BASE}/requests/reject`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ request_id: requestId, action: 'reject' }),
    });
    if (res.ok) {
      alert('Заявка отклонена');
      loadPendingRequests();
    }
  } catch (e) {
    alert('Ошибка');
  }
};

async function loadAdminHotelAnalytics() {
  try {
    const res = await fetch('/analytics/admin/hotels', { credentials: 'include' });
    const data = await res.json();

    if (!data || data.length === 0) {
      document.getElementById('adminAnalyticsData').innerHTML = '<p>Нет данных по отелям</p>';
      return;
    }

    let html = `
      <h3>Аналитика по отелям</h3>
      <div class="analytics-table">
        <div class="table-header">
          <div>Отель</div>
          <div>Город</div>
          <div>Миссий</div>
          <div>Средний балл</div>
        </div>
    `;

    data.forEach(hotel => {
      const avg = hotel.average_score !== null ? `${hotel.average_score} / 10` : '—';
      html += `
        <div class="table-row">
          <div>${hotel.hotel}</div>
          <div>${hotel.city}</div>
          <div>${hotel.total_missions}</div>
          <div>${avg}</div>
        </div>
      `;
    });

    html += `</div>`;
    document.getElementById('adminAnalyticsData').innerHTML = html;
  } catch (e) {
    console.error('Ошибка загрузки аналитики отелей:', e);
    document.getElementById('adminAnalyticsData').innerHTML = '<p class="error">Ошибка загрузки</p>';
  }
}

async function loadAdminUserAnalytics() {
  try {
    const res = await fetch('/analytics/admin/users', { credentials: 'include' });
    const data = await res.json();

    if (!data || data.length === 0) {
      document.getElementById('adminAnalyticsData').innerHTML = '<p>Нет данных по пользователям</p>';
      return;
    }

    let html = `
      <h3>Аналитика по пользователям</h3>
      <div class="analytics-table">
        <div class="table-header">
          <div>Email</div>
          <div>Роль</div>
          <div>Миссий завершено</div>
          <div>Качество отчётов</div>
        </div>
    `;

    data.forEach(user => {
      const quality = user.avg_report_quality !== null ? `${user.avg_report_quality} / 10` : '—';
      html += `
        <div class="table-row">
          <div>${user.email}</div>
          <div>${user.role}</div>
          <div>${user.missions_completed}</div>
          <div>${quality}</div>
        </div>
      `;
    });

    html += `</div>`;
    document.getElementById('adminAnalyticsData').innerHTML = html;
  } catch (e) {
    console.error('Ошибка загрузки аналитики пользователей:', e);
    document.getElementById('adminAnalyticsData').innerHTML = '<p class="error">Ошибка загрузки</p>';
  }
}

async function loadCriteria() {
  try {
    const res = await fetch(`${API_BASE}/analytics/criteria`, {
      credentials: 'include',
    });
    const criteria = await res.json();
    let html = '<ul>';
    criteria.forEach(c => {
      html += `<li><strong>${c.name}</strong> — ${c.description || ''} ${c.is_required ? '(обязательный)' : ''}</li>`;
    });
    html += '</ul>';
    document.getElementById('criteriaList').innerHTML = html;
  } catch (e) {
    document.getElementById('criteriaList').innerHTML = '<p>Ошибка загрузки</p>';
    console.log(e)
  }
}

// Запуск при загрузке
document.addEventListener('DOMContentLoaded', fetchUserData);
