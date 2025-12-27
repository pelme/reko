/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import {
  callout_styles_default
} from "./chunk.VXSWBQ6P.js";
import {
  size_styles_default
} from "./chunk.KXWF6EXL.js";
import {
  variants_styles_default
} from "./chunk.36EZLX6Z.js";
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

// src/components/callout/callout.ts
var WaCallout = class extends WebAwesomeElement {
  constructor() {
    super(...arguments);
    this.variant = "brand";
    this.size = "medium";
  }
  render() {
    return x`
      <div part="icon">
        <slot name="icon"></slot>
      </div>

      <div part="message">
        <slot></slot>
      </div>
    `;
  }
};
WaCallout.css = [callout_styles_default, variants_styles_default, size_styles_default];
__decorateClass([
  n({ reflect: true })
], WaCallout.prototype, "variant", 2);
__decorateClass([
  n({ reflect: true })
], WaCallout.prototype, "appearance", 2);
__decorateClass([
  n({ reflect: true })
], WaCallout.prototype, "size", 2);
WaCallout = __decorateClass([
  t("wa-callout")
], WaCallout);

export {
  WaCallout
};
