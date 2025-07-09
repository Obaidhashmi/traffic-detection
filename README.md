# 🚦 ROI Vehicle Detection App

A Streamlit-based application for detecting and counting vehicles within user-defined regions of interest (ROI) in video files. The app uses YOLO object detection to identify cars, trucks, and buses, and provides real-time traffic congestion analysis.

## 🌟 Features

- **Video Upload**: Support for multiple video formats (MP4, MPV, MOV, AVI, MKV, FLV, WEBM)
- **Interactive ROI Selection**: Draw custom regions of interest using OpenCV interface
- **Real-time Vehicle Detection**: Uses YOLO11 model for accurate vehicle detection
- **Traffic Congestion Analysis**: Customizable thresholds for different vehicle types
- **Visual Feedback**: Color-coded status indicators (Green = Smooth, Red = Congested)
- **Output Video Generation**: Saves processed video with detection results
      
## Dependencies
```
# Core dependencies
streamlit>=1.28.0
opencv-python-headless==4.8.1.78
numpy>=1.24.0
ultralytics>=8.0.0
shapely>=2.0.0

# Additional dependencies that might be needed
Pillow>=9.0.0
torch>=2.0.0
torchvision>=0.15.0

# For video processing
imageio>=2.25.0
imageio-ffmpeg>=0.4.8

# Optional: For better performance
psutil>=5.9.0
```

### YOLO Model
- The app uses `yolo11m.pt` model file

## 🚀 Installation
### Open pycharm or VS code command prompt
1. **Clone the repository:**
```bash
git clone https://github.com/Obaidhashmi/traffic-detection.git
```
 1.2. **selecting folder**
```
cd traffic-detection
```
2.1: **Create Virtual Environment**
### Create virtual environment
```
python -m venv traffic_detection_env
```
# Activate virtual environment
# On Windows:
```
traffic_detection_env\Scripts\activate
```
# On macOS/Linux:
```
source traffic_detection_env/bin/activate
```
2.2. **Install required packages:**
```bash
pip install -r requirments.txt
```

3. **Run the application:**
```bash
streamlit run roi_selector.py
```

## 💡 Usage

### Step 1: Upload Video
- Launch the Streamlit app
- Upload a video file using the file uploader
- Supported formats: MP4, MPV, MOV, AVI, MKV, FLV, WEBM

### Step 2: Draw ROI Regions
- Click "Select/Draw ROI" button
- A new window will open showing the first frame of your video
- **Drawing Controls:**
  - **Left Click**: Add points to create polygon
  - **Right Click**: Finish current polygon
  - **U Key**: Undo last point
  - **S Key**: Save regions and continue
  - **Q Key**: Quit without saving

### Step 3: Set Detection Thresholds
- Configure vehicle count thresholds:
  - **Car Threshold**: Maximum cars before congestion alert
  - **Truck Threshold**: Maximum trucks before congestion alert  
  - **Bus Threshold**: Maximum buses before congestion alert
  - **Overall Threshold**: Maximum total vehicles before congestion alert

### Step 4: Start Detection
- Click "🚀 Start Vehicle Detection"
- The app will process the video and generate output with:
  - Vehicle count overlay
  - ROI region highlighting
  - Congestion status indicator
  - Real-time statistics

## 📁 Project Structure

```
roi-vehicle-detection/
├── roi_selector.py          # Main Streamlit application
├── main_fixed.py           # Video upload functionality
├── vehicle_detection.py    # YOLO detection and processing
├── uploaded_videos/        # Directory for uploaded videos
├── regions.json           # Saved ROI regions data
├── yolo11m.pt            # YOLO model file (auto-downloaded)
└── README.md             # This file
```

## 🔧 Configuration Files

### regions.json
Stores ROI polygon coordinates and scale factor:
```json
{
  "scale": 1.0,
  "polygons": [
    [
      {"x": 100, "y": 200},
      {"x": 300, "y": 200},
      {"x": 300, "y": 400},
      {"x": 100, "y": 400}
    ]
  ]
}
```

## 🎯 Detection Classes

The app detects the following vehicle types:
- **Buse** (Class ID: 0) 
- **Car** (Class ID: 1)
- **Truck** (Class ID: 2)

## 📊 Output

The processed video includes:
- **Statistics Box**: Real-time vehicle counts and thresholds
- **ROI Visualization**: Highlighted regions with color coding
- **Status Indicator**: "Smooth" (Green) or "Congested" (Red)
- **Vehicle Tracking**: Bounding boxes around detected vehicles

## ⚙️ Technical Details

### Performance Optimization
- Frame skipping (processes every 4th frame)
- Automatic video scaling for large videos
- Efficient polygon-based ROI checking using Shapely

### Video Processing
- Input: Various video formats
- Output: MP4 format with detection overlay
- FPS: Maintains original video frame rate

## 🐛 Troubleshooting

### Common Issues

1. **"Could not open video" error**
   - Ensure video file is not corrupted
   - Check if video format is supported
   - Verify file permissions

2. **ROI window not opening**
   - Check if video was uploaded successfully
   - Ensure OpenCV is properly installed
   - Try with a different video file

3. **Detection not working**
   - Verify YOLO model is downloaded
   - Check internet connection for model download
   - Ensure regions.json file exists

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) for the object detection model
- [Streamlit](https://streamlit.io/) for the web interface
- [OpenCV](https://opencv.org/) for video processing
- [Shapely](https://github.com/shapely/shapely) for geometric operations

## 📧 Contact

For questions or support, please open an issue on GitHub or contact [your-email@example.com](mailto:your-email@example.com

https://github.com/user-attachments/assets/3894b5e5-aac6-409e-b917-052d1f629d71



https://github.com/user-attachments/assets/146985cb-3491-402f-8076-1c9e2e4a45e9

).

---

**Thank you for Your Time**
