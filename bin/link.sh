#!/usr/bin/env bash
declare DIR="$(cd "$(dirname "$0")/.." && pwd -P)"

declare name='anki_asset_manager'
declare addon_dev_name="AssetManagerDev"

declare customdir=''

if [[ "$1" =~ ^-?d$ ]]; then
  sed -i "s/$addon_dev_name/$name/" "${DIR}/src/gui_config/"*".py"

  if [[ -d "$customdir" ]]; then
    rm -f "$customdir/$addon_dev_name"

  elif [[ -d "$HOME/.local/share/AnkiDev/addons21" ]]; then
    rm -f "$HOME/.local/share/AnkiDev/addons21/$addon_dev_name"

  elif [[ $(uname) = 'Darwin' ]]; then
    rm -f "$HOME/Library/Application Support/Anki2/addons21/$addon_dev_name"

  elif [[ $(uname) = 'Linux' ]]; then
    rm -f "$HOME/.local/share/Anki2/addons21/$addon_dev_name"

  else
    echo 'Unknown platform'
    exit -1
  fi

elif [[ "$1" =~ ^-?c$ ]]; then
  sed -i "s/$name/$addon_dev_name/" "${DIR}/src/gui_config/"*".py"

  if [[ -d "$customdir" ]]; then
    ln -s "$DIR" "$customdir/$addon_dev_name"

  elif [[ -d "$HOME/.local/share/AnkiDev/addons21" ]]; then
    ln -s "$DIR" "$HOME/.local/share/AnkiDev/addons21/$addon_dev_name"

  elif [[ $(uname) = 'Darwin' ]]; then
    ln -s "$DIR" "$HOME/Library/Application\ Support/Anki2/addons21/$addon_dev_name"

  elif [[ $(uname) = 'Linux' ]]; then
    ln -s "$DIR" "$HOME/.local/share/Anki2/addons21/$addon_dev_name"

  else
    echo 'Unknown platform'
    exit -1
  fi

else
  echo 'Unknown command'
  exit -2
fi
