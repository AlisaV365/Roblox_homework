const tg = window.Telegram.WebApp;
tg.expand();

const user = tg.initDataUnsafe.user;

if (!user) {
    document.body.innerHTML = "❌ Ошибка: нет пользователя";
} else {
    const userId = user.id;

    fetch("https://robloxhomework-production.up.railway.app/tasks/" + userId)
        .then(res => res.json())
        .then(data => {
            console.log(data);
        })
        .catch(err => {
            document.body.innerHTML = "❌ Ошибка загрузки";
            console.error(err);
        });
}
