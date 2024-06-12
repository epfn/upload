import http.server
import socketserver
import cgi
import os
import io

UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers["content-type"])
        if ctype == "multipart/form-data":
            pdict["boundary"] = bytes(pdict["boundary"], "utf-8")
            pdict["CONTENT-LENGTH"] = int(self.headers["content-length"])

            data = self.rfile.read(pdict["CONTENT-LENGTH"])
            io_data = io.BytesIO(data)
            fields = cgi.parse_multipart(io_data, pdict)

            if "file" in fields:
                header = data.decode("utf-8", errors="ignore")
                header_lines = header.split("\r\n")
                file_id = 0
                files = []
                for line in header_lines:
                    if "Content-Disposition" in line:
                        parts = line.split(";")
                        for part in parts:
                            if "filename=" in part:
                                filename = part.split("=")[1].strip('"')
                                with open(
                                    os.path.join(UPLOAD_DIR, filename), "wb"
                                ) as output_file:
                                    output_file.write(fields["file"][file_id])
                                    print(f"uploaded {filename}")
                                    files.append(filename)
                                file_id += 1

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(", ".join(files).encode())
                return


Handler = SimpleHTTPRequestHandler

httpd = socketserver.TCPServer(("", 8000), Handler)
httpd.serve_forever()
