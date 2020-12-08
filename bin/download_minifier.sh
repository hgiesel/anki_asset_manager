declare DIR="$(cd "$(dirname "$0")/.." && pwd -P)"

curl 'https://raw.githubusercontent.com/terser/html-minifier-terser/master/dist/htmlminifier.min.js' > "${DIR}/web/htmlminifier.js"
curl 'https://cdn.jsdelivr.net/npm/terser/dist/bundle.min.js' > "${DIR}/web/terser.js"
