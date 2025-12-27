/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import {
  skeleton_styles_default
} from "./chunk.ZHM3ZZWJ.js";
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

// src/components/skeleton/skeleton.ts
var WaSkeleton = class extends WebAwesomeElement {
  constructor() {
    super(...arguments);
    this.effect = "none";
  }
  render() {
    return x` <div part="indicator" class="indicator"></div> `;
  }
};
WaSkeleton.css = skeleton_styles_default;
__decorateClass([
  n({ reflect: true })
], WaSkeleton.prototype, "effect", 2);
WaSkeleton = __decorateClass([
  t("wa-skeleton")
], WaSkeleton);

export {
  WaSkeleton
};
