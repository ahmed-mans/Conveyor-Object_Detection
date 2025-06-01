import cv2
import numpy as np
import os
import yaml
from datetime import datetime
import json
from app.shared_vars import next_id
        
def load_config(config_file):
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"[ERROR] Configuration file '{config_file}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"[ERROR] Failed to parse YAML file '{config_file}': {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error while loading config: {e}")
        return None

def init_json_file(JSON_FILE):
    """Initialize the JSON file with an empty list if it doesn't exist."""
    
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)
    
    with open(JSON_FILE, 'w') as f:
        json.dump([], f)  # Start with empty list   
        

def detect_objects(frame, mask):
    
    """
    This function takes the current frame as input and outputs data about all detected objects in the frame.

    Args:
        frame (np.ndarray):             currrent frame of the conveyor belt with objects.
        mask (np.array) :               Binary image to apply to the frame to focus only on the conveyor belt region
    Returns:
        frame (np.ndarray):             currrent frame of the conveyor belt with objects.
        detections (list of tuple) :    list of tuples containing an object's center position, contour and angle
    """
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Apply the mask
    masked_thresh = cv2.bitwise_and(gray, mask)

    # Threshold the image to binary
    _, thresh = cv2.threshold(masked_thresh, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detections = []
    
    for cnt in contours:
        
        if cv2.contourArea(cnt) > 100:  # Filter small noise
            
            
            # Detect center and angle of the object with respect to the horizontal
            (x, y), (width, height), angle = cv2.minAreaRect(cnt)  # Returns (center, (width, height), angle)
            
            corrected_angle = angle + 90 if width < height else angle
            # Correct the angle for the robotic arm
            if  90 < corrected_angle <= 180:
                corrected_angle = 180 - corrected_angle
                
            corrected_angle = round(corrected_angle, 1)    
            detections.append((int(x), int(y), cnt, corrected_angle))  # Store contour for color analysis
                
            
    return frame, detections

def get_contour_color(frame, contour):
    
    """
    This function outputs the color of the detected object.

    Args:
        frame (np.ndarray):             currrent frame of the conveyor belt with objects.
        contour (list of np.ndarray) :  list of all the contours (numpy array of (x,y) coordinates of boundary points) of the object in the image.

    Returns:
        str:    color of the object ("Red" or "Blue" or "Unknown" if neither blue of red).
    """
    
    # Create a mask using the contour to extract the object detected from the frame
    mask = np.zeros_like(frame[:, :, 0])  # Create a blank mask
    cv2.drawContours(mask, [contour], -1, 255, -1)  # Draw filled contour
    
    # Calculate mean BGR color inside the contour
    mean_color = cv2.mean(frame, mask=mask)[:3]  # Returns (B, G, R)
    
    # Classify as red or blue (adjust thresholds as needed)
    B, G, R = mean_color
    if R > B * 1.2:  # Red if R is 20% higher than B
        return "Red"
    elif B > R * 1.2:  # Blue if B is 20% higher than R
        return "Blue"
    else:
        return "Unknown"  # Handle other colors if needed
    

def track_objects(frame, detections, tracked_objects):
    
    """
    This function outputs the color of the detected object.

    Args:
        frame (np.ndarray):             currrent frame of the conveyor belt with objects.
        detections (list of tuple) :    list of tuples containing an object's center position, contour and angle
        tracked_objects (dictionnary) : Dictionnary containing all detected objects data as {"ID" : {"path" : [], "color" : string}}
        
    Returns:
        updated_objects (dictionnary):  Dictionnary containing updates detected objects data as {"ID" : (cx, cy, angle, color)}
    """
    
    # The next_id variable is used to assign new IDs to detected objects.
    # It must retain its value between function calls 
    global next_id
    
    # Empty dict that will contain {object_id: (cx, cy, color)} for the current frame.
    updated_objects = {}
    
    # Loop through each detected object in the current frame to find the Closest Existing Object
    for (cx, cy, cnt, angle) in detections:
        
        # Find closest existing object
        min_dist = float('inf')
        matched_id = None
        
        for obj_id, data in tracked_objects.items():
            if not data["path"]:
                continue
            # For each tracked object, get its last known position (last_pos)
            last_pos = data["path"][-1]
            # Compute Euclidean distance (dist) between the detection (cx, cy) and last_pos.
            dist = np.linalg.norm(np.array([cx, cy]) - np.array([last_pos[0], last_pos[1]]))
            
            # If the distance is smaller than 50 pixels (threshold for max movement), update matched_id.
            if dist < min_dist and dist < 50:  
                min_dist = dist
                matched_id = obj_id
        
        # Get color of the object (Blue or Red) from the contour
        color = get_contour_color(frame, cnt)
        
        # If matched (matched_id exists): Reuse the existing ID and update its position/color.
        if matched_id is not None:
            updated_objects[matched_id] = (cx, cy, angle, color)
        else:
            # If no match (matched_id is None): Assign a new ID (next_id) for the new object and increment the counter.
            updated_objects[next_id] = (cx, cy, angle, color)
            next_id += 1
    
    # For each object in updated_objects:
        
        
    for obj_id, (cx, cy, angle, color) in updated_objects.items():
        # Append its new position (cx, cy) to its "path" (trajectory history).
        tracked_objects[obj_id]["path"].append((cx, cy, angle))
        # Update its "color" if it changed.
        tracked_objects[obj_id]["color"] = color 
    
    # Returns the updated detections with assigned IDs for the current frame.
    return updated_objects

    
def predict_object_position(X, conveyor_belt_speed, delta_t, delay):
    
    """
    This function predict the center position (X component) of an object in the next frame.

    Args:
        X (float):      X component of the current position of the object [m].
        
    Returns:
        float:          predicted position (X component) of the object in the next frame.
    """
    # predicted_x = current_x + (conveyor_speed * time * delay)
    return X + conveyor_belt_speed*delta_t*delay



def update_or_append_object(JSON_FILE, object_id, predicted_x, predicted_y, color, real_X, angle):
    
    """
    This function updates existing object's position and add new objects if detected in the JSON file.

    Args:
        object_id (int) :       id corresponding to a single object.
        predicted_x (float) :   predicted center position (X component) of the object.
        predicted_y (float) :   predicted center position (Y component) of the object.
                                The Y component of the center postion remains the same over time since the conveyor belt translate horizontally (assuming the object does not move).
        color (str) :           Color of the object.
        real_X (float) :        Current center position (X component) of the object.
        angle (float) :         Angle in degrees of the object with respect to the horizontal.
        
    Returns: None
    """
    # 1. Load existing data
    try:
        with open(JSON_FILE, 'r') as f:
            objects = json.load(f) # List of all the objects
    except PermissionError:
        print(f"Permission denied for {JSON_FILE}. Is it open in another program?")
        return
    except FileNotFoundError:
        objects = []
    
    predicted_x = round(predicted_x, 4)
    predicted_y = round(predicted_y,4)
    real_X = round(real_X,4)
    # 2. Check if object_id exists
    updated = False
    for obj in objects:
        if obj["object_id"] == object_id:
            # Update existing object
            obj.update({
                "Current Pose" : [real_X,predicted_y, angle],
                "Predicted Pose": [predicted_x, predicted_y],
                "color": color,
                "timestamp": datetime.now().isoformat()
            })
            updated = True
            break
    
    # 3. Append new object if ID not found
    if not updated:
        new_obj = {
            "object_id": object_id,
            "Current Pose" : [real_X,predicted_y, angle],
            "Predicted Pose": [predicted_x, predicted_y],
            "color": color,
            "timestamp": datetime.now().isoformat()
        }
        objects.append(new_obj)
    
    # 4. Save back to file
    with open(JSON_FILE, 'w') as f:
        json.dump(objects, f, indent=2)
        