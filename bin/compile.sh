#!/usr/bin/env bash
declare DIR="$(cd "$(dirname "$0")/../src/gui_config" && pwd -P)"
declare name='anki_asset_manager'

rm -f "${DIR}/"*.py

for filename in "${DIR}/"*'.ui'; do
  pyuic5 $filename > "${filename%.*}_ui.py"
done

sed -i "s/$name.src.gui_config//" "$DIR/"*".py"
