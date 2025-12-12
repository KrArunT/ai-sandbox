import os
import pty
import select
import struct
import fcntl
import termios
import asyncio
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()

# Get Supabase Config
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ... (logging config) ...

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

def get_supabase_config():
    return {"url": SUPABASE_URL, "key": SUPABASE_KEY}

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "supabase_config": get_supabase_config()
    })

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "supabase_config": get_supabase_config()
    })

@app.websocket("/ws/terminal")
async def websocket_terminal(websocket: WebSocket):
    await websocket.accept()
    
    # Create a pseudo-terminal
    master_fd, slave_fd = pty.openpty()
    
    # Start the shell (bash)
    shell = os.environ.get("SHELL", "/bin/bash")
    
    # Ensure TERM is set
    os.environ["TERM"] = "xterm-256color"
    
    pid = os.fork()
    
    if pid == 0:
        # Child process
        os.setsid()
        os.dup2(slave_fd, 0)
        os.dup2(slave_fd, 1)
        os.dup2(slave_fd, 2)
        os.close(master_fd)
        os.close(slave_fd)
        
        # Execute the shell
        os.execl(shell, shell)
    else:
        # Parent process (WebSocket handler)
        os.close(slave_fd)
        
        loop = asyncio.get_running_loop()
        
        try:
            while True:
                # Use select to wait for input/output availability
                # We need to act as a bridge between the WebSocket and the PTY
                
                # Check for output from PTY to send to WebSocket
                # Doing this async is tricky with blocking read on FD.
                # We'll use loop.run_in_executor for reading from PTY to avoid blocking the event loop
                
                # However, a simpler approach for a demo/sandbox is to use a separate task or Select
                # interacting with async context.
                
                # Let's try a simpler select-based non-blocking read loop with sleep
                # or use add_reader
                
                # Using asyncio.create_task for reading from WS
                
                async def read_from_ws():
                    try:
                        while True:
                            data = await websocket.receive_text()
                            # Handle resize events or input
                            if data.startswith('{"type":"resize"'):
                                import json
                                try:
                                    msg = json.loads(data)
                                    rows = msg.get('rows', 24)
                                    cols = msg.get('cols', 80)
                                    # Set window size
                                    winsize = struct.pack("HHHH", rows, cols, 0, 0)
                                    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
                                except Exception as e:
                                    logger.error(f"Error resizing: {e}")
                            else:
                                # Write to PTY
                                os.write(master_fd, data.encode())
                    except WebSocketDisconnect:
                        logger.info("WebSocket disconnected")
                    except Exception as e:
                        logger.error(f"WebSocket error: {e}")

                read_task = asyncio.create_task(read_from_ws())
                
                try:
                    while True:
                        await asyncio.sleep(0.01)
                        # Check if data is available to read from master_fd
                        r, w, e = select.select([master_fd], [], [], 0)
                        if master_fd in r:
                            output = os.read(master_fd, 10240)
                            if not output:
                                break
                            await websocket.send_text(output.decode(errors='replace'))
                        
                        if read_task.done():
                           break
                except Exception as e:
                    pass
                finally:
                    read_task.cancel()
                    break

        except Exception as e:
            logger.error(f"Error in terminal loop: {e}")
        finally:
            os.close(master_fd)
            # Kill the child process if it's still alive
            try:
                os.kill(pid, 15) # SIGTERM
                os.waitpid(pid, 0)
            except OSError:
                pass
