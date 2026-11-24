# How Matrices Transform Vectors
**Naman Saini · E25B070594 · Linear Algebra and Calculus (M3)**

Five-minute narrated animation on how the columns of a matrix determine the images of vectors and the coordinate grid.

## Project files

| File | Purpose |
| --- | --- |
| How_Matrices_Transform_Vectors_Video.mp4 | Final 1920 × 1080, 30 fps film with Naman’s narration and English captions |
| Documents/Storyboard.pdf | Six illustrated scenes, learning objective, visual action and mathematical plan |
| Documents/Voiceover_Script.pdf | Recording script with planned cue windows |
| Assets/English.srt | Caption text and final timing, adjusted to the recording |
| Assets/Naman_Narration.flac | Synchronized voice track used in the film |
| _Code/animate.py | Editable vector, grid, equation and scene animation |
| _Code/captions.py | Typesets the English captions above the animation |
| _Code/render.sh | Rebuilds the full MP4 using the included narration |

## Worked example

The matrix has columns (2,1) and (1,1). An input with coordinates (x,y) maps to (2x+y,x+y). The vector (1,2) therefore maps to (4,3), the sum of the first column and twice the second. The square’s opposite corner (1,1) maps to (3,2). The determinant is 2×1 − 1×1 = 1, so the transformed parallelogram has area one and preserves orientation.

## Rebuild

On a Debian or Ubuntu system, install Python 3, Pycairo, Pillow, FFmpeg with libx264, libass and AAC, and the Open Sans, Liberation Serif and DejaVu Sans Mono fonts. From the project folder run:

```sh
bash _Code/render.sh
```

The script generates frame-accurate chapter clips in build/ and writes the final MP4 in the project root. The captions are embedded in the picture. The separate SRT supports editing. The script PDF retains the original recording cues.

## Credits

Narration by Naman Saini. AI assistance was used for scripting, animation code and subtitle preparation. Assignment reference: M3 Animation Video Project Instructions. The film uses original programmatic diagrams and a voice-only soundtrack.
