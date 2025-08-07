from api.main import create_api_app

app = create_api_app()


if __name__ == "__main__":
    app.run(debug=True)
