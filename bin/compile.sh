#!/usr/bin/env bash
declare DIR="$(cd "$(dirname "$0")/.." && pwd -P)"
declare name='anki_asset_manager'

rm -f "${DIR}/gui_config/forms/"*.py

for filename in "${DIR}/designer/"*'.ui'; do
  pyuic5 $filename > "${DIR}/gui_config/forms/$(basename ${filename%.*})_ui.py"
done

sed -i "s/$name.src.gui_config//" "$DIR/"*".py"
