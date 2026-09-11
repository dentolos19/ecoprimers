import { Container as CloudflareContainer, getContainer } from "@cloudflare/containers";

export { ContainerProxy } from "@cloudflare/containers";

interface Env {
  AWS_ACCESS_KEY_ID: string;
  AWS_ENDPOINT_URL_S3: string;
  AWS_REGION: string;
  AWS_SECRET_ACCESS_KEY: string;
  CONTAINER: DurableObjectNamespace<Container>;
  DATABASE_URL: string;
  GOOGLE_CLIENT_ID: string;
  GOOGLE_CLIENT_SECRET: string;
  NEWS_API_KEY: string;
  OPENROUTER_API_KEY: string;
  OPENROUTER_MODEL: string;
  OPENROUTER_REFERER: string;
  OPENROUTER_TITLE: string;
  OPENWEATHER_API_KEY: string;
  RESEND_API_KEY: string;
  RESEND_FROM_EMAIL: string;
  RESEND_FROM_NAME: string;
  SECRET_KEY: string;
  TURNSTILE_SECRET_KEY: string;
  TURNSTILE_SITE_KEY: string;
}

export class Container extends CloudflareContainer<Env> {
  static outboundByHost = {
    "192.0.2.3": async (request: Request, env: Env) => {
      if (request.method !== "POST" || new URL(request.url).pathname !== "/verify") {
        return new Response("Not found", { status: 404 });
      }

      try {
        const body = (await request.json()) as { hostname?: string; remoteip?: string; response?: string };
        if (!body.response) return Response.json({ success: false }, { status: 400 });

        const form = new FormData();
        if (body.remoteip) form.set("remoteip", body.remoteip);
        form.set("response", body.response);
        form.set("secret", env.TURNSTILE_SECRET_KEY);
        const response = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
          body: form,
          method: "POST",
        });
        const result = (await response.json()) as {
          action?: string;
          hostname?: string;
          success?: boolean;
          "error-codes"?: string[];
        };
        const success = Boolean(
          response.ok &&
          result.success &&
          result.action === "redeem-reward" &&
          body.hostname &&
          result.hostname === body.hostname,
        );
        return Response.json(
          { ...result, success },
          {
            status: response.ok ? 200 : 502,
          },
        );
      } catch (error) {
        const message = error instanceof Error ? error.message : "Turnstile verification failed";
        throw new Error(`Unable to verify Turnstile response: ${message}`);
      }
    },
  };

  defaultPort = 3000;
  enableInternet = true;
  envVars = {
    AWS_ACCESS_KEY_ID: this.env.AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL_S3: this.env.AWS_ENDPOINT_URL_S3.replace("//localhost:", "//host.docker.internal:"),
    AWS_REGION: this.env.AWS_REGION,
    AWS_SECRET_ACCESS_KEY: this.env.AWS_SECRET_ACCESS_KEY,
    DATABASE_URL: this.env.DATABASE_URL.replace("@localhost:", "@host.docker.internal:"),
    GOOGLE_CLIENT_ID: this.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: this.env.GOOGLE_CLIENT_SECRET,
    NEWS_API_KEY: this.env.NEWS_API_KEY,
    OPENROUTER_API_KEY: this.env.OPENROUTER_API_KEY,
    OPENROUTER_MODEL: this.env.OPENROUTER_MODEL,
    OPENROUTER_REFERER: this.env.OPENROUTER_REFERER,
    OPENROUTER_TITLE: this.env.OPENROUTER_TITLE,
    OPENWEATHER_API_KEY: this.env.OPENWEATHER_API_KEY,
    RESEND_API_KEY: this.env.RESEND_API_KEY,
    RESEND_FROM_EMAIL: this.env.RESEND_FROM_EMAIL,
    RESEND_FROM_NAME: this.env.RESEND_FROM_NAME,
    SECRET_KEY: this.env.SECRET_KEY,
    TURNSTILE_SITE_KEY: this.env.TURNSTILE_SITE_KEY,
  };
  sleepAfter = "10m";
}

export default {
  async fetch(request: Request, env: Env) {
    return getContainer(env.CONTAINER, "singleton").fetch(request);
  },
} satisfies ExportedHandler<Env>;
