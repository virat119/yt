
from flask import Flask, request, render_template_string
import openai
from gtts import gTTS
import subprocess
import os

app = Flask(__name__)

# OpenAI API Key
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# Step 1: Generate Scenes
def generate_scenes(story):
    prompt = f"""
    Analyze this story and break it into scenes with detailed background, characters, and actions:
    {story}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )
    scenes = response.choices[0].text.strip()
    return scenes

# Step 2: Generate Characters
def generate_characters(scene_description):
    prompt = f"""
    Analyze this scene: {scene_description}.
    Provide a detailed list of characters involved, their physical appearance, personality traits, and role in the scene.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300
    )
    return response.choices[0].text.strip()

# Step 3: Generate Voice
def generate_voice(dialogue, output_file):
    tts = gTTS(dialogue)
    tts.save(output_file)
    print(f"[INFO] Voice generated: {output_file}")

# Step 4: Dummy Background Music
def generate_background_music():
    print("[INFO] Adding dummy background music...")
    return "dummy_music.mp3"  # Placeholder for actual music file

# Step 5: Compile Final Video
def compile_video(video_files, output_file):
    with open("file_list.txt", "w") as f:
        for file in video_files:
            f.write(f"file '{file}'\n")
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "file_list.txt", "-c", "copy", output_file])
    print(f"[INFO] Final video saved as {output_file}")
    return output_file

# Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        story = request.form["story"]

        # Generate scenes
        scenes = generate_scenes(story)
        video_files = []
        characters = []

        # Process scenes
        for i, scene in enumerate(scenes.split('\n'), start=1):
            # Generate characters
            char_details = generate_characters(scene)
            characters.append(f"Scene {i} Characters:\n{char_details}")

            # Generate voice for scene
            dialogue = f"Scene {i}: {scene}"
            voice_file = f"scene_{i}_voice.mp3"
            generate_voice(dialogue, voice_file)

            # Simulate video creation (placeholder)
            video_file = f"scene_{i}.mp4"
            with open(video_file, "w") as f:  # Dummy video file
                f.write(f"Video content for {scene}")
            video_files.append(video_file)

        # Compile final video
        final_video = compile_video(video_files, "final_video.mp4")
        music_file = generate_background_music()

        # Dummy video with music output
        final_video_with_music = "final_video_with_music.mp4"

        # Render the result page
        return render_template_string(COLORFUL_HTML, video_path=final_video_with_music, characters=characters)
    return render_template_string(COLORFUL_HTML)

# Colorful HTML
COLORFUL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Story to Video Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #ff9a9e, #fad0c4);
            color: #333;
            text-align: center;
            padding: 20px;
        }
        h1 {
            color: #fff;
            text-shadow: 2px 2px 4px #000;
        }
        textarea {
            width: 80%;
            height: 200px;
            margin: 20px auto;
            padding: 10px;
            font-size: 16px;
            border-radius: 10px;
            border: 1px solid #ddd;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        video {
            margin-top: 20px;
            border: 5px solid #fff;
            border-radius: 10px;
        }
        ul {
            list-style: none;
            padding: 0;
            text-align: left;
            display: inline-block;
        }
        ul li {
            background: #fff;
            margin: 5px 0;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
        }
        a {
            display: inline-block;
            margin-top: 20px;
            text-decoration: none;
            color: #fff;
            background: #007BFF;
            padding: 10px 20px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        a:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <h1>Story to 3D HD Video Generator</h1>
    <form method="POST">
        <textarea name="story" placeholder="Enter your story here..."></textarea>
        <br>
        <button type="submit">Generate Video</button>
    </form>
    {% if video_path %}
    <h2>Your Video is Ready!</h2>
    <video width="640" height="360" controls>
        <source src="{{ video_path }}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    <br>
    <a href="{{ video_path }}" download>Download Video</a>
    <h2>Generated Characters</h2>
    <ul>
        {% for char in characters %}
        <li>{{ char }}</li>
        {% endfor %}
    </ul>
    {% endif %}
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
