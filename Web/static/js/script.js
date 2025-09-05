const plusBtn = document.getElementById("plusBtn");
const plusMenu = document.getElementById("plusHidden");

// + 버튼 토글 열기
plusBtn.addEventListener("click", () => {
    plusMenu.classList.toggle("hidden");
});

