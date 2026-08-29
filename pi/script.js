/* Pi 源码深度剖析 - 代码块极简着色（无依赖，离线可用） */
(function () {
  "use strict";

  var KEYWORDS = new Set((
    "import export from const let var function return if else for while new class extends implements " +
    "interface type enum async await try catch throw typeof instanceof in of as default void null " +
    "undefined true false this super static public private protected readonly get set yield delete " +
    "case switch break continue do finally declare abstract satisfies keyof infer namespace module"
  ).split(" "));

  var TOKEN = new RegExp(
    [
      "\\/\\*[\\s\\S]*?\\*\\/",          // block comment
      "//[^\\n]*",                        // line comment
      "`(?:\\\\[\\s\\S]|[^`\\\\])*`",     // template string
      "'(?:\\\\.|[^'\\\\\\n])*'",         // single-quote string
      '"(?:\\\\.|[^"\\\\\\n])*"',         // double-quote string
      "\\b\\d[\\w.]*",                    // number
      "[A-Za-z_$][\\w$]*"                 // identifier
    ].join("|"),
    "g"
  );

  function esc(s) {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function highlight(src) {
    var out = "";
    var last = 0;
    var m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(src)) !== null) {
      if (m.index > last) out += esc(src.slice(last, m.index));
      var tok = m[0];
      var cls = null;
      if (/^\/\*|^\/\//.test(tok)) cls = "tok-com";
      else if (/^['"`]/.test(tok)) cls = "tok-str";
      else if (/^\d/.test(tok)) cls = "tok-num";
      else if (KEYWORDS.has(tok)) cls = "tok-kw";
      else if (/^[A-Z]/.test(tok)) cls = "tok-type";
      else {
        // 函数调用：后随 "("
        var rest = src.slice(m.index + tok.length);
        if (/^\s*\(/.test(rest)) cls = "tok-fn";
      }
      out += cls ? '<span class="' + cls + '">' + esc(tok) + "</span>" : esc(tok);
      last = m.index + tok.length;
    }
    out += esc(src.slice(last));
    return out;
  }

  document.querySelectorAll(".codeblock pre code").forEach(function (el) {
    var src = el.textContent;
    el.innerHTML = highlight(src);
  });
})();
