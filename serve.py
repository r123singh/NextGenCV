from flask import Flask, send_from_directory, render_template_string
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:8501",  # Streamlit local
            "https://kyjmpabababjadllxtrv.supabase.co"  # Supabase domain
        ]
    }
})

@app.route('/')
def index():
    return 'Resume Viewer Server'

@app.route('/resume-viewer.html')
def resume_viewer():
    with open('resume-viewer.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Insert Supabase configuration as meta tags
    head_end = '</head>'
    supabase_meta_tags = '''
    <meta name="supabase-url" content="{}">
    <meta name="supabase-key" content="{}">
    </head>
    '''.format(
        os.getenv('SUPABASE_URL', ''),
        os.getenv('SUPABASE_KEY', '')
    )
    
    template = template.replace(head_end, supabase_meta_tags)
    return render_template_string(template)

# Called from resume-viewer.html when in development mode to fetch resume content:
# const response = await fetch(`tmp/${filename}`);
@app.route('/tmp/<path:filename>')
def serve_file(filename):
    return send_from_directory('tmp', filename)

if __name__ == '__main__':
    app.run(port=5500, debug=True) 