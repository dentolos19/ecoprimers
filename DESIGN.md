# Design System

## Framework

- Pages are server-rendered Jinja templates in [`src/templates/`](src/templates/), all extending [`base.html`](src/templates/base.html).
- Bootstrap 5.3 provides the layout, components, and utilities, loaded from a CDN with Bootstrap Icons and Font Awesome icons.
- Client behavior lives in TypeScript under [`src/client/`](src/client/), bundled by Bun into `public/static/js/`. Chart.js renders dashboard charts, and Marked with DOMPurify renders Markdown in chat, messages, and dashboard recommendations.

## Styling

- Custom styles live in [`public/static/css/`](public/static/css/). Prefer Bootstrap classes and add custom CSS only when Bootstrap has no equivalent.
- `base.css` defines the full-height app shell and the admin layout. `utilities.css` defines layered containers. `fun.css` defines decorative backgrounds.
- No custom color, font, or radius tokens are defined; the Bootstrap defaults apply.

## Theming

- The `<html>` element sets `data-bs-theme` to `dark` or `light` from the session, and dark mode is the default.
- Dark mode also loads `base-dark.css` and `fun-dark.css` for overrides that Bootstrap's theme does not cover.

## Layout

- The app shell is a full-height column with the navigation bar on top and a scrollable body.
- The navigation bar is a responsive Bootstrap navbar on `bg-secondary-subtle` that collapses on small screens.
- Admin pages extend [`admin/base.html`](src/templates/admin/base.html), which adds a narrow icon sidebar with tooltips.
- Content is built mostly from cards, forms, list groups, and flex utilities.

## Components

- Shared partials live in [`src/templates/components/`](src/templates/components/): navigation, flash messages, and toasts.
- Flash messages render as Bootstrap toasts bordered with the message category color. Client code creates matching toasts with [`toast.ts`](src/client/toast.ts).
