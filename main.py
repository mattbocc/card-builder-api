from fastapi import FastAPI
from routes.poke import router as poke_router

app = FastAPI()
app.router
app.include_router(poke_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
