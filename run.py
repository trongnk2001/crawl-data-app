from app import create_app
from db import Base, engine

app = create_app()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)
