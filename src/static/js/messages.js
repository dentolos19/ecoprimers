function open_chat() {
    console.log("function accessed")
}


document.addEventListener("DOMContentLoaded", function () {
    const usersDiv = document.querySelector("#users");
    if (usersDiv) {
        usersDiv.addEventListener("click", open_chat);
    }
});