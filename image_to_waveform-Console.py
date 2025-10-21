import numpy as np
from PIL import Image
import scipy.io.wavfile as wavfile
import sys
import os
import argparse

def create_waveform_from_image(input_image_path, output_wav_path, carrier_freq, samples_per_pixel):
    """
    Generates a .wav file where the waveform's envelope matches the
    shape of a transparent PNG image.
    """
    print(f"Loading image: {input_image_path}")
    try:
        img = Image.open(input_image_path).convert('RGBA')
        width, height = img.size
        pixels = img.load()
    except Exception as e:
        print(f"Error: Could not open image file. {e}")
        return

    print("Scanning image and extracting audio envelope...")
    top_envelope = []
    bottom_envelope = []
    alpha_threshold = 128

    for x in range(width):
        top_y, bottom_y = -1, -1
        for y in range(height):
            if pixels[x, y][3] > alpha_threshold:
                top_y = y
                break
        if top_y != -1:
            for y in range(height - 1, top_y - 1, -1):
                if pixels[x, y][3] > alpha_threshold:
                    bottom_y = y
                    break

        if top_y == -1 or bottom_y == -1:
            top_amp, bottom_amp = 0.0, 0.0
        else:
            top_amp = 1.0 - (2.0 * top_y / height)
            bottom_amp = 1.0 - (2.0 * bottom_y / height)
            
        top_envelope.append(top_amp)
        bottom_envelope.append(bottom_amp)

    print("Envelope extracted. Generating audio samples...")
    
    sample_rate = 44100
    total_samples = width * samples_per_pixel
    audio_data = np.zeros(total_samples, dtype=np.float32)

    for i in range(total_samples):
        time = i / sample_rate
        x = i // samples_per_pixel
        
        top_amp, bottom_amp = top_envelope[x], bottom_envelope[x]
        carrier = np.sin(2 * np.pi * carrier_freq * time)
        center = (top_amp + bottom_amp) / 2.0
        radius = (top_amp - bottom_amp) / 2.0
        audio_data[i] = center + (carrier * radius)

    print(f"Audio generated. Saving to {output_wav_path}...")
    try:
        int_data = np.int16(audio_data * 32767)
        wavfile.write(output_wav_path, sample_rate, int_data)
        print("Done.")
    except Exception as e:
        print(f"Error: Could not save .wav file. {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a transparent PNG's shape into an audio waveform.")
    parser.add_argument("input_file", type=str, help="The path to the input PNG file.")
    parser.add_argument("-f", "--freq", type=float, default=880.0, help="Carrier frequency in Hz for the sine wave. Default is 880.")
    parser.add_argument("-s", "--samples", type=int, default=100, help="Samples per pixel, controls audio duration. Default is 100.")
    parser.add_argument("-o", "--output", type=str, help="Optional: Path for the output WAV file. Defaults to the input filename with a .wav extension.")
    
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: File not found at '{args.input_file}'")
        sys.exit(1)
        
    if not args.input_file.lower().endswith('.png'):
        print("Error: Input file must be a .png file.")
        sys.exit(1)
        
    output_path = args.output
    if not output_path:
        base_name = os.path.splitext(args.input_file)[0]
        output_path = f"{base_name}.wav"
    
    create_waveform_from_image(args.input_file, output_path, args.freq, args.samples)
