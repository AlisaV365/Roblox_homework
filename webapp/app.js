const tg = window.Telegram.WebApp;
tg.expand();

const user = tg.initDataUnsafe.user;

if (!user) {
    document.body.innerHTML = "❌ Ошибка пользователя";
} else {
    const userId = user.id;

    fetch("https://robloxhomework-production.up.railway.app/tasks/" + userId)
        .then(res => res.json())
        .then(tasks => {
            const container = document.getElementById("tasks");

            if (tasks.length === 0) {
                container.innerHTML = "😴 Пока нет заданий";
                return;
            }

            tasks.forEach(task => {
                const div = document.createElement("div");
                div.innerHTML = `
                    <div style="
                        background:#222;
                        padding:10px;
                        margin:10px;
                        border-radius:10px;
                    ">
                        🧹 ${task[1]} <br>
                        💎 ${task[2]} монет
                    </div>
                `;
                container.appendChild(div);
            });
        })
        .catch(err => {
            document.body.innerHTML = "❌ Ошибка загрузки";
            console.error(err);
        });
}
