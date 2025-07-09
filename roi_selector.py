import cv2
import json
import numpy as np
import os
from main_fixed import upload_and_save_video
import streamlit as st
from vehicle_detection import detect_vehicles_in_roi

REGION_FILE = "regions.json"
tmp_points = []
polygons = []
scale = 1.0  # scale factor


# Save polygons and scale to JSON
def save_regions():
    data = {
        "scale": scale,
        "polygons": [
            [{"x": int(x), "y": int(y)} for x, y in poly]
            for poly in polygons
        ]
    }
    with open(REGION_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Saved {len(polygons)} region(s) to {REGION_FILE} with scale={scale}")


# Draw saved and in-progress polygons
def draw_overlays(frame):
    for poly in polygons:
        pts = np.array(poly, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
    if tmp_points:
        pts = np.array(tmp_points, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=False, color=(0, 0, 255), thickness=1)
        for x, y in tmp_points:
            cv2.circle(frame, (x, y), radius=3, color=(0, 0, 255), thickness=-1)


# Mouse callback
def mouse_callback(event, x, y, flags, param):
    global tmp_points, polygons
    if event == cv2.EVENT_LBUTTONDOWN:
        tmp_points.append((x, y))
    elif event == cv2.EVENT_RBUTTONDOWN:
        if len(tmp_points) >= 3:
            polygons.append(tmp_points.copy())
            print(f"[+] Region #{len(polygons)} saved ({len(tmp_points)} points)")
        tmp_points = []


def draw_roi_regions(VIDEO_PATH):
    """Function to handle ROI drawing - Modified for cloud deployment"""
    global scale

    # Show warning about ROI drawing in cloud environment
    st.warning("⚠️ ROI Drawing requires a local environment with display capabilities. "
               "This feature may not work on Streamlit Cloud.")

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        st.error("ERROR: Could not open video.")
        return False

    ret, frame = cap.read()
    cap.release()
    if not ret:
        st.error("ERROR: Could not read video frame.")
        return False

    # Show the first frame in Streamlit
    st.image(frame, caption="First frame of video", channels="BGR")

    # For cloud deployment, provide alternative method
    st.info("💡 **Alternative for Cloud Deployment:**\n"
            "1. Download and run this app locally for ROI drawing\n"
            "2. Or manually create regions.json with your ROI coordinates\n"
            "3. Upload the regions.json file to your project")

    # Try to use cv2.namedWindow (will fail in cloud but work locally)
    try:
        # Determine scaling if video is too large
        max_width = 1280
        max_height = 720
        height, width = frame.shape[:2]
        scale_x = max_width / width
        scale_y = max_height / height
        scale = min(1.0, scale_x, scale_y)

        if scale < 1.0:
            frame = cv2.resize(frame, (int(width * scale), int(height * scale)))

        window_name = "Draw Regions (L-click add, R-click finish, U=undo, S=save, Q=quit)"
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, mouse_callback)

        while True:
            display_frame = frame.copy()
            draw_overlays(display_frame)
            cv2.imshow(window_name, display_frame)
            key = cv2.waitKey(10) & 0xFF

            if key == ord('u'):
                if tmp_points:
                    tmp_points.pop()
            elif key == ord('s'):
                if tmp_points and len(tmp_points) >= 3:
                    polygons.append(tmp_points.copy())
                save_regions()
                cv2.destroyAllWindows()
                return True  # ROI saved successfully
            elif key == ord('q'):
                print("Exiting without saving.")
                cv2.destroyAllWindows()
                return False

    except Exception as e:
        st.error(f"ROI drawing not available in this environment: {str(e)}")
        st.info("Please run locally or provide a pre-made regions.json file")
        return False

    return False


# Main flow
def main():
    global scale

    # Step 1: Upload video
    VIDEO_PATH = upload_and_save_video()

    if VIDEO_PATH is None:
        return

    # Check if regions.json already exists
    if os.path.exists(REGION_FILE):
        st.success("✅ ROI regions file found!")
        st.session_state.roi_completed = True

        # Show option to redraw ROI
        if st.button("🔄 Redraw ROI Regions"):
            st.session_state.roi_completed = False
    else:
        st.session_state.roi_completed = False

    # Step 2: Draw ROI regions or upload regions file
    if not st.session_state.get('roi_completed', False):
        st.markdown("### Step 1: Define ROI Regions")

        # Option 1: Draw ROI (for local use)
        if st.button("🎨 Draw ROI Regions (Local Only)"):
            roi_success = draw_roi_regions(VIDEO_PATH)
            if roi_success:
                st.session_state.roi_completed = True
                st.success("✅ ROI regions saved successfully!")
            else:
                st.error("❌ ROI selection failed or cancelled.")

        # Option 2: Upload regions.json file
        st.markdown("**OR**")
        uploaded_regions = st.file_uploader(
            "Upload regions.json file",
            type=['json'],
            help="Upload a pre-made regions.json file with ROI coordinates"
        )

        if uploaded_regions is not None:
            try:
                # Save uploaded regions file
                with open(REGION_FILE, "wb") as f:
                    f.write(uploaded_regions.read())
                st.success("✅ Regions file uploaded successfully!")
                st.session_state.roi_completed = True
            except Exception as e:
                st.error(f"Error uploading regions file: {str(e)}")

    # Step 3: Get thresholds (only show if ROI is completed)
    if st.session_state.get('roi_completed', False):
        st.markdown("---")
        st.markdown("### Step 2: Set Detection Thresholds")

        # Get thresholds from user
        from vehicle_detection import get_thresholds_streamlit
        car_thresh, truck_thresh, bus_thresh, overall_thresh = get_thresholds_streamlit(key_prefix='main_detection')

        # Step 4: Start detection
        if st.button("🚀 Start Vehicle Detection"):
            st.info("Starting vehicle detection... This may take a while.")

            # Store thresholds in session state to pass to detection function
            st.session_state.thresholds = {
                'car_thresh': car_thresh,
                'truck_thresh': truck_thresh,
                'bus_thresh': bus_thresh,
                'overall_thresh': overall_thresh
            }

            # Call detection function
            try:
                detect_vehicles_in_roi(VIDEO_PATH, scale, st.session_state.thresholds)
                st.success("✅ Detection completed! Check the output video file.")
            except Exception as e:
                st.error(f"Detection failed: {str(e)}")


if __name__ == '__main__':
    main()
