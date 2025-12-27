/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import {
  divider_styles_default
} from "./chunk.ZD3NC7LB.js";
import {
  watch
} from "./chunk.N3AZYXKV.js";
import {
  WebAwesomeElement,
  n,
  t
} from "./chunk.CMPA2XAQ.js";
import {
  __decorateClass
} from "./chunk.6E4D3PD7.js";

// src/components/divider/divider.ts
var WaDivider = class extends WebAwesomeElement {
  constructor() {
    super(...arguments);
    this.orientation = "horizontal";
  }
  connectedCallback() {
    super.connectedCallback();
    this.setAttribute("role", "separator");
  }
  handleVerticalChange() {
    this.setAttribute("aria-orientation", this.orientation);
  }
};
WaDivider.css = divider_styles_default;
__decorateClass([
  n({ reflect: true })
], WaDivider.prototype, "orientation", 2);
__decorateClass([
  watch("orientation")
], WaDivider.prototype, "handleVerticalChange", 1);
WaDivider = __decorateClass([
  t("wa-divider")
], WaDivider);

export {
  WaDivider
};
