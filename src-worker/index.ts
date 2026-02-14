import { Container } from "@cloudflare/containers";
import { Hono } from "hono";

export class Server extends Container<CloudflareEnv> {
  defaultPort = 5000;
  sleepAfter = "10m";
}

const app = new Hono<{ Bindings: CloudflareEnv }>();

app.all("*", async (c) => {
  const instance = c.env.SERVER.getByName("singleton");
  const variables = Object.fromEntries(Object.entries(process.env)) as Record<string, string>;

  await instance.startAndWaitForPorts({
    startOptions: {
      envVars: variables,
    },
  });

  return await instance.fetch(c.req.raw);
});

export default app;
