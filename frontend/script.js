document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const hotelOwner = document.getElementById('hotel_owner').checked;

  // Собираем данные в объект
  const userData = {
    email: formData.get('email'),
    password: formData.get('password'),
    first_name: formData.get('first_name'),
    middle_name: formData.get('middle_name') || null,
    last_name: formData.get('last_name'),
    phone: formData.get('phone') || null,
    city: formData.get('city') || null,
    country: formData.get('country') || null,
    role: hotelOwner ? 'HOTEL_OWNER' : 'TRAVELER',
  };

  try {
    const response = await fetch('/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (response.ok) {
      const result = await response.json();
      console.log('Успешная регистрация:', result);
      // Перенаправляем на страницу профиля
      window.location.href = 'profile.html';
    } else {
      const error = await response.json();
      alert('Ошибка регистрации: ' + (error.detail || 'Неизвестная ошибка'));
    }
  } catch (err) {
    console.error('Ошибка сети:', err);
    alert('Не удалось подключиться к серверу. Проверьте, запущен ли бэкенд.');
  }
});
