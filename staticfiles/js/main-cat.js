document.addEventListener("DOMContentLoaded", function () {

    // Handle row click to pre-fill the form for editing
    document.querySelectorAll("table tbody tr").forEach((row) => {
        row.addEventListener("click", () => {
            document.getElementById("measurementId").value =
                row.cells[0].innerText;
            document.getElementById("inputName").value = row.cells[1].innerText;
        });
    });

    let windows = {}; // Object to keep track of opened windows

    // Function to open a new window or focus an existing one
    function openWindow(url, name, width = 1100, height = 700) {
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
    window.openWindow = openWindow;
});