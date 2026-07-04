import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .management import ManagementStore


STATIC_DIR = Path(__file__).with_name("static")
CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
}


def create_handler(store: ManagementStore) -> type[BaseHTTPRequestHandler]:
    class ManagementRequestHandler(BaseHTTPRequestHandler):
        server_version = "FactoryPublicTest/0.1"

        def do_GET(self) -> None:
            path, query = self._route_parts()

            if path == "/":
                self._send_static("index.html")
                return
            if path.startswith("/assets/"):
                self._send_static(path.removeprefix("/assets/"))
                return
            if path == "/api/dashboard":
                self._send_json(store.dashboard())
                return
            if path == "/api/projects":
                self._send_json(
                    {"projects": [project.to_dict() for project in store.list_projects()]}
                )
                return
            if path == "/api/tasks":
                project_id = query.get("project_id", [None])[0]
                try:
                    items = store.list_work_items(
                        int(project_id) if project_id is not None else None
                    )
                except (KeyError, ValueError) as exc:
                    self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                    return
                self._send_json({"work_items": [item.to_dict() for item in items]})
                return

            self._send_error(HTTPStatus.NOT_FOUND, "Route not found")

        def do_POST(self) -> None:
            path, _query = self._route_parts()

            try:
                payload = self._read_json()
                if path == "/api/projects":
                    project = store.create_project(
                        name=str(payload.get("name", "")),
                        owner=str(payload.get("owner", "")),
                        status=str(payload.get("status", "planned")),
                        description=str(payload.get("description", "")),
                    )
                    self._send_json(project.to_dict(), HTTPStatus.CREATED)
                    return
                if path == "/api/tasks":
                    item = store.create_work_item(
                        project_id=int(payload.get("project_id", 0)),
                        title=str(payload.get("title", "")),
                        assignee=str(payload.get("assignee", "")),
                        status=str(payload.get("status", "todo")),
                        priority=str(payload.get("priority", "medium")),
                        points=int(payload.get("points", 1)),
                        due_date=str(payload.get("due_date", "")),
                    )
                    self._send_json(item.to_dict(), HTTPStatus.CREATED)
                    return
            except (KeyError, ValueError) as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return

            self._send_error(HTTPStatus.NOT_FOUND, "Route not found")

        def do_PATCH(self) -> None:
            path, _query = self._route_parts()
            payload = self._read_json()

            try:
                if path.startswith("/api/projects/") and path.endswith("/status"):
                    project_id = int(path.split("/")[3])
                    project = store.update_project_status(
                        project_id, str(payload.get("status", ""))
                    )
                    self._send_json(project.to_dict())
                    return
                if path.startswith("/api/tasks/"):
                    item_id = int(path.split("/")[3])
                    allowed = {
                        key: payload[key]
                        for key in (
                            "title",
                            "assignee",
                            "status",
                            "priority",
                            "points",
                            "due_date",
                        )
                        if key in payload
                    }
                    item = store.update_work_item(item_id, **allowed)
                    self._send_json(item.to_dict())
                    return
            except (KeyError, ValueError) as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return

            self._send_error(HTTPStatus.NOT_FOUND, "Route not found")

        def log_message(self, format: str, *args: object) -> None:
            return

        def _route_parts(self) -> tuple[str, dict[str, list[str]]]:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/") or "/"
            return path, parse_qs(parsed.query)

        def _read_json(self) -> dict[str, object]:
            length = int(self.headers.get("Content-Length", "0"))
            if length == 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw)

        def _send_json(
            self,
            payload: dict[str, object],
            status: HTTPStatus = HTTPStatus.OK,
        ) -> None:
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", CONTENT_TYPES[".json"])
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_static(self, name: str) -> None:
            target = (STATIC_DIR / name).resolve()
            if STATIC_DIR.resolve() not in target.parents and target != STATIC_DIR:
                self._send_error(HTTPStatus.NOT_FOUND, "Asset not found")
                return
            if not target.is_file():
                self._send_error(HTTPStatus.NOT_FOUND, "Asset not found")
                return

            body = target.read_bytes()
            content_type = CONTENT_TYPES.get(target.suffix, "text/plain; charset=utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_error(self, status: HTTPStatus, message: str) -> None:
            self._send_json({"error": message}, status)

    return ManagementRequestHandler


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    store = ManagementStore.seeded()
    server = ThreadingHTTPServer((host, port), create_handler(store))
    print(f"Factory Public Test running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nFactory Public Test stopped")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the demo management system.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    run(args.host, args.port)


if __name__ == "__main__":
    main()
