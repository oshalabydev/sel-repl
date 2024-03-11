from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess

HOSTNAME = "localhost"
PORT = 3000

CODE_FILE = "run.py"

class Server(BaseHTTPRequestHandler):
  def do_POST(self):
    if self.path == "/eval":
      len = int(self.headers.get("Content-Length"))
      body = json.loads(self.rfile.read(len).decode())

      input_string = body["code"] + "\n" + body["input"]
      proc = subprocess.run(["python3", "run.py"], capture_output=True, text=True, input=input_string)
      self.send_response(200)
      self.send_header("Content-Type", "application/json")

      if proc.returncode != 0:
        # not enough input
        if "EOFError" in proc.stderr:
          self.send_header("X-SEL-Status", "EINPUT")
          self.end_headers()

          response = json.dumps({ "eval": True, "message": "Input required", "sel_error": proc.stderr })
          self.wfile.write(response.encode())
          return
        
        self.send_header("X-SEL-Status", "ERR")
        self.end_headers()

        response = json.dumps({ "eval": True, "sel_error": proc.stderr })
        self.wfile.write(response.encode())
        return
      
      self.send_header("X-SEL-Status", "OK")
      self.end_headers()
      
      returned = proc.stdout.splitlines()[-1]
      output = proc.stdout[:proc.stdout.rfind("\n")]

      response = json.dumps({ "eval": True, "sel_returned": returned, "sel_output": output })
      self.wfile.write(response.encode())
    else:
      self.send_response(404)
      self.send_header("Content-Type", "application/json")
      self.end_headers()

      response = json.dumps({ "eval": False, "error": "Page not found" })
      self.wfile.write(response.encode())

def main():
  server = HTTPServer((HOSTNAME, PORT), Server)
  print(f"Server started at {HOSTNAME}:{PORT}")

  try:
    server.serve_forever()
  except:
    print("Server failed to start")

  server.server_close()
  print("Server stopped")

if __name__ == "__main__":
  main()