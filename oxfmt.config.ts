import { defineConfig } from "oxfmt";

export default defineConfig({
  ignorePatterns: ["src/templates/**"],
  printWidth: 120,
  sortImports: true,
  sortTailwindcss: true,
});
