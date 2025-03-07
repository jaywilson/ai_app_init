from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
from agents.main_agent import ProjectAgent
from azure_utils import Azure

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/frontend_project":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                request_json = json.loads(post_data)
                content = request_json.get("content")
                agent = ProjectAgent()
                project = agent.build_frontend(content)
                response = {
                    "projectId": project.project_id,
                    "error": project.error,
                }
                self._send_json_response(response, 200)
            except json.JSONDecodeError as e:
                print(f"Error: {str(e)}")
                self._send_json_response({"error": "Invalid JSON"}, 400)     
        else:
            self._send_json_response({"error": "Endpoint not found"}, 404)

    def do_GET(self):
        if self.path.startswith('/download_project'):
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            project_id = params.get('project_id', [None])[0]
            
            if project_id is None:
                self._send_json_response({"error": "Missing project_id parameter"}, 400)
                return
                
            azure = Azure()
            project_zip_contents = azure.get_project_zip_contents(project_id)
           
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', f'attachment; filename="{project_id}.zip"')
            self.end_headers()
            self.wfile.write(project_zip_contents)
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