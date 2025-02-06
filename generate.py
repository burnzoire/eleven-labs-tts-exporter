import sys
import csv
import os
from datetime import datetime

from elevenlabs import ElevenLabs
from dotenv import load_dotenv
from pydub import AudioSegment

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: python generate.py <input_csv_file> [regen=true|false]")
    sys.exit(1)

input_file = sys.argv[1]
regen_arg = sys.argv[2] if len(sys.argv) == 3 else "regen=false"
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

report = []

# Function to find an entry by path in the report
def find_entry_by_path(report, path):
    for entry in report:
        if entry['path'] == path:
            return entry
    return None

# Define constants for generate_format and model_id
GENERATE_FORMAT = "mp3_44100_128"
MODEL_ID = "eleven_multilingual_v2"

with open(input_file, mode='r') as file:
    csv_reader = csv.DictReader(file, delimiter=',', quotechar='"', escapechar='\\', quoting=csv.QUOTE_ALL, skipinitialspace=True)
    for row in csv_reader:
        try:
            path = row['path']
            filename = row['filename']
            voice_id = row['voice_id']
            input_text = row['input']
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

            # Convert to specified format
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            convert_filename = filename + f".{convert_format}"
            convert_output_file = os.path.join(output_path, convert_filename)

            # Check if the final converted file exists
            if os.path.exists(convert_output_file) and not regen:
                print(f"Skipping {convert_output_file} as it already exists and regen is not set.")
                continue

            audio_generator = client.text_to_speech.convert(
                voice_id=voice_id,
                output_format=GENERATE_FORMAT,
                text=input_text,
                model_id=MODEL_ID,
                previous_text=previous_text,
                next_text=next_text,
                seed=seed,
            )

            if not os.path.exists(tmp_path):
                os.makedirs(tmp_path)

            with open(tmp_file, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

            audio = AudioSegment.from_mp3(tmp_file)
            audio = audio.set_frame_rate(frame_rate).set_channels(channels)
            if normalize:
                audio = audio.normalize()
            audio.export(convert_output_file, format=convert_format)

            # Store the duration and path in the report
            duration = round(audio.duration_seconds, 2)
            oggfile = os.path.join(path, convert_filename)
            existing_entry = find_entry_by_path(report, oggfile)
            if existing_entry:
                existing_entry.update({
                    "duration": duration,
                })
            else:
                report.append({
                    "path": oggfile,
                    "duration": duration,
                })

            # Delete the temporary file
            os.remove(tmp_file)

            print(f"Generated {convert_output_file}")
        except Exception as e:
            print(f"Error processing row: {row}")
            print(f"Exception: {e}")

# Function to read the existing report
def read_existing_report(report_file):
    if not os.path.exists(report_file):
        return []
    with open(report_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        return list(csv_reader)

# Save the report to a CSV file alongside the input file
input_file_name = os.path.basename(input_file)
report_file = os.path.join("input", os.path.splitext(input_file_name)[0] + "_output.csv")

# Read the existing report
existing_report = read_existing_report(report_file)

# Merge the new report with the existing report
for new_entry in report:
    existing_entry = find_entry_by_path(existing_report, new_entry['path'])
    if existing_entry:
        existing_entry.update(new_entry)
    else:
        existing_report.append(new_entry)

with open(report_file, "w", newline='') as f:
    csv_writer = csv.DictWriter(f, fieldnames=["path", "duration"])
    csv_writer.writeheader()
    csv_writer.writerows(existing_report)
print(f"Report saved to {report_file}")
