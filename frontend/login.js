document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;

  if (!email || !password) {
    alert('Пожалуйста, заполните все обязательные поля.');
    return;
  }

  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      credentials: 'include', // важно для отправки cookies!
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
      // Бэкенд установит cookie автоматически
      console.log('Успешный вход');
      window.location.href = 'profile.html';
    } else {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || 'Ошибка при входе';
      alert('Ошибка: ' + message);
    }
  } catch (err) {
    console.error('Ошибка сети:', err);
    alert('Не удалось подключиться к серверу. Убедитесь, что бэкенд запущен.');
  }
});
