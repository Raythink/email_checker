from app import create_app, db, app
from config import Config

app = create_app(Config)


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
