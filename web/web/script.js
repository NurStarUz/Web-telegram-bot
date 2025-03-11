document.addEventListener("DOMContentLoaded", function () {
    let tg = window.Telegram.WebApp;
    let questions = [];
    let currentIndex = 0;
    let correctAnswers = 0;

    fetch("https://your-backend-url.com/get_questions")
        .then(response => response.json())
        .then(data => {
            questions = data.questions;
            showQuestion();
        });

    function showQuestion() {
        if (currentIndex >= questions.length) {
            document.getElementById("quiz-container").style.display = "none";
            document.getElementById("result").style.display = "block";
            document.getElementById("score").innerText = `Siz ${correctAnswers} / ${questions.length} to‘g‘ri javob berdingiz.`;
            return;
        }

        let q = questions[currentIndex];
        document.getElementById("question").innerText = q.savol;
        let answersDiv = document.getElementById("answers");
        answersDiv.innerHTML = "";

        q.variantlar.forEach((answer, index) => {
            let btn = document.createElement("button");
            btn.innerText = answer;
            btn.onclick = function () {
                if (index === q.togri) {
                    btn.classList.add("correct");
                    correctAnswers++;
                } else {
                    btn.classList.add("wrong");
                }
                document.getElementById("next-button").style.display = "block";
            };
            answersDiv.appendChild(btn);
        });

        document.getElementById("next-button").onclick = function () {
            currentIndex++;
            document.getElementById("next-button").style.display = "none";
            showQuestion();
        };
    }

    document.getElementById("send-result").onclick = function () {
        let result = { user: tg.initDataUnsafe, score: correctAnswers };
        tg.sendData(JSON.stringify(result));
    };
});
