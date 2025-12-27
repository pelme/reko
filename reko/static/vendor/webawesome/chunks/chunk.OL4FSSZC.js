/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import {
  qr_code_styles_default
} from "./chunk.XVHTI7B7.js";
import {
  watch
} from "./chunk.N3AZYXKV.js";
import {
  WebAwesomeElement,
  e,
  n,
  r,
  t
} from "./chunk.CMPA2XAQ.js";
import {
  x
} from "./chunk.23WMFJHA.js";
import {
  __decorateClass
} from "./chunk.6E4D3PD7.js";

// src/components/qr-code/qr-code.ts
var QrCreator;
var WaQrCode = class extends WebAwesomeElement {
  constructor() {
    super(...arguments);
    this.value = "";
    this.label = "";
    this.size = 128;
    this.fill = "black";
    this.background = "white";
    this.radius = 0;
    this.errorCorrection = "H";
    this.generated = false;
  }
  firstUpdated(changedProperties) {
    super.firstUpdated(changedProperties);
    if (this.hasUpdated) {
      this.generate();
    }
  }
  generate() {
    this.style.setProperty("--size", `${this.size}px`);
    if (!this.hasUpdated) {
      return;
    }
    if (!QrCreator) {
      import("./qr-creator.es6.min.NMJ5JZMB.js").then((mod) => {
        QrCreator = mod.default;
        this.generate();
      });
      return;
    }
    QrCreator.render(
      {
        text: this.value,
        radius: this.radius,
        ecLevel: this.errorCorrection,
        fill: this.fill,
        background: this.background,
        // We draw the canvas larger and scale its container down to avoid blurring on high-density displays
        size: this.size * 2
      },
      this.canvas
    );
    this.generated = true;
  }
  render() {
    return x`
      <canvas
        part="base"
        class="qr-code"
        role="img"
        aria-label=${this.label?.length > 0 ? this.label : this.value}
      ></canvas>
    `;
  }
};
WaQrCode.css = qr_code_styles_default;
__decorateClass([
  e("canvas")
], WaQrCode.prototype, "canvas", 2);
__decorateClass([
  n()
], WaQrCode.prototype, "value", 2);
__decorateClass([
  n()
], WaQrCode.prototype, "label", 2);
__decorateClass([
  n({ type: Number })
], WaQrCode.prototype, "size", 2);
__decorateClass([
  n()
], WaQrCode.prototype, "fill", 2);
__decorateClass([
  n()
], WaQrCode.prototype, "background", 2);
__decorateClass([
  n({ type: Number })
], WaQrCode.prototype, "radius", 2);
__decorateClass([
  n({ attribute: "error-correction" })
], WaQrCode.prototype, "errorCorrection", 2);
__decorateClass([
  r()
], WaQrCode.prototype, "generated", 2);
__decorateClass([
  watch(["background", "errorCorrection", "fill", "radius", "size", "value"])
], WaQrCode.prototype, "generate", 1);
WaQrCode = __decorateClass([
  t("wa-qr-code")
], WaQrCode);

export {
  WaQrCode
};
