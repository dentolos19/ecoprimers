import json

from js import Object, WebSocketPair  # ty: ignore[unresolved-import] - Provided by the Workers runtime.
from pyodide.ffi import to_js
from workers import DurableObject, Response


class Room(DurableObject):
    """Durable Object that fans direct messages out to a user pair's WebSockets."""

    def __init__(self, state, env):
        super().__init__(state, env)
        self.state = state
        self.env = env

    async def fetch(self, request):
        """Accept the WebSocket upgrade for one member of the room's user pair."""
        upgrade_header = request.headers.get("Upgrade")
        if not upgrade_header or upgrade_header.lower() != "websocket":
            return Response("Expected WebSocket upgrade", status=400)

        # The Worker authenticates the session cookie before forwarding here.
        user_id = request.headers.get("X-Eco-User")
        if not user_id:
            return Response("Missing X-Eco-User header", status=401)

        client, server = WebSocketPair.new().object_values()
        self.state.acceptWebSocket(server)

        # Tag the socket so the room can tell the pair members apart if needed.
        try:
            server.serializeAttachment(to_js({"user_id": user_id}, dict_converter=Object.fromEntries))
        except Exception as error:  # noqa: BLE001 - JavaScript WebSocket calls can raise arbitrary errors.
            print(f"Failed to tag WebSocket with user id: {error}")

        return Response(None, status=101, web_socket=client)

    async def webSocketMessage(self, ws, message):
        """Reply to client pings; message persistence happens over HTTP."""
        try:
            data = json.loads(message)
        except (TypeError, ValueError):
            return

        if not isinstance(data, dict) or data.get("type") != "ping":
            return

        try:
            ws.send(json.dumps({"type": "pong"}))
        except Exception as error:  # noqa: BLE001 - JavaScript WebSocket calls can raise arbitrary errors.
            print(f"Failed to send pong: {error}")

    async def webSocketClose(self, ws, code, reason, wasClean):
        """Log disconnects so active session counts stay observable."""
        try:
            ws.close(code, reason)
        except Exception as error:  # noqa: BLE001 - JavaScript WebSocket calls can raise arbitrary errors.
            print(f"Failed to close WebSocket: {error}")

        active_connections = len(self.state.getWebSockets())
        print(f"Client disconnected. Active sessions: {active_connections}")

    async def webSocketError(self, ws, error):
        """Close the errored socket; per-socket failures are isolated."""
        try:
            ws.close(1011, "WebSocket error")
        except Exception as close_error:  # noqa: BLE001 - JavaScript WebSocket calls can raise arbitrary errors.
            print(f"Failed to close errored WebSocket: {close_error}")

        print(f"WebSocket error: {error}")

    async def broadcast(self, payload: dict) -> int:
        """Send a JSON payload to every socket in the room and return how many were reached."""
        message = json.dumps(payload)
        reached = 0

        for ws in self.state.getWebSockets():
            try:
                ws.send(message)
                reached += 1
            except Exception as error:  # noqa: BLE001 - JavaScript WebSocket calls can raise arbitrary errors.
                print(f"Failed to broadcast to session: {error}")

        return reached
