const API_BASE = '';

// Загрузка текущих данных профиля
async function loadProfileData() {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      credentials: 'include',
    });
    if (!res.ok) throw new Error('Не удалось загрузить профиль');
    const user = await res.json();

    // Заполняем форму
    document.getElementById('email').value = user.email || '';
    document.getElementById('first_name').value = user.first_name || '';
    document.getElementById('middle_name').value = user.middle_name || '';
    document.getElementById('last_name').value = user.last_name || '';
    document.getElementById('phone').value = user.phone || '';
    document.getElementById('city').value = user.city || '';
    document.getElementById('country').value = user.country || '';
  } catch (err) {
    console.error('Ошибка загрузки профиля:', err);
    alert('Не удалось загрузить данные профиля. Возможно, сессия истекла.');
    window.location.href = 'login.html';
  }
}

// Обновление профиля
document.getElementById('updateProfileForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const data = {};
  for (let [key, value] of formData.entries()) {
    if (value.trim() !== '') {
      data[key] = value.trim();
    }
  }

  if (Object.keys(data).length === 0) {
    alert('Нет данных для обновления');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/auth/update-user`, {
      method: 'PATCH',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (res.ok) {
      alert('Профиль успешно обновлён!');
      window.location.href = 'profile.html';
    } else {
      const err = await res.json().catch(() => ({}));
      alert('Ошибка: ' + (err.detail || 'Не удалось обновить профиль'));
    }
  } catch (err) {
    console.error('Ошибка сети:', err);
    alert('Не удалось подключиться к серверу');
  }
});

// Смена пароля
document.getElementById('changePasswordForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const prev = document.getElementById('prev_password').value;
  const newPass = document.getElementById('new_password').value;
  const confirm = document.getElementById('confirm_password').value;

  if (newPass !== confirm) {
    alert('Новые пароли не совпадают');
    return;
  }

  if (newPass.length < 6) {
    alert('Новый пароль должен быть не менее 6 символов');
    return;
  }

  const data = {
    prev_password: prev,
    new_password: newPass,
  };

  try {
    const res = await fetch(`${API_BASE}/auth/password`, {
      method: 'PATCH',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (res.ok) {
      alert('Пароль успешно изменён!');
      // Очищаем поля
      document.getElementById('changePasswordForm').reset();
    } else {
      const err = await res.json().catch(() => ({}));
      alert('Ошибка: ' + (err.detail || 'Не удалось изменить пароль'));
    }
  } catch (err) {
    console.error('Ошибка сети:', err);
    alert('Не удалось подключиться к серверу');
  }
});

// Удаление аккаунта
document.getElementById('deleteAccountBtn').addEventListener('click', async () => {
  if (!confirm('Вы уверены? Это действие нельзя отменить. Все данные будут удалены.')) {
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/auth/delete-user`, {
      method: 'DELETE',
      credentials: 'include',
    });

    if (res.status === 204) {
      alert('Аккаунт удалён.');
      // Выход и редирект на логин
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      window.location.href = 'login.html';
    } else {
      const err = await res.json().catch(() => ({}));
      alert('Ошибка: ' + (err.detail || 'Не удалось удалить аккаунт'));
    }
  } catch (err) {
    console.error('Ошибка сети:', err);
    alert('Не удалось подключиться к серверу');
  }
});

// Загрузка данных при старте
document.addEventListener('DOMContentLoaded', loadProfileData);
