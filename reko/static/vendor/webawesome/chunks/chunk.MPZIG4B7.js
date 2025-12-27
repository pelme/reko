/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import {
  variants_styles_default
} from "./chunk.36EZLX6Z.js";
import {
  badge_styles_default
} from "./chunk.KT565SLV.js";
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

// src/components/badge/badge.ts
var WaBadge = class extends WebAwesomeElement {
  constructor() {
    super(...arguments);
    this.variant = "brand";
    this.appearance = "accent";
    this.pill = false;
    this.attention = "none";
  }
  render() {
    return x` <slot part="base" role="status"></slot>`;
  }
};
WaBadge.css = [variants_styles_default, badge_styles_default];
__decorateClass([
  n({ reflect: true })
], WaBadge.prototype, "variant", 2);
__decorateClass([
  n({ reflect: true })
], WaBadge.prototype, "appearance", 2);
__decorateClass([
  n({ type: Boolean, reflect: true })
], WaBadge.prototype, "pill", 2);
__decorateClass([
  n({ reflect: true })
], WaBadge.prototype, "attention", 2);
WaBadge = __decorateClass([
  t("wa-badge")
], WaBadge);

export {
  WaBadge
};
