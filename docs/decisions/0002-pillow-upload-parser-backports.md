# 0002. Pillow Upload Parser Backports

- Status: Accepted
- Date: 2026-11-01

## Context

The Pyodide 314.0.7 index used by the Worker supplies Pillow 12.2.0, while the normal Python environment uses Pillow 13. Image upload validation relies on Pillow parsers with known advisories that Pillow 13 fixes, and no ABI-compatible Pillow 13 wheel is available for the Worker.

## Decision

Apply four upstream Python parser fixes to the vendored Pillow during `just build` with [`scripts/patch_pillow.py`](../../scripts/patch_pillow.py). The patch checks the exact version and each file's source hash, is safe to repeat, and refuses unknown older source. Upload validation also restricts detected formats to PNG, JPEG, and GIF.

Keep Pillow's redistribution license in [`scripts/pillow-backport-license.txt`](../../scripts/pillow-backport-license.txt), beside the script that carries the backported code, rather than in `docs/`.

## Consequences

- The backports do not include all security fixes in Pillow 13. The Worker only opens and verifies images; decoding pixels, seeking animation frames, transforming, or encoding images requires reassessing the older wheel first.
- Remove the backports and the license file once an ABI-compatible Pillow 13 wheel is available.
- The fixes and advisories are listed in the [Cloudflare guide](../guides/cloudflare.md#pillow-backports).
