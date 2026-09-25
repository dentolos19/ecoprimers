import { defineConfig } from "oxfmt";

export default defineConfig({
  ignorePatterns: ["src/templates/**"],
  sortImports: true,
  sortTailwindcss: true,
});
