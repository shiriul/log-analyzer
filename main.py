from fastapi import FastAPI
import typer

app = FastAPI()
cli = typer.Typer()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@cli.command()
def hello(name: str):
    print(f"Hello {name}")

if __name__ == "__main__":
    cli()
