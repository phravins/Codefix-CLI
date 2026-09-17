import http.server
import socketserver
import threading
import time
import requests
import asyncio
from debugger.llm import ask_ollama, ask_ollama_async

class MockOllamaHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        _ = self.rfile.read(content_length)
        time.sleep(0.01)  # 10ms processing latency
        response_body = b'{"response": "def fixed(): return True"}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        pass

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_mock_server(server):
    server.serve_forever()

def benchmark_ask_ollama(num_requests=50):
    t0 = time.perf_counter()
    for i in range(num_requests):
        res = ask_ollama(f"prompt {i}")
        assert res == "def fixed(): return True"
    t1 = time.perf_counter()
    return t1 - t0

async def benchmark_ask_ollama_async(num_requests=50):
    t0 = time.perf_counter()
    tasks = [ask_ollama_async(f"prompt {i}") for i in range(num_requests)]
    results = await asyncio.gather(*tasks)
    for res in results:
        assert res == "def fixed(): return True"
    t1 = time.perf_counter()
    return t1 - t0

def main():
    server = ReusableTCPServer(("127.0.0.1", 11434), MockOllamaHandler)
    server_thread = threading.Thread(target=run_mock_server, args=(server,), daemon=True)
    server_thread.start()

    print("Running optimized ask_ollama benchmark...")
    elapsed_sync = benchmark_ask_ollama(num_requests=50)
    print(f"Optimized 50 ask_ollama requests time (sequential session reuse): {elapsed_sync:.4f}s ({elapsed_sync/50*1000:.2f}ms/req)")

    elapsed_async = asyncio.run(benchmark_ask_ollama_async(num_requests=50))
    print(f"Optimized 50 ask_ollama_async requests time (concurrent execution): {elapsed_async:.4f}s ({elapsed_async/50*1000:.2f}ms/req)")

    server.shutdown()
    server.server_close()

if __name__ == "__main__":
    main()
