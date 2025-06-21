document.addEventListener('DOMContentLoaded', function () {
    const feedbackId = '{{ feedback.id }}';

    function loadMessages() {
        $.get(`/fetch_messages/${feedbackId}/`, function (data) {
            let messageList = $("#message-list");
            messageList.empty();
            $("#loading-text").remove();

            $.each(data.messages, function (i, message) {
                let sender = message.sender_type === "client" ? "عميل" : "موظف";
                let senderClass = message.sender_type === "client" ? "client-message" : "employee-message";
                let alignmentClass = message.sender_type === "client" ? "justify-content-end" : "justify-content-start";

                messageList.append(`
                        <div class="message-row d-flex ${alignmentClass}">
                            <div class="chat-message ${senderClass}">
                                <strong>${sender}:</strong> ${message.message_text}
                                <div class="message-time">${message.sent_at}</div>
                            </div>
                        </div>
                    `);
            });

            messageList.scrollTop(messageList[0].scrollHeight);
        }).fail(function (xhr) {
            console.error("Error fetching messages:", xhr.responseText);
        });
    }

    loadMessages();
    setInterval(loadMessages, 3000);

    $("#message-form").submit(function (e) {
        e.preventDefault();
        let messageText = $("#message-text").val();

        $.ajax({
            url: `/add_message_to_feedback/${feedbackId}/`,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                message_text: messageText,
                sender_type: "employee"
            }),
            success: function (data) {
                $("#message-text").val("");
                loadMessages();
            },
            error: function (xhr) {
                alert("خطأ: " + xhr.responseJSON.error);
            }
        });
    });

    $("#close-feedback-btn").click(function () {
        $.ajax({
            url: `/close_feedback/${feedbackId}/`,
            type: "POST",
            success: function (response) {
                alert(response.message);
                window.close();
            },
            error: function (xhr) {
                alert("خطأ: " + xhr.responseJSON.error);
            }
        });
    });

    $("#delete-feedback-btn").click(function () {
        if (confirm("هل أنت متأكد أنك تريد حذف هذه الملاحظة؟")) {
            $.ajax({
                url: `/delete_feedback/${feedbackId}/`,
                type: "POST",
                success: function (response) {
                    alert(response.message);
                    window.close();
                },
                error: function (xhr) {
                    alert("خطأ: " + xhr.responseJSON.error);
                }
            });
        }
    });
});