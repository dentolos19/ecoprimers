# Agent Instructions

Eco Primers is a sustainability community web app where users join events, complete eco-friendly tasks for points, redeem rewards, and connect with each other. It is a Flask app deployed as a Cloudflare Python Worker.

## Commands

- `just setup`: Installs dependencies, starts local services, and migrates the database.
- `just install`: Installs Bun and Python dependencies from the lockfiles.
- `just start`: Runs the Flask development server on port 3000 with the client bundle in watch mode.
- `just compose`: Starts the local Postgres and S3 services with Docker Compose.
- `just decompose`: Stops the local services.
- `just build`: Builds the client bundle and vendors Python packages for the Worker.
- `just check`: Lints, formats, and type-checks the TypeScript and Python code.
- `just test`: Runs the Python unit tests.
- `just migrate`: Applies Alembic migrations.
- `just seed`: Seeds the database.
- `just deploy`: Migrates the database and deploys the Worker. Pass `environment=production` to use `.env.production`.

## Stack

Python Flask with Jinja templates and Bootstrap, SQLAlchemy and Alembic on Neon Postgres through Hyperdrive, TypeScript client scripts bundled by Bun, and a Durable Object for real-time messaging.

## Rules

- Always build through `just build` or `just deploy`; calling Wrangler directly bypasses the Pillow vendoring safeguards.
- Do not add image decoding, transforms, or encoding to the Worker without reassessing the Pillow backports.

## Documentation

- [Product Specifications](PRODUCT.md)
- [Design System](DESIGN.md)
- [Documentation Guidelines](docs/README.md)
- [Cloudflare Development](docs/guides/cloudflare.md)
