/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import "../chunks/chunk.DR3YY3XN.js";
import "../chunks/chunk.YR76HA7F.js";
import {
  registerTranslation
} from "../chunks/chunk.BYHIFG43.js";
import "../chunks/chunk.6E4D3PD7.js";

// src/translations/da.ts
var translation = {
  $code: "da",
  $name: "Dansk",
  $dir: "ltr",
  carousel: "Karrusel",
  clearEntry: "Ryd indtastning",
  close: "Luk",
  copied: "Kopieret",
  copy: "Kopier",
  currentValue: "Nuv\xE6rende v\xE6rdi",
  error: "Fejl",
  goToSlide: (slide, count) => `G\xE5 til dias ${slide} af ${count}`,
  hidePassword: "Skjul adgangskode",
  loading: "Indl\xE6ser",
  nextSlide: "N\xE6ste slide",
  numOptionsSelected: (num) => {
    if (num === 0) return "Ingen valgt";
    if (num === 1) return "1 valgt";
    return `${num} valgt`;
  },
  pauseAnimation: "Pause animation",
  playAnimation: "Afspil animation",
  previousSlide: "Forrige dias",
  progress: "Status",
  remove: "Fjern",
  resize: "Tilpas st\xF8rrelse",
  scrollableRegion: "Rullebar region",
  scrollToEnd: "Scroll til slut",
  scrollToStart: "Scroll til start",
  selectAColorFromTheScreen: "V\xE6lg en farve fra sk\xE6rmen",
  showPassword: "Vis adgangskode",
  slideNum: (slide) => `Slide ${slide}`,
  toggleColorFormat: "Skift farveformat",
  zoomIn: "Zoom ind",
  zoomOut: "Zoom ud"
};
registerTranslation(translation);
var da_default = translation;
export {
  da_default as default
};
