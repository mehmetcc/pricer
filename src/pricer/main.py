import uvicorn

def start() -> None:
    uvicorn.run("src.pricer.routes:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()