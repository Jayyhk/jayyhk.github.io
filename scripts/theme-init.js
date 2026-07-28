// Applies the saved theme before the page paints, to avoid a flash of the
// wrong theme. Must be loaded as a blocking script at the top of <body>.
try {
  var t = localStorage.getItem("portfolio-theme");
  if (t === "light" || t === "dark") {
    document.body.classList.remove("light", "dark");
    document.body.classList.add(t);
  }
} catch (e) {}
