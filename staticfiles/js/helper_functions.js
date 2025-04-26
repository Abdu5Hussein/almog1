async function customFetch(url, options = {}) {
  let accessToken = localStorage.getItem('session_data@access_token') || "";
  options.headers = {
    ...(options.headers || {}),
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken.replace(/"/g, '')}`,
  };

  let response = await fetch(url, options);

  if (response.status === 401) {
    const refreshToken = localStorage.getItem('session_data@refresh_token') || "";

    if (!refreshToken) {
      alert("refresh token NA");
      logoutFunction();
      return;
    }
    const data = {
      refresh: refreshToken.replace(/"/g, '')
    }
    //alert("data :" + JSON.stringify(data));
    const refreshResponse = await fetch('/api/get/tokken/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (refreshResponse.ok) {
      //alert("refresh response ok");
      const data = await refreshResponse.json();
      accessToken = data.access;
      localStorage.setItem('session_data@access_token', accessToken);

      options.headers['Authorization'] = `Bearer ${accessToken.replace(/"/g, '')}`;
      response = await fetch(url, options);
    } else {
      const errorData = await refreshResponse.json();
      console.error("Error refreshing token:", errorData);
      alert("refresh response not ok, error: " + JSON.stringify(errorData) + "and refresh: " + refreshToken);
      logoutFunction();
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

function logoutFunction() {

  const access_token = localStorage.getItem("session_data@access_token").replace(/"/g, '');
  const refresh_token = localStorage.getItem("session_data@refresh_token").replace(/"/g, '');

  const data = {
    "refresh": refresh_token,
    "access": access_token,
  };

  console.log("access: " + access_token);
  console.log("refresh: " + refresh_token);

  fetch(`/api/user/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${access_token}`, // Correct string interpolation
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((result) => {
      console.log(result);
      console.log("تم تسجيل الخروج");

      // Clear both localStorage and sessionStorage after successful logout
      localStorage.clear();
      sessionStorage.clear();

      // Redirect to login page
      window.location.href = "/login";
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

let windows = {}; // Object to keep track of opened windows

// Function to open a new window or focus an existing one
function Helper_openWindow(url, name, width = 1100, height = 700) {
  // Check if the window is already open
  if (windows[name] && !windows[name].closed) {
    windows[name].focus(); // Bring the existing window to the front
  } else {
    // Get the screen width and height
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;

    // Calculate the position to center the window
    const left = (screenWidth - width) / 2;
    const top = (screenHeight - height) / 2;

    // Open the window with the specified or default dimensions, centered
    windows[name] = window.open(
      url,
      name,
      `width=${width},height=${height},left=${left},top=${top}`
    );
  }
}