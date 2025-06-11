# SoundScape Studio

An AI audio conversion toolkit that actually works.

Turn whistling into sheet music. Draw melodies on canvas. Convert any audio to MIDI.

## Quick Start

```bash
conda env create -f environment.yml
conda activate music-transcription
streamlit run app.py
```

## Features

- **Audio-to-MIDI**: Upload/record audio, get MIDI using Basic Pitch
- **Whistle-to-Sheet**: Whistle melodies become sheet music  
- **Draw-to-Music**: Paint sounds where X=time, Y=pitch

## Tech Stack

Streamlit + Basic Pitch + CREPE + Pretty MIDI + Librosa


