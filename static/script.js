// ===============================
// Navbar Shadow on Scroll
// ===============================

window.addEventListener("scroll", function () {

    const navbar = document.querySelector(".navbar");

    if (window.scrollY > 20) {
        navbar.classList.add("shadow");
    } else {
        navbar.classList.remove("shadow");
    }

});

// ===============================
// Smooth Scroll
// ===============================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        document.querySelector(this.getAttribute("href"))
            .scrollIntoView({
                behavior: "smooth"
            });

    });

});

// ===============================
// Fade In Animation
// ===============================

window.addEventListener("load", function () {

    document.body.style.opacity = "1";

});
// ===========================
// Loading Animation
// ===========================

document.addEventListener("DOMContentLoaded", function(){

    const forms = document.querySelectorAll("form");

    forms.forEach(function(form){

        form.addEventListener("submit", function(){

            const loader = document.getElementById("loadingScreen");

            if(loader){

                loader.style.display = "flex";

            }

        });

    });

});

// Dark Mode

const toggleBtn = document.getElementById("themeToggle");

if (localStorage.getItem("theme") === "dark") {

    document.body.classList.add("dark-mode");

}

if (toggleBtn) {

    toggleBtn.addEventListener("click", function () {

        document.body.classList.toggle("dark-mode");

        if (document.body.classList.contains("dark-mode")) {

            localStorage.setItem("theme", "dark");

        } else {

            localStorage.setItem("theme", "light");

        }

    });

}