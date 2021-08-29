import AssetsButton from "./AssetsButton.svelte";

export function addAssetsButton() {
    $editorToolbar.then((editorToolbar) => {
      editorToolbar.notetypeButtons.appendButton({ component: AssetsButton });
    });
}

export function hideCardsButton() {
    $editorToolbar.then((editorToolbar) => {
      editorToolbar.notetypeButtons.hideButton(1);
    });
}
