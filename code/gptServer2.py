from flask import Flask, request, render_template_string
from urllib.parse import parse_qs, unquote

app = Flask(__name__)

# Example HTML template with potential XSS vulnerability
html_template = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>XSS Simulation</title>
  </head>
  <body>
    <h1>XSS Simulation</h1>
    <form method="post" action="/submit">
      <label for="input">Enter something:</label>
      <input type="text" id="input" name="input">
      <button type="submit">Submit</button>
    </form>
    <h2>Submitted Value</h2>
    <div>{}</div>
  </body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template.format(""))

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        # Get the raw bytes from the request body
        raw_data = request.get_data()
    elif request.method == 'GET':
        # Get the raw bytes from the query string
        raw_data = request.query_string
    
    # Decode the raw bytes to a string
    raw_data_str = raw_data.decode('utf-8')
    
    # Assuming the raw data is URL-encoded form data like "input=value"
    # Extract the user input value
    parsed_data = parse_qs(raw_data_str)
    
    # This assumes the form field is named 'input'
    user_input = parsed_data.get('input', [''])[0]
    
    # Decode any URL-encoded characters in the input
    user_input_decoded = unquote(user_input)
    
    # Render the user input directly (XSS vulnerability)
    return render_template_string(html_template.format(user_input_decoded))

if __name__ == '__main__':
    app.run(debug=True)
