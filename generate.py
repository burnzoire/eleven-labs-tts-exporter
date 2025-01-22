import os
import sys
import json
import re
from elevenlabs import ElevenLabs
from dotenv import load_dotenv
from pydub import AudioSegment


def sanitize_filename(text):
    sanitized = re.sub(r"[^a-zA-Z0-9_\-]", "_", text).lower()
    return sanitized.rstrip("_")


if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: python generate.py <input_json_file> [regen=true|false]")
    sys.exit(1)

input_file = sys.argv[1]
regen_arg = sys.argv[2] if len(sys.argv) == 3 else "false"
regen = "true" in regen_arg.strip().lower()

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    print("Please set the ELEVENLABS_API_KEY environment variable.")
    sys.exit(1)

with open(input_file, "r") as f:
    data = json.load(f)

client = ElevenLabs(api_key=api_key)

generate_settings = data["voice"]["generateSettings"]
convert_settings = data["voice"]["convertSettings"]

output_path = os.path.join("output", data["voice"]["outputPath"])
generate_format = generate_settings["format"] or "mp3_44100_128"
convert_format = convert_settings["format"] or "ogg"
frame_rate = int(convert_settings["frameRate"]) or 22000
channels = int(convert_settings["channels"]) or 1
normalize = convert_settings["normalize"].lower() == "true" or True

for line in data["voice"]["lines"]:
    text = line["text"]
    previous_text = line.get("previous_text")
    next_text = line.get("next_text")
    model_id = line.get("model_id", "eleven_multilingual_v2")

    filename = sanitize_filename(text) + ".mp3"
    output_file = os.path.join(output_path, filename)

    if os.path.exists(output_file) and not regen:
        print(f"Skipping {output_file} as it already exists and regen is not set.")
        continue

    audio_generator = client.text_to_speech.convert(
        voice_id=generate_settings["voiceId"],
        output_format=generate_format,
        text=text,
        model_id=model_id,
        previous_text=previous_text,
        next_text=next_text,
        seed=generate_settings.get("seed"),
    )

    with open(output_file, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)
    print(f"Generated {output_file}")

    # Convert to specified format
    convert_output_path = os.path.join(output_path, convert_format)
    if not os.path.exists(convert_output_path):
        os.makedirs(convert_output_path)

    convert_filename = sanitize_filename(text) + f".{convert_format}"
    convert_output_file = os.path.join(convert_output_path, convert_filename)

    audio = AudioSegment.from_mp3(output_file)
    audio = audio.set_frame_rate(frame_rate).set_channels(channels)
    if normalize:
        audio = audio.normalize()
    audio.export(convert_output_file, format=convert_format)
    print(f"Converted to {convert_output_file}")
