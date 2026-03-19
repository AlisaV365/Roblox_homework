const tg = window.Telegram.WebApp;
tg.expand();

const user = tg.initDataUnsafe.user;

const API = "https://robloxhomework-production.up.railway.app";

const userId = user.id;

fetch(API + "/tasks/" + userId)
    .then(res => res.json())
    .then(tasks => {
        const container = document.getElementById("tasks");

        tasks.forEach(task => {
            const div = document.createElement("div");

            div.innerHTML = `
                <div style="background:#222;padding:10px;margin:10px;border-radius:10px">
                    🧹 ${task[1]} <br>
                    💎 ${task[2]} <br>
                    📊 ${task[3]} <br>
                    <button onclick="complete(${task[0]})">✅ Выполнено</button>
                </div>
            `;

            container.appendChild(div);
        });
    });

function complete(taskId) {
    fetch(API + "/complete/" + taskId, {method: "POST"})
        .then(() => {
            alert("Отправлено на проверку 👌");
            location.reload();
        });
}
