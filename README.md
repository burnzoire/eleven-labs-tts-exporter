# ElevenLabs Text To Speach Exporter
This is a tool to automate generation of voice-overs from an input csv file. It will generate and convert files to an output folder in the format of your choosing.

## Publishing the image
1. Build the Docker image:
    ```sh
    docker build -t burnzoire/tts-exporter .
    ```
2. Publish to docker hub:
    ```sh
    docker push burnzoire/tts-exporter:latest
    ```

## Running the generate script using Docker

To execute the `generate.py` script using the Docker image `burnzoire/tts-exporter`, follow these steps:

1. Ensure you have Docker installed on your machine.
2. Run the Docker container with the necessary environment variables and input file:
    ```sh
    docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --env-file .env burnzoire/tts-exporter python generate.py input/input.csv
    ```

Make sure to replace `input.csv` with the path to your input CSV file.

## Input CSV format

The input CSV file should have the following columns:

| Column Name       | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| path              | The directory path where the generated files will be saved.                 |
| filename          | The name of the generated file (without extension).                         |
| voice_id          | The ID of the voice to be used for text-to-speech generation.               |
| input             | The text input to be converted to speech.                                   |
| generate_format   | The format of the generated audio file (e.g., `mp3_44100_128`).             |
| generate_model    | The model ID to be used for text-to-speech generation (default: `eleven_multilingual_v2`). |
| convert_format    | The format to which the generated audio file will be converted (e.g., `ogg`).|
| convert_framerate | The frame rate for the converted audio file (e.g., `22000`).                |
| convert_channels  | The number of channels for the converted audio file (e.g., `1`).            |
| normalize         | Whether to normalize the audio file (`true` or `false`).                    |
| seed              | The seed value for randomization.                                           |
| previous_text     | The previous text context (optional).                                       |
| next_text         | The next text context (optional).                                           |

Example CSV content:
```csv
path, filename, voice_id, input, generate_format, generate_model, convert_format, convert_framerate, convert_channels, normalize, seed, previous_text, next_text
voices/blackjack_11, blackjack_11, c6SfcYrb2t09NHXiT80T, "Blackjack 1 1", mp3_44100_128, eleven_multilingual_v2, ogg, 22000, 1, true, 123456,,
voices/blackjack_11, go_ahead, c6SfcYrb2t09NHXiT80T, "Go ahead.", mp3_44100_128, eleven_multilingual_v2, ogg, 22000, 1, true, 123456,,
```

