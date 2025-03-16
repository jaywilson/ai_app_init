from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import traceback
from agents.main_agent import ProjectAgent, BackendName


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/frontend_project":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                request_json = json.loads(post_data)
                content = request_json.get("content")
                agent = ProjectAgent()
                project = agent.build_project(content, BackendName.JAVA)
                response = {
                    "projectId": project.project_id,
                    "error": project.error,
                }
                self._send_json_response(response, 200)
            except json.JSONDecodeError as e:
                print(traceback.format_exc())
                print(f"Error: {str(e)}")
                self._send_json_response({"error": "Invalid JSON"}, 400)     
        else:
            self._send_json_response({"error": "Endpoint not found"}, 404)

    def _send_json_response(self, data, status_code):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

def run_server(host="0.0.0.0", port=9002):
    server_address = (host, port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server running on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()