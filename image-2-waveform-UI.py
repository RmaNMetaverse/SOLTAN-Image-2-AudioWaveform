import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image
import scipy.io.wavfile as wavfile
import os
import threading
import webbrowser

# --- Core Waveform Generation Logic ---
# This is the same powerful logic from the original script, adapted for the UI.

def create_waveform_from_image(input_image_path, output_wav_path, carrier_freq, samples_per_pixel, update_status_callback):
    """
    Generates a .wav file where the waveform's envelope matches the
    shape of a transparent PNG image.
    Args:
        input_image_path (str): Path to the source PNG.
        output_wav_path (str): Path to save the destination WAV.
        carrier_freq (float): The frequency of the carrier sine wave.
        samples_per_pixel (int): Controls the duration/stretch of the audio.
        update_status_callback (function): A function to call to update the UI's status bar.
    """
    try:
        update_status_callback("Loading image...")
        # Open the image and ensure it has an Alpha (transparency) channel
        img = Image.open(input_image_path).convert('RGBA')
        width, height = img.size
        pixels = img.load()
    except Exception as e:
        messagebox.showerror("Error", f"Could not open image file: {e}")
        update_status_callback("Ready.")
        return

    update_status_callback("Scanning image and extracting envelope...")
    top_envelope = []
    bottom_envelope = []
    
    alpha_threshold = 128

    # Scan each vertical column of pixels to find the top and bottom of the shape
    for x in range(width):
        top_y, bottom_y = -1, -1
        # Scan from top to bottom
        for y in range(height):
            if pixels[x, y][3] > alpha_threshold:
                top_y = y
                break
        # If the column wasn't empty, scan from bottom to top
        if top_y != -1:
            for y in range(height - 1, top_y - 1, -1):
                if pixels[x, y][3] > alpha_threshold:
                    bottom_y = y
                    break
        
        # Convert pixel coordinates to audio amplitude (-1.0 to 1.0)
        if top_y == -1 or bottom_y == -1:
            top_amp, bottom_amp = 0.0, 0.0
        else:
            top_amp = 1.0 - (2.0 * top_y / height)
            bottom_amp = 1.0 - (2.0 * bottom_y / height)
            
        top_envelope.append(top_amp)
        bottom_envelope.append(bottom_amp)

    update_status_callback("Generating audio samples... This may take a moment.")
    
    sample_rate = 44100
    total_samples = width * samples_per_pixel
    audio_data = np.zeros(total_samples, dtype=np.float32)

    # Generate the audio wave, modulating it to fit inside the shape's envelope
    for i in range(total_samples):
        time = i / sample_rate
        x = i // samples_per_pixel
        
        top_amp, bottom_amp = top_envelope[x], bottom_envelope[x]

        carrier = np.sin(2 * np.pi * carrier_freq * time)
        
        center = (top_amp + bottom_amp) / 2.0
        radius = (top_amp - bottom_amp) / 2.0
        
        audio_data[i] = center + (carrier * radius)

    update_status_callback("Saving audio file...")
    try:
        # Convert float samples to 16-bit integers for the WAV file
        int_data = np.int16(audio_data * 32767)
        wavfile.write(output_wav_path, sample_rate, int_data)
        update_status_callback(f"Done! Saved to {os.path.basename(output_wav_path)}")
        messagebox.showinfo("Success", f"Waveform successfully generated!\nSaved to: {output_wav_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save .wav file: {e}")
        update_status_callback("Error saving file.")

# --- GUI Application Class ---

class WaveformApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG to Waveform Generator")
        self.root.geometry("550x450")
        self.root.minsize(550, 450)

        # --- Application State Variables ---
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.carrier_freq = tk.DoubleVar(value=880)
        self.samples_per_pixel = tk.IntVar(value=200)
        self.status_text = tk.StringVar(value="Ready. Select a PNG image to start.")
        
        # --- UI Layout ---
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- File Selection Section ---
        file_frame = ttk.LabelFrame(main_frame, text="1. File Paths", padding=10)
        file_frame.pack(fill=tk.X, pady=10)

        ttk.Button(file_frame, text="Select PNG Image...", command=self.select_input_file).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(file_frame, textvariable=self.input_path, wraplength=350, foreground="blue").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(file_frame, text="Set Output WAV Path...", command=self.select_output_file).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(file_frame, textvariable=self.output_path, wraplength=350, foreground="blue").grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        file_frame.columnconfigure(1, weight=1)

        # --- Parameter Sliders Section ---
        param_frame = ttk.LabelFrame(main_frame, text="2. Tweak Parameters", padding=10)
        param_frame.pack(fill=tk.X, pady=10)

        # Carrier Frequency Slider
        ttk.Label(param_frame, text="Carrier Frequency (Hz):").grid(row=0, column=0, sticky="w")
        self.freq_slider = ttk.Scale(param_frame, from_=20, to=2000, orient=tk.HORIZONTAL, variable=self.carrier_freq, command=self.update_freq_label)
        self.freq_slider.grid(row=0, column=1, sticky="ew", padx=10)
        self.freq_label = ttk.Label(param_frame, text=f"{self.carrier_freq.get():.0f} Hz", width=10)
        self.freq_label.grid(row=0, column=2)

        # Samples per Pixel Slider
        ttk.Label(param_frame, text="Samples per Pixel:").grid(row=1, column=0, sticky="w")
        self.samples_slider = ttk.Scale(param_frame, from_=10, to=2000, orient=tk.HORIZONTAL, variable=self.samples_per_pixel, command=self.update_samples_label)
        self.samples_slider.grid(row=1, column=1, sticky="ew", padx=10)
        self.samples_label = ttk.Label(param_frame, text=f"{self.samples_per_pixel.get()}", width=10)
        self.samples_label.grid(row=1, column=2)
        
        param_frame.columnconfigure(1, weight=1)

        # --- Generation Button ---
        self.generate_button = ttk.Button(main_frame, text="Generate Waveform", command=self.start_generation)
        self.generate_button.pack(pady=20, ipady=10, fill=tk.X)

        # --- Status Bar ---
        status_bar = ttk.Frame(root, relief=tk.SUNKEN, padding=2)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(status_bar, textvariable=self.status_text).pack(side=tk.LEFT)

        # --- "Inspired by" Link ---
        def open_soltan_link(event):
            webbrowser.open_new_tab("https://www.google.com/search?q=SOLTAN+Music")

        inspired_label = ttk.Label(root, text="Inspired by SOLTAN", foreground="cornflowerblue", cursor="hand2")
        inspired_label.pack(side=tk.BOTTOM, pady=2)
        inspired_label.bind("<Button-1>", open_soltan_link)

    def select_input_file(self):
        path = filedialog.askopenfilename(
            title="Select a transparent PNG file",
            filetypes=(("PNG files", "*.png"), ("All files", "*.*"))
        )
        if path:
            self.input_path.set(os.path.basename(path))
            self._full_input_path = path # Store full path internally
            
            # Suggest an output path if one isn't already set
            if not self.output_path.get():
                base_name = os.path.splitext(path)[0]
                suggested_out = f"{base_name}.wav"
                self.output_path.set(os.path.basename(suggested_out))
                self._full_output_path = suggested_out

    def select_output_file(self):
        path = filedialog.asksaveasfilename(
            title="Save WAV file as...",
            defaultextension=".wav",
            initialfile=self.output_path.get(),
            filetypes=(("WAV files", "*.wav"), ("All files", "*.*"))
        )
        if path:
            self.output_path.set(os.path.basename(path))
            self._full_output_path = path # Store full path internally

    def update_freq_label(self, value):
        self.freq_label.config(text=f"{float(value):.0f} Hz")
        
    def update_samples_label(self, value):
        self.samples_label.config(text=f"{int(float(value))}")

    def update_status(self, message):
        self.status_text.set(message)
        
    def start_generation(self):
        # --- Validation before starting ---
        if not hasattr(self, '_full_input_path') or not self._full_input_path:
            messagebox.showwarning("Input Missing", "Please select a PNG image first.")
            return
        if not hasattr(self, '_full_output_path') or not self._full_output_path:
            messagebox.showwarning("Output Missing", "Please set an output path for the WAV file.")
            return
            
        self.generate_button.config(state=tk.DISABLED, text="Generating...")
        
        # Run the lengthy generation task in a separate thread to keep the UI responsive
        generation_thread = threading.Thread(
            target=self.run_generation_thread,
            daemon=True # Allows the app to exit even if the thread is running
        )
        generation_thread.start()

    def run_generation_thread(self):
        try:
            create_waveform_from_image(
                self._full_input_path,
                self._full_output_path,
                self.carrier_freq.get(),
                self.samples_per_pixel.get(),
                self.update_status
            )
        finally:
            # Re-enable the button once done, whether it succeeded or failed
            self.generate_button.config(state=tk.NORMAL, text="Generate Waveform")


if __name__ == "__main__":
    root = tk.Tk()
    app = WaveformApp(root)
    root.mainloop()

