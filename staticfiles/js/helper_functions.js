async function customFetch(url, options = {}) {
  // Fetch request as usual; cookies will be sent automatically by the browser
  let response = await fetch(url, options);

  if (response.status === 401) {
    // Token has expired; attempt to refresh
    const refreshResponse = await fetch('/api/get/tokken/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (refreshResponse.ok) {
      // Retry the original request with the refreshed token
      response = await fetch(url, options);
    } else {
      console.error("Error refreshing token.");
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
  fetch(`/api/user/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((result) => {
      console.log(result);
      console.log("Logged out successfully");

      // Redirect to login page
      window.location.href = "/login";
    })
    .catch((error) => {
      console.error("Error logging out:", error);
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