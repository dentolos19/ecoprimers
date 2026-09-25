import { defineConfig } from "oxlint";

export default defineConfig({
  ignorePatterns: ["src/templates/**"],
  plugins: ["typescript", "eslint"],
});
