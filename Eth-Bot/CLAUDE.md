
Default to using pnpm with Node.js.

## Package Management

- Use `pnpm install` to install dependencies
- Use `pnpm add <package>` to add new dependencies
- Use `pnpm add -D <package>` to add dev dependencies
- Use `pnpm run <script>` to run scripts from package.json

## Running TypeScript

- Use `pnpm start` to run the main file (configured with tsx)
- Use `pnpm dev` to run with watch mode
- tsx provides fast TypeScript execution without separate build steps

## Environment Variables

- This project uses `dotenv` to load environment variables from `.env`
- Import `dotenv/config` at the top of entry files
- Never commit `.env` files to version control

## Testing

Use `vitest` for testing (when needed):

```ts
import { test, expect } from "vitest";

test("hello world", () => {
  expect(1).toBe(1);
});
```
