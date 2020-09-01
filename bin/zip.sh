declare DIR="$(cd "$(dirname "$0")/.." && pwd -P)"
mkdir -p "$DIR/build"

declare addon_id='asset_manager'
declare name='anki_asset_manager' # for finding gui files

cd "$DIR"

"$DIR/bin/compile.sh"

zip -r "build/$addon_id.ankiaddon" \
  "__init__.py" \
  "src/"*".py" \
  "src/lib/"*".py" \
  "gui_config/"*".py" \
  "gui_config/forms/"*".py" \
  "json_schemas/"* \
  "config."{json,md} \
  "manifest.json"
