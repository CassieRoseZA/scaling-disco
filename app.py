from flask import Flask, send_from_directory, request, jsonify, make_response
import os
import pandas as pd
from io import BytesIO

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/upload', methods=['POST'])
def upload_log():
    if 'logfile' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['logfile']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.log'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        with open(file_path, 'r') as f:
            log_contents = f.read()
        
        return jsonify({"analysis": f"Log file analyzed with {len(log_contents)} characters.", "file_path": file_path})
    else:
        return jsonify({"error": "File type not allowed"}), 400

@app.route('/api/view_log', methods=['POST'])
def view_log():
    file_path = request.json.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    with open(file_path, 'r') as f:
        log_contents = f.read()

    return jsonify({"log_contents": log_contents})

@app.route('/api/export', methods=['POST'])
def export_log():
    file_path = request.json.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    with open(file_path, 'r') as f:
        log_contents = f.readlines()

    df = pd.DataFrame({'Log': log_contents})
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Logs')
    writer.save()
    output.seek(0)

    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=logfile.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response

@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory('.', '404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=10000)
