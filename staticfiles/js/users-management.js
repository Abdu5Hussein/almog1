document.addEventListener("DOMContentLoaded", function () {

    const table = new Tabulator("#users-table", {
        height: "auto",
        layout: "fitColumns",
        selectable: true,
        rowHeight: 20,
        movableColumns: true,
        columnHeaderVertAlign: "bottom",
        columnMenu: true, // Enable column menu
        data: [], // Load dynamically
        columns: [
            { title: "ر.م", field: "id", visible: true, width: 45 },
            { title: "اسم المستخدم", field: "username", visible: true, width: 95 },
            { title: "اسم الموظف", field: "first_name", visible: true, width: 95 },
            {
                title: "اخر دخول",
                field: "last_login",
                visible: true,
                width: 135,
                formatter: function (cell) {
                    const value = cell.getValue();
                    if (!value) return "-";
                    const date = new Date(value);
                    return date.toLocaleString(); // You can use options to customize format
                }
            },

            {
                title: "موظف",
                field: "is_superuser",
                visible: true,
                formatter: function (cell) {
                    return cell.getValue() ? "✗" : "✓";
                },
                width: 60,
            },
            {
                title: "نشط",
                field: "is_active",
                visible: true,
                formatter: function (cell) {
                    return cell.getValue() ? "✓" : "✗";
                },
                width: 60,
            },
            // {
            //     title: "الوظيفة",
            //     field: "profile", // point to the object itself
            //     formatter: function (cell) {
            //         const profile = cell.getValue();
            //         return profile ? profile.role : "";
            //     },
            //     visible: true
            // },

        ],
        placeholder: "لا توجد بيانات متاحة",
    });
    const client_table = new Tabulator("#clients-table", {
        height: "auto",
        layout: "fitColumns",
        selectable: true,
        rowHeight: 20,
        movableColumns: true,
        columnHeaderVertAlign: "bottom",
        columnMenu: true, // Enable column menu
        data: [], // Load dynamically
        columns: [
            { title: "ر.م", field: "id", visible: true, width: 45 },
            { title: "اسم المستخدم", field: "username", visible: true, width: 95 },
            { title: "اسم الموظف", field: "first_name", visible: true, width: 95 },
            {
                title: "اخر دخول",
                field: "last_login",
                visible: true,
                width: 135,
                formatter: function (cell) {
                    const value = cell.getValue();
                    if (!value) return "-";
                    const date = new Date(value);
                    return date.toLocaleString(); // You can use options to customize format
                }
            },

            {
                title: "موظف",
                field: "is_superuser",
                visible: true,
                formatter: function (cell) {
                    return cell.getValue() ? "✗" : "✓";
                },
                width: 60,
            },
            {
                title: "نشط",
                field: "is_active",
                visible: true,
                formatter: function (cell) {
                    return cell.getValue() ? "✓" : "✗";
                },
                width: 60,
            },
            //{ title: "الاسم", field: "first_name", visible: true },
            //{ title: "اللقب", field: "last_name", visible: true },

        ],
        placeholder: "لا توجد بيانات متاحة",
    });
    refreshTable();
    function refreshTable() {
        customFetch("/api/users/get", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Fetched Data:", data);

                // Set data in Tabulator
                table.setData(data.non_clients);
                client_table.setData(data.clients);
            })
            .catch((error) => console.error("Error fetching data:", error)).finally(() => {

            });
    }
    function updatePermissionCheckboxes(responseData) {
        const permissions = new Set(responseData);  // Convert to Set for fast lookup
        const checkboxes = document.querySelectorAll('#permissions-container input[type="checkbox"]');

        checkboxes.forEach((checkbox) => {
            checkbox.checked = permissions.has(checkbox.value);
        });
    }
    function getPermissions(id) {
        customFetch("/api/users/" + id + "/permissions", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                updatePermissionCheckboxes(data);
            })
            .catch((error) => console.error("Error fetching data:", error)).finally(() => {

            });
    }
    const checkboxes = document.querySelectorAll('#permissions-container input[type="checkbox"]');
    const all_permissions_check = document.getElementById("all_permissions_check");
    const client_permissions_check = document.getElementById("client_permissions_check");
    const employee_permissions_check = document.getElementById("employee_permissions_check");
    const is_active_toggle_check = document.getElementById("is_active_toggle_check");

    client_permissions_check.addEventListener("change", function () {
        const id = document.getElementById("user-no").value;
        if (!id) {
            alert("يرجى اختيار مستخدم أولاً.");
            this.checked = !this.checked; // Uncheck the checkbox
            return;
        }
        assignGroupToUser(id, "client");
    });
    employee_permissions_check.addEventListener("change", function () {
        const id = document.getElementById("user-no").value;
        if (!id) {
            alert("يرجى اختيار مستخدم أولاً.");
            this.checked = !this.checked; // Uncheck the checkbox
            return;
        }
        assignGroupToUser(id, "employee");
    });
    function assignGroupToUser(userId, groupName) {
        if (!userId || !groupName) {
            console.error("User ID and group name are required.");
            return;
        }
        customFetch("/api/users/assign-group", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_id: userId,
                group_name: groupName,
            })
        }).then(response => {
            if (!response.ok) {
                throw new Error('Request failed');
            }
            return response.json();
        })
            .then(data => {
                alert(data.message);
            })
            .catch(error => {
                console.error('Error:', error);
                // Optionally uncheck if request fails
                this.checked = !this.checked;
                alert("فشل في حفظ الصلاحية. حاول مجددا.");
            }).finally(() => {
                window.location.reload();
            });
    }

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            const permissionCodename = this.value;
            const action = this.checked ? "grant" : "remove";
            const id = document.getElementById("user-no").value;

            if (!id) {
                alert("يرجى اختيار مستخدم أولاً.");
                this.checked = !this.checked; // Uncheck the checkbox
                return;
            }

            fetch("/api/user/permissions/toggle", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    // Add Authorization if needed
                    // "Authorization": "Bearer YOUR_TOKEN"
                },
                body: JSON.stringify({
                    user_id: id,
                    permission_codename: permissionCodename,
                    action: action
                })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Request failed');
                    }
                    return response.json();
                })
                .then(data => {
                    alert('Success:' + data.arabic_message);
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Optionally uncheck if request fails
                    this.checked = !this.checked;
                    alert("فشل في حفظ الصلاحية. حاول مجددا.");
                });
        });
    });
    all_permissions_check.addEventListener("change", function () {
        const id = document.getElementById("user-no").value;

        if (!id) {
            alert("يرجى اختيار مستخدم أولاً.");
            this.checked = !this.checked; // Uncheck the checkbox
            return;
        }

        fetch("/api/user/permissions/give-all-permissions/toggle", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                id: id,
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Request failed');
                }
                return response.json();
            })
            .then(data => {
                alert('Success:' + data.message);
            })
            .catch(error => {
                console.error('Error:', error);
                // Optionally uncheck if request fails
                this.checked = !this.checked;
                alert("فشل في حفظ الصلاحية. حاول مجددا.");
            });
    });
    is_active_toggle_check.addEventListener("change", function () {
        const id = document.getElementById("user-no").value;

        if (!id) {
            alert("يرجى اختيار مستخدم أولاً.");
            this.checked = !this.checked; // Uncheck the checkbox
            return;
        }

        fetch("/api/user/activate/toggle", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                id: id,
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Request failed');
                }
                return response.json();
            })
            .then(data => {
                alert('Success:' + data.message);
            })
            .catch(error => {
                console.error('Error:', error);
                // Optionally uncheck if request fails
                this.checked = !this.checked;
                alert("فشل في حفظ الصلاحية. حاول مجددا.");
            });
    });

    async function updateUserStatusCheckboxes(userId) {
        const allPermissionsCheck = document.getElementById("all_permissions_check");
        const clientPermissionsCheck = document.getElementById("client_permissions_check");
        const employeePermissionsCheck = document.getElementById("employee_permissions_check");
        const isActiveToggleCheck = document.getElementById("is_active_toggle_check");

        if (!userId) {
            console.error("User ID is required.");
            return;
        }

        try {
            const response = await fetch(`/api/user/user-status-and-all-permissions/get?id=${userId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Error:", errorData.error || "Failed to fetch user status.");
                return;
            }

            const data = await response.json();

            // Set checkbox states
            isActiveToggleCheck.checked = !data.is_active;
            allPermissionsCheck.checked = data.all_permissions;
            clientPermissionsCheck.checked = data.groups.includes("client");
            employeePermissionsCheck.checked = data.groups.includes("employee");

        } catch (error) {
            console.error("Error fetching user status:", error);
        }
    }

    table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const id = parseInt(row.getData().id); // Get pno of the clicked row
        const username = row.getData().username;

        document.getElementById("user-no").value = id;
        document.getElementById("user-name").value = username;

        getPermissions(id);
        updateUserStatusCheckboxes(id);
        console.log("Clicked id:", id);
    });
    client_table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const id = parseInt(row.getData().id); // Get pno of the clicked row
        const username = row.getData().username;

        document.getElementById("user-no").value = id;
        document.getElementById("user-name").value = username;

        getPermissions(id);
        updateUserStatusCheckboxes(id);
        console.log("Clicked id:", id);
    });

    async function createUser(username, password) {
        if (!username || !password) {
            console.error("Username and password are required.");
            return;
        }

        try {
            const response = await fetch('/api/users/create-auth-user/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Include CSRF token if required by your Django setup
                    //'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                console.log("User created:", data);
                alert(`User '${username}' created successfully.`);
            } else {
                console.error("Error creating user:", data);
                alert(`Error: ${data.error}`);
            }

        } catch (error) {
            console.error("Network error:", error);
            alert("Network error while creating user.");
        }
    }
    document.getElementById("add_user_btn").addEventListener("click", function () {
        const username = document.getElementById("user-name").value;
        const password = document.getElementById("password").value;

        if (!username || !password) {
            alert("يرجى إدخال اسم المستخدم وكلمة المرور.");
            return;
        }

        const confirmPassword = prompt("يرجى إعادة إدخال كلمة المرور للتأكيد:");

        if (confirmPassword === null) {
            // User cancelled the prompt
            return;
        }

        if (password !== confirmPassword) {
            alert("كلمتا المرور غير متطابقتين.");
            return;
        }
        createUser(username, password);
    });
    document.getElementById("clear-btn").addEventListener("click", function () {
        clearForm();
    });
    function clearForm() {
        // Select all inputs except the CSRF token
        const inputs = document.querySelectorAll(
            "input:not([name='csrfmiddlewaretoken']), select"
        );
        inputs.forEach((input) => {
            if (input.type === "radio" || input.type === "checkbox") {
                input.checked = false; // Uncheck radios/checkboxes
            } else {
                input.value = ""; // Clear text, number, etc.
            }
        });

    }
    document.getElementById("employee").addEventListener("change", function () {
        const selectedOption = this.options[this.selectedIndex]; // get selected <option>
        const username = selectedOption.getAttribute("data-phone");

        if (!username) {
            alert("ليس للموظف رقم هاتف , يرجى إدخال رقم هاتف المستخدم من دليل الموظفين.");
            return;
        }
        document.getElementById("user-name").value = username;
    });
    function deleteUser(userId) {
        fetch(`/users/${userId}/delete/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),  // Function defined below
            },
            credentials: 'include'
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert(data.error || 'Failed to delete user.');
                }
            })
            .catch(error => console.error('Error deleting user:', error)).finally(() => {
                // Optionally refresh the table or clear the form
                refreshTable();
                clearForm();
            });
    }
    function changeUserPassword(userId, newPassword) {
        fetch(`/users/${userId}/change-password/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'include',
            body: JSON.stringify({ password: newPassword })
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert(data.error || 'Failed to change password.');
                }
            })
            .catch(error => console.error('Error changing password:', error)).finally(() => {
                // Optionally refresh the table or clear the form
                refreshTable();
                clearForm();
            });
    }
    document.getElementById('delete_user_btn').addEventListener('click', function () {
        const userId = document.getElementById('user-no').value;
        if (userId) {
            if (confirm("هل أنت متأكد من حذف هذا المستخدم؟")) {
                deleteUser(userId);
            }
        } else {
            alert('يرجى إدخال رقم المستخدم أولاً.');
        }
    });

    document.getElementById('change_password_btn').addEventListener('click', function () {
        const userId = document.getElementById('user-no').value;
        const newPassword = document.getElementById('password').value;

        if (!userId) {
            alert('يرجى إدخال رقم المستخدم أولاً.');
            return;
        }

        if (!newPassword) {
            alert('يرجى إدخال كلمة مرور جديدة.');
            return;
        }

        const confirmPassword = prompt("يرجى إعادة إدخال كلمة المرور للتأكيد:");

        if (confirmPassword === null) {
            // User cancelled the prompt
            return;
        }

        if (newPassword !== confirmPassword) {
            alert("كلمتا المرور غير متطابقتين.");
            return;
        }

        if (confirm("هل تريد تغيير كلمة المرور لهذا المستخدم؟")) {
            changeUserPassword(userId, newPassword);
        }
    });
});