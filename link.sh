#!/usr/bin/env bash
declare DIR=$(realpath ${BASH_SOURCE%/*})
declare customdir=''

declare projname='anki_script_manager'

if [[ "$customdir" ]]; then
  target="${customdir}/${projname}"

elif [[ $(uname) = 'Darwin' ]]; then
  target="$HOME/Library/Application Support/Anki2/addons21/${projname}"

elif [[ $(uname) = 'Linux' ]]; then
  target="$HOME/.local/share/Anki2/addons21/${projname}"

else
  echo 'Unknown platform'
  exit -1
fi

if [[ "$1" == '-d' || "$1" =~ ^d ]]; then
  rm "$target"
elif [[ ! -h "${target}" ]]; then
  ln -s "${DIR}" "${target}"
fi
