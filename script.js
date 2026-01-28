const body = document.body;

const btnTheme = document.getElementById("btn-theme");
const btnHamburger = document.querySelector(".fa-bars");

const addThemeClass = (bodyClass, btnClass) => {
  body.classList.remove("light", "dark");
  body.classList.add(bodyClass);
  btnTheme.classList.remove("fa-moon", "fa-sun");
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
        window.scrollTo({ top: 0, behavior: "smooth" }),
      );
    }
  })
  .catch((error) => console.error("Error loading footer or scroll:", error));

// Load blog dates and titles from posts and populate them
const blogLinks = document.querySelectorAll(
  '.blog__list-item a[href^="posts/"]',
);

blogLinks.forEach((link) => {
  const href = link.getAttribute("href");
  const slug = href.split("/")[1]; // Extract slug from href like "posts/slug/"
  fetch(`posts/${slug}/index.html`)
    .then((response) => response.text())
    .then((html) => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");

      // Get title
      const h1 = doc.querySelector("h1.title");
      if (h1) {
        const title = h1.textContent.trim();
        const titleElement = link.querySelector(".link-text");
        if (titleElement) {
          titleElement.textContent = title;
        }
      }

      // Get date
      const h3 = doc.querySelector("h3.date");
      if (h3) {
        const date = h3.textContent.trim();
        const dateElement = link.querySelector(".blog-date");
        if (dateElement) {
          dateElement.textContent = date;
        }
      }
    })
    .catch((error) => console.error(`Error loading data for ${slug}:`, error));
});
