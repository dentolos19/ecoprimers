from flask import request

from lib import env


def room_key(user_a, user_b) -> str:
    """Return the canonical key for the direct-message room between two users."""
    return ":".join(sorted([str(user_a), str(user_b)]))


def notify(user_a, user_b, payload: dict) -> None:
    """Broadcast a payload to the WebSockets connected to a user pair's room."""
    if "workers.env" not in request.environ:
        return

    from pyodide.ffi import run_sync

    rooms = env.binding("ROOMS")
    stub = rooms.get(rooms.idFromName(room_key(user_a, user_b)))

    try:
        run_sync(stub.broadcast(payload))
    except Exception as error:  # noqa: BLE001 - Notification fan-out is best-effort.
        # Notification is best-effort: persistence already succeeded, so a
        # failed fan-out must not fail the request that triggered it.
        print(f"Failed to notify room {room_key(user_a, user_b)}: {error}")
