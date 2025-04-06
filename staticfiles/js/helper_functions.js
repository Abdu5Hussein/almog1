async function customFetch(url, options = {}) {
  let accessToken = localStorage.getItem('session_data@access_token');
  options.headers = {
    ...(options.headers || {}),
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,
  };

  let response = await fetch(url, options);

  if (response.status === 401) {
    const refreshToken = localStorage.getItem('session_data@refresh_token');

    if (!refreshToken) {
      window.location.href = '/login';
      return;
    }

    const refreshResponse = await fetch('api/get/tokken/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      accessToken = data.access;
      localStorage.setItem('session_data@access_token', accessToken);

      options.headers['Authorization'] = `Bearer ${accessToken}`;
      response = await fetch(url, options);
    } else {
      localStorage.removeItem('session_data@access_token');
      localStorage.removeItem('session_data@refresh_token');
      window.location.href = '/login';
      return;
    }
  }

  return response;
}

function getCSRFToken() {
  return document.querySelector("[name=csrfmiddlewaretoken]").value;
}

const getValueById = (id) => {
  const element = document.getElementById(id);
  return element ? element.value.trim() : "";
};

const getSelectedTextById = (id) => {
  const element = document.getElementById(id);
  return element && element.selectedIndex !== 0
    ? element.options[element.selectedIndex].text
    : "";
};

const getChoicesTextById = (id) => {
  const element = document.getElementById(id);
  return element ? element.getValue(true).join("; ") : "";
};