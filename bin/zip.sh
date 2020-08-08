declare DIR="$(cd "$(dirname "$0")/.." && pwd -P)"
mkdir -p "$DIR/build"

declare addon_id='asset_manager'
declare name='anki_asset_manager' # for finding gui files

cd "$DIR"

"$DIR/bin/link.sh" -d

sed -i "s/$name.src.gui_config//" "$DIR/src/gui_config/"*".py"

cd "$DIR"

zip -r "build/$addon_id.ankiaddon" \
  "__init__.py" \
  "src/"*".py" \
  "src/lib/"*".py" \
  "src/gui_config/"*".py" \
  "src/gui_config/custom/"*".py" \
  "src/json_schemas/"* \
  "config."{json,md} \
  "manifest.json"

sed -i "s/.custom/$name.src.gui_config.custom/" "$DIR/src/gui_config/"*".py"
