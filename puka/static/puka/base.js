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

// <c-ui.tabs> and <c-ui.tab-panel>.
Alpine.data("tabs", (initial = "") => ({
  active: initial,

  select(name) {
    this.active = name;
  },

  isActive(name) {
    return this.active === name;
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
