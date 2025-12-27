/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import {
  carousel_item_styles_default
} from "./chunk.72DAAFMZ.js";
import {
  WebAwesomeElement,
  t
} from "./chunk.CMPA2XAQ.js";
import {
  x
} from "./chunk.23WMFJHA.js";
import {
  __decorateClass
} from "./chunk.6E4D3PD7.js";

// src/components/carousel-item/carousel-item.ts
var WaCarouselItem = class extends WebAwesomeElement {
  connectedCallback() {
    super.connectedCallback();
    this.setAttribute("role", "group");
  }
  render() {
    return x` <slot></slot> `;
  }
};
WaCarouselItem.css = carousel_item_styles_default;
WaCarouselItem = __decorateClass([
  t("wa-carousel-item")
], WaCarouselItem);

export {
  WaCarouselItem
};
