# Product Specifications

## Purpose

Eco Primers encourages sustainable, eco-friendly habits by rewarding people for taking part in green events and tasks, and by giving them a community to share progress and tips.

## Users

- **Members**: Sign up with email and password or Google, take part in events and tasks, earn and spend points, and interact with other members.
- **Administrators**: Manage users, events, tasks, reward products, and transactions, and review engagement analytics.

## Core Features

- **Accounts**: Email sign-up and login, Google sign-in, password reset by email through Resend, and editable profiles with followers and followings.
- **Events**: Browse events, view details, sign up, and withdraw.
- **Tasks and points**: Members submit a photo for a task, an AI model checks it against the task's criteria, and approved tasks award points.
- **Rewards**: Members redeem points for reward products, protected by Cloudflare Turnstile.
- **Transactions**: Members view their point transactions, see a transaction dashboard, and export transactions to an Excel file.
- **Community**: Members create, edit, delete, like, comment on, save, and share posts, and follow other members.
- **Messaging**: Direct messages between members with real-time delivery over WebSockets, message search, and restoring deleted messages.
- **Chatbot**: An AI assistant that gives sustainability tips.
- **News and weather**: Environmental news from NewsAPI and current weather from OpenWeather.
- **Donations**: A donation form that accepts amounts from S$0.50 to S$999,999.00 and shows a thank-you message.
- **Administration**: A dashboard with engagement analytics and AI-generated recommendations, plus create, edit, and delete pages for users, events, tasks, products, and transactions.
- **Dark mode**: A per-session light and dark theme toggle.

## Scope

- Routes are defined in [`src/routes.py`](src/routes.py) and [`src/routing/`](src/routing/), and data models in [`src/lib/models.py`](src/lib/models.py).
- AI features use OpenRouter with the prompts in [`src/prompts/`](src/prompts/).
- Uploaded images are stored in S3-compatible object storage and limited to PNG, JPEG, and GIF.

### Out of Scope

- Donations do not process payments; the form only validates the amount and thanks the member.
- The Worker does not decode, transform, or encode uploaded images. See the [Cloudflare guide](docs/guides/cloudflare.md#image-uploads).
