import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add API constant
content = content.replace(
    "const editorHighlight = document.getElementById('editorHighlight');",
    "const editorHighlight = document.getElementById('editorHighlight');\nconst API = location.origin || 'http://127.0.0.1:5000';"
)

# Replace hardcoded URLs
content = content.replace("fetch('http://127.0.0.1:5000/compile'", "fetch(API + '/compile'")
content = content.replace("fetch('http://127.0.0.1:5000/samples')", "fetch(API + '/samples')")
content = content.replace("fetch('http://127.0.0.1:5000/sample?name='", "fetch(API + '/sample?name='")
content = content.replace("fetch('http://127.0.0.1:5000/labels?model='", "fetch(API + '/labels?model='")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
