from fastapi import FastAPI

app = FastAPI(title="Content Machine")


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}
