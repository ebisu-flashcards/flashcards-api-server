import json
from flashcards_server.main import app


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>Flashcards API - ReDoc</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
    <style data-styled="" data-styled-version="4.4.1"></style>
</head>
<body>
    <div id="redoc-container"></div>
    <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"> </script>
    <script>
        var spec = {};
        Redoc.init(spec, {{}}, document.getElementById("redoc-container"));
    </script>
</body>
</html>
"""


def generate_redoc():
    """
    Export the ReDoc documentation page into a standalone HTML file.
    """
    with open("redoc.html", "w") as fd:
        fd.write(HTML_TEMPLATE.format(json.dumps(app.openapi())))
    with open("spec.json", "w") as fd:
        json.dump(app.openapi(), fd)
