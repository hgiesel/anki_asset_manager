const esbuild = require("esbuild");
const sveltePlugin = require("esbuild-svelte");

esbuild
  .build({
    entryPoints: ["./editor.js"],
    outfile: "editor-compiled.js",
    format: "iife",
    minify: false /* do not set this to true */,
    bundle: true,
    globalName: "assetManagerGlobal",
    splitting: false,
    external: ["svelte"],
    plugins: [sveltePlugin()],
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
