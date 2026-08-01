// MathJax-Konfiguration für "The Computational Minimum"
// Wird von mkdocs.yml (extra_javascript) referenziert.
// Zusammen mit pymdownx.arithmatex (generic: true) rendert das
// $...$ und $$...$$-Formeln in der Site.

window.MathJax = {
  tex: {
    inlineMath: [["$", "$"], ["\\(", "\\)"]],
    displayMath: [["$$", "$$"], ["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};

document$.subscribe(() => {
  MathJax.startup.output.clearCache();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
});