from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import openai_util

# Custom HTTP request handler
class RequestHandler(BaseHTTPRequestHandler):

    # Handle POST requests
    def do_POST(self):
        if self.path == "/completion":
            # Parse the content length to read the incoming request data
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)  # Read request body

            try:
                # Parse incoming data as JSON
                request_json = json.loads(post_data)

                # Extract relevant fields (depending on the use case)
                content = request_json.get("content", "")

                print(f"Received content {content}")
                # Dummy completion logic (replace with model inference)
                completion = openai_util.completion(content)

                # Respond to the client with the generated text
                response = {
                    "completion": completion
                }
                self._send_json_response(response, 200)

            except json.JSONDecodeError:
                # Invalid JSON in the request body
                self._send_json_response({"error": "Invalid JSON"}, 400)

        else:
            # Return a 404 Not Found for unknown endpoints
            self._send_json_response({"error": "Endpoint not found"}, 404)

    # Helper method to send a JSON response
    def _send_json_response(self, data, status_code):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

# Configure and run the HTTP server
def run_server(host="0.0.0.0", port=9002):
    server_address = (host, port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server running on http://{host}:{port}")
    httpd.serve_forever()

# Entry point
if __name__ == "__main__":
    run_server()