from fastapi import FastAPI
from app.api.todo_routes import router as todo_router
from app.api.health_routes import router as health_routes

server_instance = None

class Server:

    def __init__(self, app: FastAPI):
        global server_instance
        self.app = app
        server_instance = self

    def start(self):
        print("Starting server...")
        self.setup_routes()
        
    def setup_routes(self):
        
        self.app.include_router(todo_router, prefix="/api/v1")
        self.app.include_router(health_routes, prefix="/api/v1")

    def stop(self):
        print("Stopping server...")
        
    @staticmethod
    def get_server_instance() -> 'Server':
        if server_instance is None:
            raise RuntimeError("Server not initialized")
        return server_instance
