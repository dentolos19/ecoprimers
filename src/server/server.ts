import { Container, getContainer } from "@cloudflare/containers";
import { Hono } from "hono";

export class Server extends Container<Env> {
  defaultPort = 3000;
  sleepAfter = "10m";
  envVars = Object.fromEntries(
    Object.entries(this.env).filter(([, value]) => typeof value === "string" && !!value),
  ) as Record<string, string>;
}

const app = new Hono<{ Bindings: Env }>();

app.all("*", async (c) => {
  const instance = getContainer<Server>(c.env.SERVER, "singleton");
  return instance.fetch(c.req.raw);
});

export default app;
