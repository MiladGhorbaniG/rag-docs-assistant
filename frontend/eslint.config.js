const js = require("@eslint/js");

module.exports = [
  js.configs.recommended,
  {
    ignores: [
      ".next/**",
      "node_modules/**",
      "next.config.js",
      "eslint.config.js",
    ],
  },
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: {
        window: "readonly",
        document: "readonly",
        fetch: "readonly",
        console: "readonly",
        TextDecoder: "readonly",
      },
    },
  },
  {
    files: ["**/*.test.js"],
    languageOptions: {
      globals: {
        describe: "readonly",
        it: "readonly",
        expect: "readonly",
      },
    },
  },
];
