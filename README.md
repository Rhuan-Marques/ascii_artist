# Ascii Artist

This is a python tool that converts images and video files into ASCII art, with possibly subtitles or headers and tons of other options

---

## Features

- **Image to ASCII Conversion:** Transform any image into a detailed ASCII art representation.
- **Video Processing:** Extract frames from video files (e.g., `.mp4`, `.avi`, `.gif`) and convert them into ASCII art.
- **Color Mode:** Generate colored ASCII art using ANSI escape codes for true color output.
- **Custom Text Addition:** Dynamically add custom text to the top and/or bottom of the image.
- **Adjustable Parameters:** Customize output with adjustable width, contrast, brightness, pixel density, and more.
- **Frame Control for Videos:** Skip frames, control playback speed, and set repeat modes for video conversion.
- **Cross-Platform Font Handling:** Supports default fonts on both Unix-based systems and Windows (with configurable font path).

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Rhuan-Marques/ascii_artist.git
   cd AsciiArtist
   ```

2. **Install Dependencies:**

    Inside the clonned repository, install the dependencies of the project.
    Ensure you have Python 3 installed.
    Reccomended using Poetry or a venv
   
    **With Poetry**:
    ```bash
    poetry install
    ```

    **Without Poetry**:
        
    Check `pyproject.toml` file.
    On the area `dependencies` use pip to install each of the packages.
        
    Example:
    ```bash
    pip install pillow opencv-python pydantic
    ``` 

---

## Usage

Run the script from the command line by specifying the file to convert along with any optional parameters:

```bash
python main.py <filepath> [--width WIDTH] [--contrast FACTOR] [--brightness FACTOR] [--pixel_density DENSITY] [--text_above TEXT] [--text_below TEXT] [--skip_frames FRAMES] [--repeat REPEAT] [--time_between_frames SECONDS] [--color] [--inverse] [--font_path PATH] [--text_margin MARGIN]
```

Note: If using poetry or a venv, python should reffer to the python inside the environment


## Command-line Arguments
| Argument               | Description | Default |
|------------------------|-------------|----------
| `filepath`             | **Required**. Path to the image or video file | |
| `--width`             | Width of the ASCII output in character number. Height will be based on this number by keeping the original ratio | 100 |
| `--contrast`         | Contrast adjustment factor | 1.0 |
| `--brightness`       | Brightness adjustment factor | 1.0 |
| `--pixel_density`    | Shifts the ascii character choice by pixel brightness. A high pixel density means the image will have more bigger characters like `@` and `#`. Low pixel density means the image will have more small characters like `;` and `.`. Range: (-255, 255) | 0 |
| `--text_above`       | Text to display above the image. Width based on the `--width` argument, height based on the width and font | null |
| `--text_below`       | Text to display below the image. Width based on the `--width` argument, height based on the width and font | null |
| `--skip_frames`      | Frames to skip in video processing. For long or high frame-rate videos, can be used to make the animmations choppier and run them better | 0 |
| `--repeat`           | Number of times to repeat a video (-1 for infinite) | 1 |
| `--time_between_frames` | Time delay between video frames in seconds | 0.15 |
| `--color`            | Enables colored ASCII output |  |
| `--inverse`          | Inverts ASCII brightness mapping. Usefull if terminal (or target use for the ascii) has a bright background on dark text |  |
| `--font_path`        | Path to a custom font file | Windows: Arial Bold. Other: NotoSansCJK-Bold | 
| `--text_margin`      | Margin around text overlay (in pixels)| 10 |

