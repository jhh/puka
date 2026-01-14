import Alpine from "alpinejs";
import focus from "@alpinejs/focus";

window.htmx = require("htmx.org");

window.Alpine = Alpine;
Alpine.plugin(focus);
Alpine.start();
