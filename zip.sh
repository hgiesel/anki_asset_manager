declare DIR=${BASH_SOURCE%/*}
declare name='anki_script_manager'

if [[ "$1" == '-a' ]]; then
  # for uploading to AnkiWeb
  declare addon_id='667831375'
else
  # for installing myself
  declare addon_id='script_manager'
fi

rm -f "${DIR}/${addon_id}.ankiaddon"
sed -i "s/${name}.src.gui_config//" "${DIR}/src/gui_config/"*".py"

zip -r "${DIR}/${addon_id}.ankiaddon" \
  "${DIR}/__init__.py" \
  "${DIR}/src/"*".py" \
  "${DIR}/src/lib/"*".py" \
  "${DIR}/src/gui_config/"*".py" \
  "${DIR}/src/gui_config/custom/"*".py" \
  "${DIR}/src/json_schemas/"* \
  "${DIR}/config."{json,md} "${DIR}/manifest.json"

sed -i "s/.custom/${name}.src.gui_config.custom/" "${DIR}/src/gui_config/"*".py"
