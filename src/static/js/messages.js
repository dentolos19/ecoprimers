function open_chat(event) {
    const clickedUser = event.target.closest('.user');
    
    if (clickedUser) {
        const allUserDivs = document.querySelectorAll('.user');
        allUserDivs.forEach(div => div.classList.remove('active'));
        
        clickedUser.classList.add('active');
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const usersDiv = document.querySelector("#users");
    if (usersDiv) {
        usersDiv.addEventListener("click", open_chat);  
    }
});

