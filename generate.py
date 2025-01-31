import sys
import csv
import os

from elevenlabs import ElevenLabs
from dotenv import load_dotenv
from pydub import AudioSegment

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: python generate.py <input_csv_file> [regen=true|false]")
    sys.exit(1)

input_file = sys.argv[1]
regen_arg = sys.argv[2] if len(sys.argv() == 3 else "false"
regen = "true" in regen_arg.strip().lower()

# Sanitize and resolve the input_file path
input_file = os.path.abspath(input_file)

print(f"Input file: {input_file}")
print(f"Regen: {regen}")

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    print("Please set the ELEVENLABS_API_KEY environment variable.")
    sys.exit(1)

client = ElevenLabs(api_key=api_key)

with open(input_file, mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        row = {k.strip(): v.strip() for k, v in row.items()}  # Strip whitespace from keys and values
        path = row['path']
        filename = row['filename']
        voice_id = row['voice_id']
        input_text = row['input']
        generate_format = row['generate_format']
        model_id = row.get('generate_model', 'eleven_multilingual_v2')
        convert_format = row['convert_format']
        frame_rate = int(row['convert_framerate'])
        channels = int(row['convert_channels'])
        normalize = row['normalize'].lower() == 'true'
        seed = int(row['seed'])
        previous_text = row.get('previous_text')
        next_text = row.get('next_text')

        output_path = os.path.join("output", path)
        tmp_path = os.path.join("tmp", path)
        tmp_file = os.path.join(tmp_path, filename + ".mp3")

        if os.path.exists(tmp_file) and not regen:
            print(f"Skipping {tmp_file} as it already exists and regen is not set.")
            continue

        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format=generate_format,
            text=input_text,
            model_id=model_id,
            previous_text=previous_text,
            next_text=next_text,
            seed=seed,
        )

        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

        with open(tmp_file, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)
        print(f"Generated {tmp_file}")

        # Convert to specified format
        convert_output_path = os.path.join(output_path, convert_format)
        if not os.path.exists(convert_output_path):
            os.makedirs(convert_output_path)

        convert_filename = filename + f".{convert_format}"
        convert_output_file = os.path.join(convert_output_path, convert_filename)

        audio = AudioSegment.from_mp3(tmp_file)
        audio = audio.set_frame_rate(frame_rate).set_channels(channels)
        if normalize:
            audio = audio.normalize()
        audio.export(convert_output_file, format=convert_format)
        print(f"Converted to {convert_output_file}")

        # Delete the temporary file
        os.remove(tmp_file)
        print(f"Deleted temporary file {tmp_file}")
