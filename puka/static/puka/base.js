import Alpine from "alpinejs";
import focus from "@alpinejs/focus";

window.htmx = require("htmx.org");

// <c-ui.search-box>: the input is x-ref="input" and carries the htmx attributes.
Alpine.data("searchBox", () => ({
  focus() {
    this.$refs.input.focus();
    this.$refs.input.select();
  },

  // Esc: clear, blur and re-run the search. Both events are sent so it works with
  // hx-trigger="input ..." and hx-trigger="change".
  reset() {
    this.clear();
    this.$refs.input.blur();
    this.$refs.input.dispatchEvent(new Event("input", { bubbles: true }));
    this.$refs.input.dispatchEvent(new Event("change", { bubbles: true }));
  },

  // Also handles the server's `clearSearch` event, so it mustn't trigger a request.
  clear() {
    this.$refs.input.value = "";
  },
}));

// <c-ui.pagination>: remember the chosen page size per table in localStorage.
Alpine.data("pageSize", (key, current, options) => ({
  // Restore the stored size by clicking its menu link, which htmx swaps in.
  restore() {
    // A page_size in the URL is an explicit choice (e.g. a shared link); keep it.
    if (new URL(location.href).searchParams.has("page_size")) return;
    const stored = localStorage.getItem(key);
    if (!stored) return;
    if (!options.split(",").includes(stored)) {
      localStorage.removeItem(key);
      return;
    }
    if (stored === current) return;
    const link = this.$root.querySelector(`[data-page-size="${stored}"]`);
    if (link) link.click();
  },

  remember(size) {
    localStorage.setItem(key, size);
  },
}));

// <c-layout.drawer>: close the (mobile) sidebar after navigating from it.
Alpine.data("drawer", () => ({
  close() {
    this.$root.querySelector(":scope > .drawer-toggle").checked = false;
  },

  closeOnLink(event) {
    if (event.target.closest("a[href]")) this.close();
  },
}));

window.Alpine = Alpine;
Alpine.plugin(focus);
Alpine.start();
