# Continuous Video Recorder

This Python script continuously records 1-minute videos at 30fps from an external camera and manages storage by automatically deleting old videos when the folder exceeds 2GB.

## Features

- Records videos in 1-minute segments at 30fps
- Automatically manages storage by deleting oldest videos first when the 2GB limit is reached
- Timestamps each video file for easy organization
- Configurable camera ID, resolution, and output directory

## Requirements

- Python 3.12
- OpenCV (opencv-python)

## Setup

1. Make sure you have Python 3.12 installed
2. Set up the virtual environment using the provided batch script:
   ```
   0_setup_venv.bat
   ```
3. Activate the virtual environment:
   ```
   call .venv\Scripts\activate
   ```

## Usage

**Important**: You must activate the virtual environment before running the script to ensure all required packages (like OpenCV) are available:

```
call .venv\Scripts\activate
```

Then run the script with:

```
python continuous_recorder.py
```

The script will:
1. Create a `recorded_videos` directory if it doesn't exist
2. Start recording 1-minute video segments continuously
3. Monitor the storage usage and delete old videos when it exceeds 2GB
4. Continue recording until interrupted with Ctrl+C

## Configuration

You can modify the following parameters in the `main()` function:

- `camera_id`: ID of the camera device (default: 0)
- `output_dir`: Directory to save recorded videos (default: "recorded_videos")
- `duration`: Duration of each video in seconds (default: 60)
- `resolution`: Video resolution (width, height) (default: 1920x1080)
- `fps`: Frames per second (default: 30)
- `max_storage_gb`: Maximum storage in GB (default: 2)

## Notes

- Not all cameras support setting a specific FPS. The script will try to maintain the target FPS using timing controls.
- The actual resolution may differ from the requested resolution depending on what the camera supports.
- Videos are saved in MP4 format with filenames based on the recording timestamp.
