# Cloudflare development

Use `just install` to install Bun and Python dependencies. `just check` uses Bun's
built-in linter, formatter and type checker, followed by Ruff and ty. Formatter
options live in `bunfig.toml`; Jinja templates retain their required exclusion.
The line-width guide remains in `.editorconfig`.

The Python Worker retains Wrangler and `wrangler.jsonc`. The installed
`workers-py` package's `pywrangler sync` reads the JSONC compatibility date and
flags and does not accept `cloudflare.config.ts` or `wrangler.config.ts`.
`just build` continues to vendor the Python dependencies for that runtime.

`just deploy` installs dependencies, prepares Python packages, applies database
migrations, then uploads the Worker and the selected environment file's secrets
in one Wrangler deployment. A failed migration stops the upload.
Use `just environment=production deploy` for `.env.production`, or omit
`environment` for `.env`. The selected file also supplies local commands and
migrations and takes precedence over inherited environment variables. Keep
Cloudflare account/API credentials in the process environment, outside these
application files. Each key in the selected file is uploaded as a Worker secret.

GitHub Actions creates `.env` from the Production environment's existing app
secrets and variables with `SpicyPizza/create-envfile@v2.0`, then runs
`just deploy`, which migrates before deployment. The Worker name, custom domain, Hyperdrive binding and
SQLite Durable Object remain unchanged. The deployment migration uses `CI=true` to skip local Compose startup even
when deploying from a developer machine; it uses the selected database URL.

The current Pyodide 314.0.7 index supplies Pillow 12.2.0, while the normal
Python environment uses Pillow 13. `just build` applies four upstream Python
parser fixes needed by image validation:

- [GIF comment accumulation](https://github.com/python-pillow/Pillow/commit/68a3fe957d8a4d552e8c69d96066d749f0614c7e), addressing [GHSA-74r2-7ff9-mjj2](https://github.com/advisories/GHSA-74r2-7ff9-mjj2).
- [APNG disposal allocation](https://github.com/python-pillow/Pillow/commit/b564ea660bb3d56fcadaa7f29b4fc93a8f9e5c91), addressing [GHSA-5xm2-6676-qcp9](https://github.com/advisories/GHSA-5xm2-6676-qcp9).
- [Repeated EXIF headers](https://github.com/python-pillow/Pillow/commit/806e38381c781f32bbd22f4cd026678acd40fd6c), addressing [GHSA-g4qv-2jxx-769h](https://github.com/advisories/GHSA-g4qv-2jxx-769h), including JPEG's automatic EXIF DPI lookup.
- [Overlapping EXIF tag data](https://github.com/python-pillow/Pillow/commit/4908edaf7f416616784c7c03d8c1a60153710ffb), addressing [GHSA-wqgw-9xfh-qf2g](https://github.com/advisories/GHSA-wqgw-9xfh-qf2g).

The backports check the exact version and each file's source hash, are safe to
repeat, and refuse unknown older source. They become unnecessary once an
ABI-compatible Pillow 13 wheel is available. See the
[Pillow license](pillow-backport-license.txt). Always build through `just build`
or `just deploy`; calling Wrangler directly bypasses the vendoring safeguards.

Image uploads accept PNG, JPEG and GIF contents. Restricting the detected format
also prevents EPS files renamed with an allowed extension from reaching the
vulnerable EPS parser in Pillow 12.2 ([GHSA-pg7v-jwj7-p798](https://github.com/advisories/GHSA-pg7v-jwj7-p798)).
The backports do not include all security fixes in Pillow 13. The current upload
validator opens and verifies images; it does not decode pixels, seek animation
frames, transform, or encode images. Do not add those operations to the Worker
without reassessing the older wheel. Review the
[release notes](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html)
when changing image handling or when a compatible Worker wheel becomes available.
