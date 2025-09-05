const plusBtn = document.getElementById("plusBtn");
const plusMenu = document.getElementById("plusHidden");

const textarea = document.querySelector("textarea[name='prompt-textarea']");
const inputBox = document.querySelector(".input-wrapper")

// + 버튼 토글 열기
plusBtn.addEventListener("click", () => {
  plusMenu.classList.toggle("hidden");

  if (!plusMenu.classList.contains("hidden")) {
    const rect = plusBtn.getBoundingClientRect();
    plusMenu.style.position = "fixed";
    plusMenu.style.left = rect.left + "px";
    plusMenu.style.top = rect.top - plusMenu.offsetHeight - 20 + "px"; // 버튼 위에
  }
});


// Input 자동 늘림
textarea.addEventListener("input", function () {
  this.style.height = "auto";               // 높이를 초기화했다가
  this.style.height = this.scrollHeight + "px"; // 내용만큼 다시 늘려줌
});
