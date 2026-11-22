# 0001. Wrangler JSONC for Python Worker

- Status: Accepted
- Date: 2026-11-01

## Context

The application runs as a Cloudflare Python Worker. Its build vendors Python dependencies with the `workers-py` package's `pywrangler sync`, which reads the compatibility date and flags from the Wrangler configuration.

## Decision

Keep Wrangler and [`wrangler.jsonc`](../../wrangler.jsonc) as the Worker configuration. `pywrangler sync` reads the JSONC compatibility date and flags and does not accept `cloudflare.config.ts` or `wrangler.config.ts`, so those formats are not used.

## Consequences

- The Worker name, custom domain, Hyperdrive binding, and Durable Object are configured in `wrangler.jsonc`.
- Builds must go through `just build` or `just deploy` so Python dependencies are vendored for the runtime. See the [Cloudflare guide](../guides/cloudflare.md).
