# 🎵 Image to Custom-Shaped Audio Waveform Generator

Convert the **shape of a transparent PNG image into an audio waveform**.  
You can literally *"draw your sound."*

It comes with two versions:
- 🖥 **Graphical User Interface (GUI)** — for easy, interactive use  
- 💻 **Command-Line Interface (CLI)** — for automation and scripting

The output is a `.wav` file that, when viewed in an audio editor, will visually match the shape of the input image.

---

## 🚀 Installation

This project uses a few common Python libraries for image and audio processing.  
after installing python & pip on your system, you can install them using **pip**:

```bash
pip install pillow numpy scipy
```

---

## 🧠 How to Use

### 1️⃣ GUI Version

The easiest way to use the tool is with the graphical interface.

Run the UI script from your terminal:

```bash
python waveform_generator_ui.py
```

#### Steps:

- **Select PNG Image:** Click the first button to choose your transparent `.png` file.  
- **Set Output Path:** Click the second button to decide where to save the resulting `.wav` file.  
- **Tweak Parameters:** Use the sliders to adjust the sound:  
  - **Carrier Frequency:** Controls the pitch of the sound. Lower values are more “bassy” but create a less dense visual waveform.  
  - **Samples per Pixel:** Controls the duration of the audio. Higher values “stretch” the sound out, giving a low-frequency wave more time to be drawn, resulting in a clearer shape.  
- **Generate:** Click the “Generate Waveform” button to create the audio file.

---

### 2️⃣ Console Version

For scripting or command-line use, the `shape_to_waveform.py` script is available.

#### Basic Usage

```bash
python shape_to_waveform.py path/to/your/logo.png
```

This will create `logo.wav` in the same directory using the default settings.

#### Advanced Usage (Tweaking Parameters)

You can control the frequency and duration using command-line flags:

```bash
python shape_to_waveform.py <input_file.png> -f <freq> -s <samples> -o <output_file.wav>
```

| Flag | Description | Default |
|------|--------------|----------|
| `-f`, `--freq` | Sets the carrier frequency in Hz | 880 |
| `-s`, `--samples` | Sets the samples per pixel | 100 |
| `-o`, `--output` | Sets a custom path for the output file | _same as input_ |

#### Example (bassy sound with a clear shape)

```bash
python shape_to_waveform.py my_logo.png -f 110 -s 800 -o bassy_logo.wav
```

---

## 💡 Inspiration

This technique was pioneered by the **electronic music producer SOLTAN**.  
He is known for ending his songs with audio waveforms shaped like a heart, his name ("SOLTAN"), machine guns, and other fun visuals that are visible when the audio file is analyzed.

This project is an **homage to that creative sound design.**

---
