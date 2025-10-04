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

  if (btnHamburger.classList.contains("fa-bars")) {
    btnHamburger.classList.remove("fa-bars");
    btnHamburger.classList.add("fa-times");
    navUl.classList.add("display-nav-list");
  } else {
    btnHamburger.classList.remove("fa-times");
    btnHamburger.classList.add("fa-bars");
    navUl.classList.remove("display-nav-list");
  }
};

btnHamburger.addEventListener("click", displayList);

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
