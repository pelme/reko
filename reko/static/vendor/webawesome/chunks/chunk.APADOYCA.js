/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import {
  progress_bar_styles_default
} from "./chunk.BT4W5YLH.js";
import {
  clamp
} from "./chunk.KABXVFSA.js";
import {
  o
} from "./chunk.G3G3UFWM.js";
import {
  LocalizeController
} from "./chunk.DR3YY3XN.js";
import {
  WebAwesomeElement,
  n,
  t
} from "./chunk.CMPA2XAQ.js";
import {
  x
} from "./chunk.23WMFJHA.js";
import {
  __decorateClass
} from "./chunk.6E4D3PD7.js";

// src/components/progress-bar/progress-bar.ts
var WaProgressBar = class extends WebAwesomeElement {
  constructor() {
    super(...arguments);
    this.localize = new LocalizeController(this);
    this.value = 0;
    this.indeterminate = false;
    this.label = "";
  }
  updated(changedProperties) {
    if (changedProperties.has("value")) {
      requestAnimationFrame(() => {
        this.style.setProperty("--percentage", `${clamp(this.value, 0, 100)}%`);
      });
    }
  }
  render() {
    return x`
      <div
        part="base"
        class="progress-bar"
        role="progressbar"
        title=${o(this.title)}
        aria-label=${this.label.length > 0 ? this.label : this.localize.term("progress")}
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow=${this.indeterminate ? "0" : this.value}
      >
        <div part="indicator" class="indicator">
          ${!this.indeterminate ? x` <slot part="label" class="label"></slot> ` : ""}
        </div>
      </div>
    `;
  }
};
WaProgressBar.css = progress_bar_styles_default;
__decorateClass([
  n({ type: Number, reflect: true })
], WaProgressBar.prototype, "value", 2);
__decorateClass([
  n({ type: Boolean, reflect: true })
], WaProgressBar.prototype, "indeterminate", 2);
__decorateClass([
  n()
], WaProgressBar.prototype, "label", 2);
WaProgressBar = __decorateClass([
  t("wa-progress-bar")
], WaProgressBar);

export {
  WaProgressBar
};
