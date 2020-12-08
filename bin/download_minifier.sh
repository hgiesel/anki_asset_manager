declare DIR="$(cd "$(dirname "$0")/.." && pwd -P)"

curl 'https://raw.githubusercontent.com/terser/html-minifier-terser/master/dist/htmlminifier.min.js' > "${DIR}/web/htmlminifier.js"
