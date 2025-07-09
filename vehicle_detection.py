import cv2
import json
import numpy as np
from shapely.geometry import Point, Polygon
from ultralytics import YOLO
import os
import streamlit as st

REGION_FILE = "regions.json"
MODEL_PATH = "yolo11m.pt"


def load_regions():
    if not os.path.exists(REGION_FILE):
        st.error(f"Regions file {REGION_FILE} not found. Please create ROI regions first.")
        return [], []

    with open(REGION_FILE, "r") as f:
        data = json.load(f)
    shapely_polys = [Polygon([(pt['x'], pt['y']) for pt in poly]) for poly in data['polygons']]
    raw_polys = data['polygons']
    return shapely_polys, raw_polys


def get_thresholds_streamlit(key_prefix="default"):
    st.header("🔧 Threshold Settings")

    car_thresh = st.number_input("Car Threshold", min_value=0, value=5, step=1, key=f"{key_prefix}_car_thresh")
    truck_thresh = st.number_input("Truck Threshold", min_value=0, value=3, step=1, key=f"{key_prefix}_truck_thresh")
    bus_thresh = st.number_input("Bus Threshold", min_value=0, value=2, step=1, key=f"{key_prefix}_bus_thresh")
    overall_thresh = st.number_input("Overall Threshold", min_value=0, value=10, step=1,
                                     key=f"{key_prefix}_overall_thresh")

    return car_thresh, truck_thresh, bus_thresh, overall_thresh


def draw_stats_box(frame, car_count, truck_count, bus_count, car_thresh, truck_thresh, bus_thresh, overall_count,
                   overall_thresh, status_text, status_color):
    box_x, box_y, box_w, box_h = 10, 10, 340, 160
    overlay = frame.copy()
    cv2.rectangle(overlay, (box_x, box_y), (box_x + box_w, box_y + box_h), (50, 50, 50), -1)
    frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

    cv2.putText(frame, f"Cars: {car_count} / {car_thresh}", (box_x + 10, box_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, f"Trucks: {truck_count} / {truck_thresh}", (box_x + 10, box_y + 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, f"Buses: {bus_count} / {bus_thresh}", (box_x + 10, box_y + 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, f"Total: {overall_count} / {overall_thresh}", (box_x + 10, box_y + 105),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, f"Status: {status_text}", (box_x + 10, box_y + 140),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
    return frame


def detect_vehicles_in_roi(video_path, scale=1.0, thresholds=None):
    """
    Detect vehicles in ROI with given thresholds - Cloud friendly version
    """
    # Load ROI regions
    rois, raw_polygons = load_regions()
    if not rois:
        return

    # Initialize YOLO model
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        st.error(f"Error loading YOLO model: {str(e)}")
        return

    vehicle_classes = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}

    # Use provided thresholds or get them from Streamlit
    if thresholds:
        car_thresh = thresholds['car_thresh']
        truck_thresh = thresholds['truck_thresh']
        bus_thresh = thresholds['bus_thresh']
        overall_thresh = thresholds['overall_thresh']
    else:
        car_thresh, truck_thresh, bus_thresh, overall_thresh = 5, 3, 2, 10

    st.write(
        f"Using thresholds - Cars: {car_thresh}, Trucks: {truck_thresh}, Buses: {bus_thresh}, Overall: {overall_thresh}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error(f"ERROR: Unable to open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * scale)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * scale)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = os.path.join(os.path.dirname(video_path), "output_result.mp4")

    # Create output video writer
    try:
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    except Exception as e:
        st.error(f"Error creating output video: {str(e)}")
        return

    frame_skip = 4
    frame_counter = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_counter += 1
            if frame_counter % frame_skip != 0:
                continue

            # Update progress
            progress = min(frame_counter / total_frames, 1.0)
            progress_bar.progress(progress)
            status_text.text(f"Processing frame {frame_counter}/{total_frames}")

            if scale != 1.0:
                frame = cv2.resize(frame, (width, height))

            # Run YOLO detection
            results = model(frame)[0]
            boxes = results.boxes.xyxy.cpu().numpy()
            class_ids = results.boxes.cls.cpu().numpy().astype(int)

            car_count = truck_count = bus_count = 0

            # Count vehicles in ROI
            for box, cls_id in zip(boxes, class_ids):
                if cls_id not in vehicle_classes:
                    continue
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                pt = Point(cx, cy)

                if any(poly.contains(pt) for poly in rois):
                    label = vehicle_classes[cls_id]
                    if label == 'car':
                        car_count += 1
                    elif label == 'truck':
                        truck_count += 1
                    elif label == 'bus':
                        bus_count += 1

            # Determine status
            overall_count = car_count + truck_count + bus_count
            status_color = (0, 255, 0)
            status_text_label = "Smooth"
            if (car_count > car_thresh or truck_count > truck_thresh or
                    bus_count > bus_thresh or overall_count > overall_thresh):
                status_color = (0, 0, 255)
                status_text_label = "Congested"

            # Draw ROI overlay
            overlay = frame.copy()
            alpha = 0.2
            for poly in raw_polygons:
                pts = np.array([[pt['x'], pt['y']] for pt in poly], np.int32).reshape((-1, 1, 2))
                cv2.fillPoly(overlay, [pts], status_color)
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

            # Draw ROI boundaries
            for poly in raw_polygons:
                pts = np.array([[pt['x'], pt['y']] for pt in poly], np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, status_color, 2)

            # Add stats box
            frame = draw_stats_box(frame, car_count, truck_count, bus_count,
                                   car_thresh, truck_thresh, bus_thresh,
                                   overall_count, overall_thresh,
                                   status_text_label, status_color)

            out.write(frame)

    except Exception as e:
        st.error(f"Error during detection: {str(e)}")
    finally:
        cap.release()
        out.release()
        progress_bar.progress(1.0)
        status_text.text("Detection completed!")

    st.success(f"✅ Output video saved to: {output_path}")

    # Offer download option
    if os.path.exists(output_path):
        with open(output_path, "rb") as f:
            st.download_button(
                label="📥 Download Result Video",
                data=f.read(),
                file_name="detection_result.mp4",
                mime="video/mp4"
            )


if __name__ == '__main__':
    st.error("This module should be imported, not run directly. Please run roi_selector.py instead.")
