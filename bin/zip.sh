declare DIR="$(cd "$(dirname "$0")/.." && pwd -P)"
declare name='anki_asset_manager'

if [[ "$1" == '-a' ]]; then
  # for uploading to AnkiWeb
  declare addon_id=''
else
  # for installing myself
  declare addon_id='asset_manager'
fi

sed -i "s/${name}.src.gui_config//" "${DIR}/src/gui_config/"*".py"

cd "$DIR"

zip -r "${addon_id}.ankiaddon" \
  "__init__.py" \
  "src/"*".py" \
  "src/lib/"*".py" \
  "src/gui_config/"*".py" \
  "src/gui_config/custom/"*".py" \
  "src/json_schemas/"* \
  "config."{json,md} \
  "manifest.json"

sed -i "s/.custom/${name}.src.gui_config.custom/" "${DIR}/src/gui_config/"*".py"
