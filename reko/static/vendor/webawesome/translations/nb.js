/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import "../chunks/chunk.DR3YY3XN.js";
import "../chunks/chunk.YR76HA7F.js";
import {
  registerTranslation
} from "../chunks/chunk.BYHIFG43.js";
import "../chunks/chunk.6E4D3PD7.js";

// src/translations/nb.ts
var translation = {
  $code: "nb",
  $name: "Norwegian Bokm\xE5l",
  $dir: "ltr",
  carousel: "Karusell",
  clearEntry: "T\xF8m felt",
  close: "Lukk",
  copied: "Kopiert",
  copy: "Kopier",
  currentValue: "N\xE5v\xE6rende verdi",
  error: "Feil",
  goToSlide: (slide, count) => `G\xE5 til visning ${slide} av ${count}`,
  hidePassword: "Skjul passord",
  loading: "Laster",
  nextSlide: "Neste visning",
  numOptionsSelected: (num) => {
    if (num === 0) return "Ingen alternativer valgt";
    if (num === 1) return "Ett alternativ valgt";
    return `${num} alternativer valgt`;
  },
  pauseAnimation: "Sett animasjon p\xE5 pause",
  playAnimation: "Spill av animasjon",
  previousSlide: "Forrige visning",
  progress: "Fremdrift",
  remove: "Fjern",
  resize: "Endre st\xF8rrelse",
  scrollableRegion: "Rullbar region",
  scrollToEnd: "Rull til slutten",
  scrollToStart: "Rull til starten",
  selectAColorFromTheScreen: "Velg en farge fra skjermen",
  showPassword: "Vis passord",
  slideNum: (slide) => `Visning ${slide}`,
  toggleColorFormat: "Bytt fargeformat",
  zoomIn: "Zoom inn",
  zoomOut: "Zoom ut"
};
registerTranslation(translation);
var nb_default = translation;
export {
  nb_default as default
};
