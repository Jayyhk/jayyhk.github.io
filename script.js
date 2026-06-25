const body = document.body;

// Apply saved theme immediately to avoid flash
const addThemeClass = (bodyClass, btnClass) => {
  body.classList.remove("light", "dark");
  body.classList.add(bodyClass);
  const btn = document.getElementById("btn-theme");
  if (btn) {
    btn.classList.remove("fa-moon", "fa-sun");
    btn.classList.add(btnClass);
  }
};

const getBodyTheme = localStorage.getItem("portfolio-theme");
const getBtnTheme = localStorage.getItem("portfolio-btn-theme");
addThemeClass(getBodyTheme || "dark", getBtnTheme || "fa-sun");

// Inject header
const headerEl = document.createElement("header");
headerEl.className = "header center";
document.body.prepend(headerEl);

fetch("/assets/header.html")
  .then((r) => r.text())
  .then((html) => {
    headerEl.innerHTML = html;

    const btnTheme = document.getElementById("btn-theme").closest("button");

    const isDark = () => body.classList.contains("dark");

    const setTheme = (bodyClass, btnClass) => {
      addThemeClass(bodyClass, btnClass);
      localStorage.setItem("portfolio-theme", bodyClass);
      localStorage.setItem("portfolio-btn-theme", btnClass);
    };

    setTheme(isDark() ? "dark" : "light", isDark() ? "fa-sun" : "fa-moon");

    btnTheme.addEventListener("click", () =>
      isDark() ? setTheme("light", "fa-moon") : setTheme("dark", "fa-sun"),
    );
  })
  .catch((error) => console.error("Error loading header:", error));

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

const footer = document.createElement("footer");
footer.className = "footer";
document.body.appendChild(footer);

const scrollArrow = document.createElement("div");
scrollArrow.className = "scroll-arrow";
document.body.appendChild(scrollArrow);

Promise.all([
  fetch("/assets/footer.html").then((response) => response.text()),
  fetch("/assets/scroll.html").then((response) => response.text()),
])
  .then(([footerData, scrollData]) => {
    footer.innerHTML = footerData;
    scrollArrow.innerHTML = scrollData;

    const btnScrollTop = document.querySelector(".scroll-top-btn");
    if (btnScrollTop) {
      btnScrollTop.addEventListener("click", () =>
        window.scrollTo({ top: 0, behavior: "smooth" }),
      );
    }
  })
  .catch((error) => console.error("Error loading footer or scroll:", error));

// Load KaTeX on pages that have math
if (document.querySelector('.post-content')) {
  const katexCSS = document.createElement('link');
  katexCSS.rel = 'stylesheet';
  katexCSS.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css';
  katexCSS.integrity = 'sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+';
  katexCSS.crossOrigin = 'anonymous';
  document.head.appendChild(katexCSS);

  const katexScript = document.createElement('script');
  katexScript.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js';
  katexScript.integrity = 'sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg';
  katexScript.crossOrigin = 'anonymous';
  katexScript.onload = function () {
    const autoRender = document.createElement('script');
    autoRender.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js';
    autoRender.integrity = 'sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk';
    autoRender.crossOrigin = 'anonymous';
    autoRender.onload = function () {
      renderMathInElement(document.body, {
        delimiters: [
          {left: '$$', right: '$$', display: true},
          {left: '\\[', right: '\\]', display: true},
          {left: '$', right: '$', display: false},
          {left: '\\(', right: '\\)', display: false},
        ],
        throwOnError: false,
      });
    };
    document.head.appendChild(autoRender);
  };
  document.head.appendChild(katexScript);
}

// Load blog dates and titles from posts and populate them
const blogLinks = document.querySelectorAll(
  '.blog__list-item a[href*="posts/"]',
);

blogLinks.forEach((link) => {
  const href = link.getAttribute("href");
  const slug = (href.match(/posts\/([^/]+)/) || [])[1];
  if (!slug) return;
  fetch(`/posts/${slug}/index.html`)
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
