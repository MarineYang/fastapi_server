from fastapi import FastAPI
import uvicorn
from config.config import web_server_config

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(
                "router.router:app",
                host=web_server_config.host,
                port=web_server_config.port,
                access_log=False
                )
    

