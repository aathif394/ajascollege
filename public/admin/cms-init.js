/**
 * AJAS branding + preview styles for Sveltia CMS.
 * Runs after sveltia-cms.js exposes window.CMS / starts the app.
 */
(function () {
  var COLLEGE = "Al Jamia Arts & Science College";
  var TITLE = COLLEGE + " · CMS";

  function forceTitle() {
    if (document.title !== TITLE && document.title.indexOf("Sveltia") !== -1) {
      document.title = TITLE;
    } else if (!document.title || document.title === "Sveltia CMS") {
      document.title = TITLE;
    }
  }

  // Sveltia overwrites <title> after boot — keep reclaiming it
  forceTitle();
  var titleEl = document.querySelector("title");
  if (titleEl && window.MutationObserver) {
    new MutationObserver(forceTitle).observe(titleEl, {
      childList: true,
      characterData: true,
      subtree: true,
    });
  }
  setInterval(forceTitle, 1500);

  function whenCMS(cb) {
    if (window.CMS && typeof window.CMS.registerPreviewStyle === "function") {
      cb(window.CMS);
      return;
    }
    var n = 0;
    var id = setInterval(function () {
      n += 1;
      if (window.CMS && typeof window.CMS.registerPreviewStyle === "function") {
        clearInterval(id);
        cb(window.CMS);
      } else if (n > 100) {
        clearInterval(id);
      }
    }, 100);
  }

  whenCMS(function (CMS) {
    // Option C: site-like preview pane styles
    try {
      CMS.registerPreviewStyle("/admin/preview.css");
    } catch (e) {
      console.warn("[AJAS CMS] registerPreviewStyle failed", e);
    }

    // Optional: register simple field-based preview helpers if API exists
    try {
      if (typeof CMS.registerPreviewTemplate === "function") {
        // Lightweight template: wrap entry fields in branded shell
        // Signature compatible with Decap-style (name, component)
        // Sveltia may expect a different shape; guard errors.
        var collections = ["pages", "news", "events", "faculty", "programmes"];
        collections.forEach(function (name) {
          // Only if React-style createClass exists (Decap compat); otherwise skip
          if (typeof window.createClass === "function" && window.h) {
            CMS.registerPreviewTemplate(
              name,
              window.createClass({
                render: function () {
                  var entry = this.props.entry;
                  var title = entry.getIn(["data", "title"]) || "";
                  var body = this.props.widgetFor("body");
                  return window.h(
                    "div",
                    { className: "ajas-preview-shell" },
                    window.h("div", { className: "ajas-preview-kicker" }, COLLEGE),
                    window.h("h1", null, title),
                    body
                  );
                },
              })
            );
          }
        });
      }
    } catch (e) {
      // Preview templates optional — styles alone still improve the pane
      console.info("[AJAS CMS] preview templates skipped", e && e.message);
    }
  });
})();
