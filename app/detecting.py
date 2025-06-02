import cv2
import time
import numpy as np
import os
import json
from datetime import datetime
from collections import defaultdict
from app.shared_vars import next_id
from app.calibration import calibration, convert_pixel_to_real
from app.utils import (detect_objects, get_contour_color, track_objects,
                       predict_object_position, init_json_file, 
                       update_or_append_object, load_config)


def run_detection():
    
    """
    This function calibrates the camera, create a mask and run the detection process for objects on the conveyor belt.
    The user can edit the "config.yaml" file to pass in conveyor belt parameters, camera parameters, camera stream or mp4 file path and more.
    
    The current "config.yaml" is setup for an example case in which a conveyor belt simulated on Blender is in motion transporting 5 red 
    and blue rectangular objects of differents sizes and shapes.
    """
    
    # ------------- Load config file -------------
    config = load_config("config/config.yaml")

    conveyor_belt_speed = config["conveyor_belt_speed"]
    conveyor_belt_width_real = config["conveyor_belt_width_real"]
    conveyor_belt_border_width_real = config["conveyor_belt_border_width_real"]
    ref_object_coord = config["reference_object_coordinate"]
    FPS = config["FPS"]
    delta_t = 1 / FPS
    delay = config["delay"]
    video_path = config["video_path"]
    calibration_image_path = config["calibration_image_path"]
    JSON_FILE = config["output_json"]
    
    # ------------- Calibrate the camera -------------
    
    # Get width of the image
    image = cv2.imread(calibration_image_path)
    height, width = image.shape[:2]
    # Compute the PPM
    ppm = calibration(calibration_image_path, ref_object_coord)

    # ------------- Create mask for conveyor belt region -------------
    conveyor_belt_width_pixel = conveyor_belt_width_real * ppm
    conveyor_belt_border_width_pixel = int(conveyor_belt_border_width_real * ppm)

    # Create a mask with the same size as the image
    mask = np.zeros_like(np.array(image[:,:,0]))

    # Draw a white rectangle (ROI) on the mask
    y1, y2 = 185+conveyor_belt_border_width_pixel, 185+int(conveyor_belt_width_pixel)-conveyor_belt_border_width_pixel-3
    cv2.rectangle(mask, (0, y1), (width, y2), 255, -1)  # white-filled rectangle


    # ------------- Run Detection algorithm -------------
    tracked_objects = defaultdict(lambda: {"path": [], "color": None})
    #global next_id
    next_id = 0
    
    init_json_file(JSON_FILE)
    
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, detections = detect_objects(frame, mask)
        current_objects = track_objects(frame, detections, tracked_objects)

        for obj_id, data in tracked_objects.items():
            if obj_id in current_objects:
                path = data["path"]
                color = data["color"]
                last_pos = path[-1]
                if int(frame.shape[1] / 4) < last_pos[0] <= int(3 * frame.shape[1] / 4):
                    X, Y = convert_pixel_to_real(frame, last_pos, ppm)
                    Xr = predict_object_position(X, conveyor_belt_speed, delta_t, delay)
                    update_or_append_object(JSON_FILE, obj_id, Xr, Y, color, X, last_pos[2])

                # Draw info
                cv2.circle(frame, (last_pos[0], last_pos[1]), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"ID:{obj_id} ({color})", (last_pos[0] + 10, last_pos[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        #time.sleep(0.5)
        cv2.imshow("Detection", frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
