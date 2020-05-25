module.exports = {
  env: {
    browser: true,
    es6: true,
  },
  extends: [
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    project: "tsconfig.json",
    createDefaultProgram: true,
    sourceType: "module",
  },
  plugins: [
    "@typescript-eslint",
    "@typescript-eslint/tslint",
  ],
  rules: {
    "@typescript-eslint/array-type": [
      "error",
      {
        default: "array-simple",
      },
    ],
    "@typescript-eslint/ban-types": [
      "error",
      {
        types: {
          Object: {
            message: "Avoid using the `Object` type. Did you mean `object`?",
          },
          Function: {
            message: "Avoid using the `Function` type. Prefer a specific function type, like `() => void`.",
          },
          Boolean: {
            message: "Avoid using the `Boolean` type. Did you mean `boolean`?",
          },
          Number: {
            message: "Avoid using the `Number` type. Did you mean `number`?",
          },
          String: {
            message: "Avoid using the `String` type. Did you mean `string`?",
          },
          Symbol: {
            message: "Avoid using the `Symbol` type. Did you mean `symbol`?",
          },
        },
      },
    ],
    "@typescript-eslint/camelcase": "off",
    "@typescript-eslint/consistent-type-definitions": "error",
    "@typescript-eslint/dot-notation": "error",
    "@typescript-eslint/explicit-member-accessibility": [
      "error",
      {
        accessibility: "explicit",
      },
    ],
    "@typescript-eslint/indent": [
      "error",
      2,
      {
        FunctionDeclaration: {
          parameters: "first",
        },
        FunctionExpression: {
          parameters: "first",
        },
      },
    ],
    "@typescript-eslint/member-delimiter-style": [
      "error",
      {
        multiline: {
          delimiter: "semi",
          requireLast: true,
        },
        singleline: {
          delimiter: "semi",
          requireLast: false,
        },
      },
    ],
    "@typescript-eslint/member-ordering": "error",
    "@typescript-eslint/no-explicit-any": "off",
    "@typescript-eslint/no-parameter-properties": "off",
    "@typescript-eslint/no-unused-expressions": "error",
    "@typescript-eslint/no-use-before-define": "off",
    "@typescript-eslint/prefer-for-of": "error",
    "@typescript-eslint/prefer-function-type": "error",
    "@typescript-eslint/quotes": [
      "error",
      "double",
      {
        avoidEscape: true,
      },
    ],
    "@typescript-eslint/semi": [
      "error",
      "always",
    ],
    "@typescript-eslint/triple-slash-reference": [
      "error",
      {
        path: "always",
        types: "prefer-import",
        lib: "always",
      },
    ],
    "@typescript-eslint/unified-signatures": "error",
    "arrow-body-style": "error",
    "arrow-parens": [
      "error",
      "always",
    ],
    "brace-style": [
      "error",
      "1tbs",
    ],
    "camelcase": "off",
    "comma-dangle": [
      "error",
      "always-multiline",
    ],
    "complexity": "off",
    "constructor-super": "error",
    "curly": "error",
    "eol-last": "error",
    "eqeqeq": [
      "error",
      "smart",
    ],
    "guard-for-in": "error",
    "id-blacklist": [
      "error",
      "any",
      "Number",
      "number",
      "String",
      "string",
      "Boolean",
      "boolean",
      "Undefined",
      "undefined",
    ],
    "id-match": "error",
    "max-classes-per-file": [
      "error",
      1,
    ],
    "max-len": [
      "error",
      {
        code: 200,
      },
    ],
    "new-parens": "error",
    "no-bitwise": "error",
    "no-caller": "error",
    "no-cond-assign": "error",
    "no-console": "error",
    "no-debugger": "error",
    "no-empty": "error",
    "no-eval": "error",
    "no-fallthrough": "off",
    "no-invalid-this": "off",
    "no-multiple-empty-lines": "error",
    "no-new-wrappers": "error",
    "no-shadow": [
      "error",
      {
        hoist: "all",
      },
    ],
    "no-throw-literal": "error",
    "no-trailing-spaces": "error",
    "no-undef-init": "error",
    "no-underscore-dangle": "error",
    "no-unsafe-finally": "error",
    "no-unused-labels": "error",
    "object-shorthand": "error",
    "one-var": [
      "error",
      "never",
    ],
    "prefer-arrow-callback": "error",
    "quote-props": [
      "error",
      "consistent-as-needed",
    ],
    "radix": "error",
    "space-before-function-paren": [
      "error",
      {
        anonymous: "never",
        asyncArrow: "always",
        named: "never",
      },
    ],
    "spaced-comment": [
      "off",
      "always",
      {
        markers: [
          "/",
        ],
      },
    ],
    "use-isnan": "error",
    "valid-typeof": "off",
    "@typescript-eslint/tslint/config": [
      "error",
      {
        rules: {
          "import-spacing": true,
          "object-literal-sort-keys": true,
          "whitespace": [
            true,
            "check-branch",
            "check-decl",
            "check-operator",
            "check-separator",
            "check-type",
            "check-typecast",
          ],
        },
      },
    ],
  },
};
