const tg = window.Telegram.WebApp;
tg.expand();

const API = "https://robloxhomework-production.up.railway.app";

const user = tg.initDataUnsafe.user;

const container = document.getElementById("tasks");

if (!user) {
    container.innerHTML = "❌ Открой через Telegram";
} else {
    const userId = user.id;

    loadTasks(userId);
}

function loadTasks(userId) {
    fetch(API + "/tasks/" + userId)
        .then(res => res.json())
        .then(tasks => {

            if (!tasks.length) {
                container.innerHTML = "😴 Нет заданий";
                return;
            }

            container.innerHTML = "";

            tasks.forEach(task => {
                const div = document.createElement("div");

                div.innerHTML = `
                    <div style="
                        background:#222;
                        padding:10px;
                        margin:10px;
                        border-radius:10px
                    ">
                        🧹 ${task[1]} <br>
                        💎 ${task[2]} <br>
                        📊 ${task[3]} <br>

                        ${task[3] === "pending" ? `
                            <button onclick="complete(${task[0]})">
                                ✅ Выполнить
                            </button>
                        ` : ""}

                        ${task[3] === "done" ? "🏆 Выполнено" : ""}
                    </div>
                `;

                container.appendChild(div);
            });
        });
}

function complete(taskId) {
    fetch(API + "/complete/" + taskId, { method: "POST" })
        .then(() => {
            alert("✅ Выполнено!");
            location.reload();
        });
}
