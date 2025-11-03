const body = document.body;

const btnTheme = document.querySelector(".fa-moon");
const btnHamburger = document.querySelector(".fa-bars");

const addThemeClass = (bodyClass, btnClass) => {
  body.classList.add(bodyClass);
  btnTheme.classList.add(btnClass);
};

const getBodyTheme = localStorage.getItem("portfolio-theme");
const getBtnTheme = localStorage.getItem("portfolio-btn-theme");

if (getBodyTheme) {
  addThemeClass(getBodyTheme, getBtnTheme);
} else {
  addThemeClass("light", "fa-moon");
}

const isDark = () => body.classList.contains("dark");

const setTheme = (bodyClass, btnClass) => {
  body.classList.remove(localStorage.getItem("portfolio-theme"));
  btnTheme.classList.remove(localStorage.getItem("portfolio-btn-theme"));

  addThemeClass(bodyClass, btnClass);

  localStorage.setItem("portfolio-theme", bodyClass);
  localStorage.setItem("portfolio-btn-theme", btnClass);
};

const toggleTheme = () =>
  isDark() ? setTheme("light", "fa-moon") : setTheme("dark", "fa-sun");

btnTheme.addEventListener("click", toggleTheme);

const displayList = () => {
  const navUl = document.querySelector(".nav__list");

  if (navUl.classList.contains("display-nav-list")) {
    navUl.classList.remove("display-nav-list");
    body.classList.remove("menu-open");
  } else {
    navUl.classList.add("display-nav-list");
    body.classList.add("menu-open");
  }
};

btnHamburger.addEventListener("click", displayList);

// Close menu when clicking on a nav item
const navLinks = document.querySelectorAll(".nav__list-item a");
navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    const navUl = document.querySelector(".nav__list");
    if (navUl.classList.contains("display-nav-list")) {
      navUl.classList.remove("display-nav-list");
      body.classList.remove("menu-open");
    }
  });
});

window.addEventListener("scroll", () => {
  const btnScrollTop = document.querySelector(".scroll-top");
  if (btnScrollTop) {
    if (window.scrollY > 500) {
      btnScrollTop.style.display = "block";
    } else {
      btnScrollTop.style.display = "none";
    }
  }
});

Promise.all([
  fetch("/assets/footer.html").then((response) => response.text()),
  fetch("/assets/scroll.html").then((response) => response.text()),
])
  .then(([footerData, scrollData]) => {
    document.querySelector(".footer").innerHTML = footerData;
    document.querySelector(".scroll-arrow").innerHTML = scrollData;

    const btnScrollTop = document.querySelector(".scroll-top-btn");
    if (btnScrollTop) {
      btnScrollTop.addEventListener("click", () =>
        window.scrollTo({ top: 0, behavior: "smooth" })
      );
    }
  })
  .catch((error) => console.error("Error loading footer or scroll:", error));
