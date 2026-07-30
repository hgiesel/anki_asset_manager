var assetManagerGlobal = (() => {
  var __create = Object.create;
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __markAsModule = (target) => __defProp(target, "__esModule", { value: true });
  var __require = (x) => {
    if (typeof require !== "undefined")
      return require(x);
    throw new Error('Dynamic require of "' + x + '" is not supported');
  };
  var __export = (target, all) => {
    __markAsModule(target);
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __reExport = (target, module, desc) => {
    if (module && typeof module === "object" || typeof module === "function") {
      for (let key of __getOwnPropNames(module))
        if (!__hasOwnProp.call(target, key) && key !== "default")
          __defProp(target, key, { get: () => module[key], enumerable: !(desc = __getOwnPropDesc(module, key)) || desc.enumerable });
    }
    return target;
  };
  var __toModule = (module) => {
    return __reExport(__markAsModule(__defProp(module != null ? __create(__getProtoOf(module)) : {}, "default", module && module.__esModule && "default" in module ? { get: () => module.default, enumerable: true } : { value: module, enumerable: true })), module);
  };

  // editor.js
  var editor_exports = {};
  __export(editor_exports, {
    addAssetsButton: () => addAssetsButton,
    hideCardsButton: () => hideCardsButton
  });

  // AssetsButton.svelte
  var import_internal = __toModule(__require("svelte/internal"));
  function create_default_slot(ctx) {
    let t;
    return {
      c() {
        t = (0, import_internal.text)("Assets...");
      },
      m(target, anchor) {
        (0, import_internal.insert)(target, t, anchor);
      },
      d(detaching) {
        if (detaching)
          (0, import_internal.detach)(t);
      }
    };
  }
  function create_fragment(ctx) {
    let labelbutton;
    let current;
    labelbutton = new ctx[0]({
      props: {
        $$slots: { default: [create_default_slot] },
        $$scope: { ctx }
      }
    });
    labelbutton.$on("click", ctx[1]);
    return {
      c() {
        (0, import_internal.create_component)(labelbutton.$$.fragment);
      },
      m(target, anchor) {
        (0, import_internal.mount_component)(labelbutton, target, anchor);
        current = true;
      },
      p(ctx2, [dirty]) {
        const labelbutton_changes = {};
        if (dirty & 4) {
          labelbutton_changes.$$scope = { dirty, ctx: ctx2 };
        }
        labelbutton.$set(labelbutton_changes);
      },
      i(local) {
        if (current)
          return;
        (0, import_internal.transition_in)(labelbutton.$$.fragment, local);
        current = true;
      },
      o(local) {
        (0, import_internal.transition_out)(labelbutton.$$.fragment, local);
        current = false;
      },
      d(detaching) {
        (0, import_internal.destroy_component)(labelbutton, detaching);
      }
    };
  }
  function instance($$self) {
    const { LabelButton } = anki.components;
    const click_handler = () => globalThis.pycmd("assetManagerDialog");
    return [LabelButton, click_handler];
  }
  var AssetsButton = class extends import_internal.SvelteComponent {
    constructor(options) {
      super();
      (0, import_internal.init)(this, options, instance, create_fragment, import_internal.safe_not_equal, {});
    }
  };
  var AssetsButton_default = AssetsButton;

  // editor.js
  function addAssetsButton() {
    $editorToolbar.then((editorToolbar) => {
      editorToolbar.notetypeButtons.appendButton({ component: AssetsButton_default });
    });
  }
  function hideCardsButton() {
    $editorToolbar.then((editorToolbar) => {
      editorToolbar.notetypeButtons.hideButton(1);
    });
  }
  return editor_exports;
})();
