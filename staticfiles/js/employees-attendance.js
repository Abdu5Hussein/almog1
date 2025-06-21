document.addEventListener('DOMContentLoaded', function () {
    function calculateTotalDelay() {
        let total = 0;
        const delayCells = document.querySelectorAll('.delay-cell');
        delayCells.forEach(cell => {
            const value = parseFloat(cell.textContent) || 0;
            total += value;
        });
        document.getElementById('total-delay').textContent = total;
    }

    // Run calculation when page loads
    //window.addEventListener('DOMContentLoaded', calculateTotalDelay);
    async function generateAttendanceTable(id) {
        const container = document.getElementById("attendance-table-container");
        container.innerHTML = ""; // Clear previous content

        const month = parseInt(document.getElementById("month").value);
        const year = parseInt(document.getElementById("year").value);
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        let daily_hours = "0"; // Default
        let foundFirst = false;

        // Map to store attendance records by day
        const attendanceMap = new Map();

        // Fetch attendance data
        try {
            const res = await fetch(`/api/attendance/employees/${id}/`, { method: "GET" });
            if (!res.ok) throw new Error("فشل في جلب البيانات");

            const data = await res.json();
            data.forEach(entry => {
                const entryDate = new Date(entry.date);
                const entryMonth = entryDate.getMonth();
                const entryYear = entryDate.getFullYear();

                if (entryMonth === month && entryYear === year) {
                    const day = entryDate.getDate();
                    attendanceMap.set(day, entry);

                    if (!foundFirst && entry.daily_hours) {
                        daily_hours = entry.daily_hours * daysInMonth;
                        foundFirst = true;
                    }
                }
            });
        } catch (err) {
            alert("حدث خطأ أثناء تحميل بيانات الحضور: " + err.message);
        }

        // Create table element
        const table = document.createElement("table");
        table.className = "table table-bordered table-striped table-hover mb-4";
        table.dir = "rtl";

        // Table header
        const thead = document.createElement("thead");
        const headRow = document.createElement("tr");
        headRow.innerHTML = `
      <th class="text-center bg-secondary text-white">التاريخ</th>
      <th class="text-center bg-secondary text-white">اليوم</th>
      <th class="text-center bg-secondary text-white">حضور</th>
      <th class="text-center bg-secondary text-white">انصراف</th>
      <th class="text-center bg-secondary text-white">غياب</th>
      <th class="text-center bg-secondary text-white">عدد ساعات التأخير</th>
      <th class="text-center bg-secondary text-white">معاملات</th>
    `;
        thead.appendChild(headRow);
        table.appendChild(thead);

        // Table body
        const tbody = document.createElement("tbody");

        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const weekday = date.toLocaleDateString("ar-EG", { weekday: "long" });

            const record = attendanceMap.get(day);
            const coming_time = record?.coming_time ?? "";
            const leaving_time = record?.leaving_time ?? "";
            const absent = record?.absent ?? false;
            const absent_hours = record?.absent_hours ?? "";
            const isDisabled = record ? "disabled" : "";

            const row = document.createElement("tr");
            row.innerHTML = `
        <td class="text-center">${day}-${month + 1}-${year}</td>
        <td class="text-center">${weekday}</td>
        <td class="text-center"><input type="time" class="form-control form-control-sm" name="start-${day}" id="start-${day}" value="${coming_time}" ${isDisabled}></td>
        <td class="text-center"><input type="time" class="form-control form-control-sm" name="end-${day}" id="end-${day}" value="${leaving_time}" ${isDisabled}></td>
        <td class="text-center"><input type="checkbox" class="form-check-input" name="absent-${day}" id="absent-${day}" ${absent ? "checked" : ""} ${isDisabled}></td>
        <td class="text-center" data-column='absent_hours'>${absent_hours}</td>
        <td class="text-center"><button class="btn btn-secondary mt-3 mt-md-0" id="save-${day}-${month + 1}" ${isDisabled}>حفظ</button></td>
      `;
            tbody.appendChild(row);
        }

        table.appendChild(tbody);
        container.appendChild(table);

        // Set daily working hours input
        document.getElementById("total-working-hours").value = daily_hours;

        // Setup post-render functionality
        calculateTotalAbsentHours();
        setupAttendanceSaveButtons(id);
        update_input_calc();
    }


    function setupAttendanceSaveButtons(id) {
        const tableRows = document.querySelectorAll("#attendance-table-container table tbody tr");

        tableRows.forEach((row) => {
            const dateText = row.children[0].textContent.trim(); // بصيغة dd-mm-yyyy
            const [day, month, year] = dateText.split("-");

            const dayNum = parseInt(day);
            const monthNum = parseInt(month);
            const yearNum = parseInt(year);

            const btn = row.querySelector(`button[id="save-${dayNum}-${monthNum}"]`);
            if (!btn) return;

            btn.addEventListener("click", function () {
                const coming_time = document.getElementById(`start-${dayNum}`).value || null;
                const leaving_time = document.getElementById(`end-${dayNum}`).value || null;
                const absent = document.getElementById(`absent-${dayNum}`).checked;
                const employee = id;
                //const absent_hours = absent ? "1.4" : "0";
                //const reason = "";
                //const note = "";

                const body = {
                    date: `${yearNum}-${monthNum.toString().padStart(2, "0")}-${dayNum.toString().padStart(2, "0")}`,
                    //absent_hours: absent_hours,
                    coming_time: coming_time,
                    leaving_time: leaving_time,
                    absent: absent,
                    //reason: reason,
                    //note: note,
                    employee: employee
                };
                console.log("attendance body: ", body);

                fetch("/api/attendance-api/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(body),
                })
                    .then((res) => {
                        if (!res.ok) throw new Error("فشل في الحفظ");
                        return res.json();
                    })
                    .then((data) => {
                        alert(`تم الحفظ ليوم ${body.date}`);

                        // Disable the row when the record is successfully saved
                        row.querySelectorAll("input, button").forEach((input) => {
                            input.disabled = true; // Disable the inputs
                        });

                        // Optionally change button text to indicate submission
                        btn.textContent = "تم الحفظ";
                        btn.classList.add("btn-success"); // Optional: Style the button as saved
                    })
                    .catch((err) => {
                        alert(`حدث خطأ: ${err.message}`);
                    });
            });
        });
    }
    document.getElementById("generate-btn").addEventListener("click", function () {
        const employeeId = parseInt(document.getElementById("employee").value); // معرف الموظف المحد
        if (employeeId == "" || !employeeId) {
            alert("الرجاء اختيار موظف");
            return
        }
        generateAttendanceTable(employeeId); // توليد الجدول
        //setupAttendanceSaveButtons(employeeId); // ربط أزرار الحفظ بالموظف (معرف الموظف 15)
    });
    function calculateTotalAbsentHours() {
        let totalAbsentHours = 0;
        const tableRows = document.querySelectorAll("#attendance-table-container table tbody tr");

        // Traverse each row and sum the absent hours using header ID
        tableRows.forEach((row) => {
            const absentHoursCell = row.querySelector("td[data-column='absent_hours']"); // Use the 'data-column' or other attribute
            const absentHours = parseFloat(absentHoursCell ? absentHoursCell.textContent.trim() : 0);

            if (!isNaN(absentHours)) {
                totalAbsentHours += absentHours; // Add to total if it's a valid number
            }
        });

        // Update the input field with the total absent hours
        document.getElementById("total-absent-hours").value = totalAbsentHours.toFixed(2); // Set value with two decimal points
    }

    function update_input_calc() {
        const total_working_hours = parseFloat(document.getElementById("total-working-hours").value) || 0;
        const total_absent_hours = parseFloat(document.getElementById("total-absent-hours").value) || 0;
        console.log("total_working_hours: ", document.getElementById("total-working-hours").value);
        console.log("total_absent_hours: ", document.getElementById("total-absent-hours").value);
        const total_net_hours = total_working_hours - total_absent_hours;
        document.getElementById("total-net-hours").value = total_net_hours.toFixed(2); // Set value with two decimal points

        const salary = parseFloat(document.getElementById("employee").selectedOptions[0].getAttribute("data-salary")) || 0;
        const after_absent_salary = parseFloat((total_net_hours / total_working_hours) * salary) || 0;
        const absent_worth = parseFloat(salary - after_absent_salary)
        const net_salary = salary - absent_worth;
        console.log("salary: ", salary);
        document.getElementById("total-salary").value = salary.toFixed(2); // Set value with two decimal points
        document.getElementById("absent-worth").value = absent_worth.toFixed(2);
        document.getElementById("net-salary").value = net_salary.toFixed(2);
    }
});