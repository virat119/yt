
import os
import random
import pytube
import cv2
import numpy as np
import ffmpeg
import whisper
import sqlite3
from datetime import datetime
from flask import Flask, request, send_from_directory, render_template, redirect, url_for

# Flask app for public link generation
app = Flask(__name__, template_folder='templates')

# SQLite database initialization
DB_PATH = "videos.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY,
            url TEXT,
            file_path TEXT,
            download_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Video download karna
def download_video(url, path='./downloads'):
    yt = pytube.YouTube(url)
    video_stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
    print(f"Downloading: {yt.title}")
    video_stream.download(output_path=path)
    return os.path.join(path, video_stream.default_filename)

# Whisper se subtitles generate karna
def generate_subtitles(video_path):
    model = whisper.load_model("base")
    result = model.transcribe(video_path)
    subtitles = []
    for segment in result['segments']:
        subtitles.append(f"{segment['start']} --> {segment['end']}\n{segment['text']}\n")
    return subtitles

# Highlights extraction
def extract_highlights(video_path):
    video = cv2.VideoCapture(video_path)
    highlights = []
    prev_frame = None

    while True:
        ret, frame = video.read()
        if not ret:
            break
        if prev_frame is not None:
            diff = cv2.absdiff(frame, prev_frame)
            non_zero_count = np.count_nonzero(diff)
            if non_zero_count > 10000:
                highlights.append(frame)
        prev_frame = frame
    video.release()
    return highlights

# Create final video
def create_final_video(video_path, output_path='./downloads'):
    output_file = os.path.join(output_path, f"final_video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4")
    os.system(f"ffmpeg -i {video_path} -t 00:01:00 -c:v copy -c:a copy {output_file}")
    return output_file

# Save video details in database
def save_to_db(url, file_path, download_link):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO videos (url, file_path, download_link)
        VALUES (?, ?, ?)
    ''', (url, file_path, download_link))
    conn.commit()
    conn.close()

# Generate public download link (Flask server)
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(directory='./downloads', path=filename, as_attachment=True)

# Homepage with form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        return redirect(url_for('process_video', url=url))
    return render_template('index.html')

# Video processing route
@app.route('/process', methods=['GET'])
def process_video():
    url = request.args.get('url')
    if not url:
        return redirect(url_for('index'))

    download_folder = './downloads'
    os.makedirs(download_folder, exist_ok=True)

    # Video download
    video_path = download_video(url, path=download_folder)

    # Subtitles generate
    generate_subtitles(video_path)

    # Highlights nikaalna
    extract_highlights(video_path)

    # Final video creation
    final_video_path = create_final_video(video_path, output_path=download_folder)

    # Generate public download link
    file_name = os.path.basename(final_video_path)
    public_link = f"http://127.0.0.1:5000/download/{file_name}"

    # Save to database
    save_to_db(url, final_video_path, public_link)

    return render_template('result.html', link=public_link)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False)
