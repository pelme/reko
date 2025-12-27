/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import {
  RequiredValidator
} from "./chunk.EHXOY5WV.js";
import {
  l
} from "./chunk.T7SKOEAS.js";
import {
  form_control_styles_default
} from "./chunk.S3VHOE2O.js";
import {
  checkbox_styles_default
} from "./chunk.P5GQVQYH.js";
import {
  WebAwesomeFormAssociatedElement
} from "./chunk.EC4QVN46.js";
import {
  e as e2
} from "./chunk.6MY2PWCO.js";
import {
  HasSlotController
} from "./chunk.SFADIYDM.js";
import {
  size_styles_default
} from "./chunk.KXWF6EXL.js";
import {
  o as o2
} from "./chunk.G3G3UFWM.js";
import {
  watch
} from "./chunk.N3AZYXKV.js";
import {
  e,
  n,
  t
} from "./chunk.CMPA2XAQ.js";
import {
  o
} from "./chunk.HAXJJGQX.js";
import {
  x
} from "./chunk.23WMFJHA.js";
import {
  __decorateClass
} from "./chunk.6E4D3PD7.js";

// src/components/checkbox/checkbox.ts
var WaCheckbox = class extends WebAwesomeFormAssociatedElement {
  constructor() {
    super(...arguments);
    this.hasSlotController = new HasSlotController(this, "hint");
    this.title = "";
    this.name = "";
    this._value = this.getAttribute("value") ?? null;
    this.size = "medium";
    this.disabled = false;
    this.indeterminate = false;
    this.checked = this.hasAttribute("checked");
    this.defaultChecked = this.hasAttribute("checked");
    this.required = false;
    this.hint = "";
  }
  static get validators() {
    const validators = o ? [] : [
      RequiredValidator({
        validationProperty: "checked",
        // Use a checkbox so we get "free" translation strings.
        validationElement: Object.assign(document.createElement("input"), {
          type: "checkbox",
          required: true
        })
      })
    ];
    return [...super.validators, ...validators];
  }
  /** The value of the checkbox, submitted as a name/value pair with form data. */
  get value() {
    const val = this._value || "on";
    return this.checked ? val : null;
  }
  set value(val) {
    this._value = val;
  }
  handleClick() {
    this.hasInteracted = true;
    this.checked = !this.checked;
    this.indeterminate = false;
    this.updateComplete.then(() => {
      this.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
    });
  }
  handleDefaultCheckedChange() {
    if (!this.hasInteracted && this.checked !== this.defaultChecked) {
      this.checked = this.defaultChecked;
      this.handleValueOrCheckedChange();
    }
  }
  handleValueOrCheckedChange() {
    this.setValue(this.checked ? this.value : null, this._value);
    this.updateValidity();
  }
  handleStateChange() {
    if (this.hasUpdated) {
      this.input.checked = this.checked;
      this.input.indeterminate = this.indeterminate;
    }
    this.customStates.set("checked", this.checked);
    this.customStates.set("indeterminate", this.indeterminate);
    this.updateValidity();
  }
  handleDisabledChange() {
    this.customStates.set("disabled", this.disabled);
  }
  willUpdate(changedProperties) {
    super.willUpdate(changedProperties);
    if (changedProperties.has("defaultChecked")) {
      if (!this.hasInteracted) {
        this.checked = this.defaultChecked;
      }
    }
    if (changedProperties.has("value") || changedProperties.has("checked")) {
      this.handleValueOrCheckedChange();
    }
  }
  formResetCallback() {
    this.checked = this.defaultChecked;
    super.formResetCallback();
    this.handleValueOrCheckedChange();
  }
  /** Simulates a click on the checkbox. */
  click() {
    this.input.click();
  }
  /** Sets focus on the checkbox. */
  focus(options) {
    this.input.focus(options);
  }
  /** Removes focus from the checkbox. */
  blur() {
    this.input.blur();
  }
  render() {
    const hasHintSlot = o ? true : this.hasSlotController.test("hint");
    const hasHint = this.hint ? true : !!hasHintSlot;
    const isIndeterminate = !this.checked && this.indeterminate;
    const iconName = isIndeterminate ? "indeterminate" : "check";
    const iconState = isIndeterminate ? "indeterminate" : "check";
    return x`
      <label part="base">
        <span part="control">
          <input
            class="input"
            type="checkbox"
            title=${this.title}
            name=${this.name}
            value=${o2(this._value)}
            .indeterminate=${l(this.indeterminate)}
            .checked=${l(this.checked)}
            .disabled=${this.disabled}
            .required=${this.required}
            aria-checked=${this.checked ? "true" : "false"}
            aria-describedby="hint"
            @click=${this.handleClick}
          />

          <wa-icon part="${iconState}-icon icon" library="system" name=${iconName}></wa-icon>
        </span>

        <slot part="label"></slot>
      </label>

      <slot
        id="hint"
        part="hint"
        name="hint"
        aria-hidden=${hasHint ? "false" : "true"}
        class="${e2({ "has-slotted": hasHint })}"
      >
        ${this.hint}
      </slot>
    `;
  }
};
WaCheckbox.css = [form_control_styles_default, size_styles_default, checkbox_styles_default];
WaCheckbox.shadowRootOptions = { ...WebAwesomeFormAssociatedElement.shadowRootOptions, delegatesFocus: true };
__decorateClass([
  e('input[type="checkbox"]')
], WaCheckbox.prototype, "input", 2);
__decorateClass([
  n()
], WaCheckbox.prototype, "title", 2);
__decorateClass([
  n({ reflect: true })
], WaCheckbox.prototype, "name", 2);
__decorateClass([
  n({ reflect: true })
], WaCheckbox.prototype, "value", 1);
__decorateClass([
  n({ reflect: true })
], WaCheckbox.prototype, "size", 2);
__decorateClass([
  n({ type: Boolean })
], WaCheckbox.prototype, "disabled", 2);
__decorateClass([
  n({ type: Boolean, reflect: true })
], WaCheckbox.prototype, "indeterminate", 2);
__decorateClass([
  n({ type: Boolean, attribute: false })
], WaCheckbox.prototype, "checked", 2);
__decorateClass([
  n({ type: Boolean, reflect: true, attribute: "checked" })
], WaCheckbox.prototype, "defaultChecked", 2);
__decorateClass([
  n({ type: Boolean, reflect: true })
], WaCheckbox.prototype, "required", 2);
__decorateClass([
  n()
], WaCheckbox.prototype, "hint", 2);
__decorateClass([
  watch("defaultChecked")
], WaCheckbox.prototype, "handleDefaultCheckedChange", 1);
__decorateClass([
  watch(["checked", "indeterminate"])
], WaCheckbox.prototype, "handleStateChange", 1);
__decorateClass([
  watch("disabled")
], WaCheckbox.prototype, "handleDisabledChange", 1);
WaCheckbox = __decorateClass([
  t("wa-checkbox")
], WaCheckbox);

export {
  WaCheckbox
};
