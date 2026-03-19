const tg = window.Telegram.WebApp;
tg.expand();

const user = tg.initDataUnsafe.user;

const container = document.getElementById("tasks");

if (!user) {
    container.innerHTML = "❌ Нет user (открой через Telegram)";
} else {
    const userId = user.id;

    container.innerHTML = "⏳ Загружаем задания...";

    fetch("https://robloxhomework-production.up.railway.app/tasks/" + userId)
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
                    <div style="background:#222;color:white;padding:10px;margin:10px;border-radius:10px">
                        🧹 ${task[1]} <br>
                        💎 ${task[2]}
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
