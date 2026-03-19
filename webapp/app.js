const tg = window.Telegram.WebApp;
tg.expand();

const container = document.getElementById("tasks");

const user = tg.initDataUnsafe?.user;

if (!user) {
    container.innerHTML = "❌ Открой через Telegram кнопку";
} else {
    const API = "https://robloxhomework-production.up.railway.app";
    const userId = user.id;

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
    <div style="background:#222;padding:10px;margin:10px;border-radius:10px;color:white">
        🧹 ${task[1]} <br>
        💎 ${task[2]} <br>
        📊 ${task[3]} <br>

        ${task[3] === "pending" ? <button onclick="complete(${task[0]})">✅ Выполнить</button> : ""}

        ${task[3] === "waiting" ? "⏳ Ждёт подтверждения" : ""}
        ${task[3] === "done" ? "🏆 Выполнено" : ""}
    </div>
`;

                container.appendChild(div);
            });
        })
        .catch(err => {
            container.innerHTML = "❌ Ошибка загрузки";
            console.error(err);
        });
}

function complete(taskId) {
    fetch(API + "/complete/" + taskId, { method: "POST" })
        .then(() => {
            alert("Отправлено родителю 👌");
            location.reload();
        });
}
