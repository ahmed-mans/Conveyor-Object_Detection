# 🚀 Corematic Technical Test - Industrial Simulated Vision Project
This project simulates an industrial vision system that detects plastic objects of two different colors (🔴 red or 🔵 blue) on a moving conveyor belt.

A robotic arm is positioned beside the belt to pick up each object based on data provided by the vision system, and sort them by color.

## 🎯 Project Objectives
Detect objects on a conveyor belt using a simulated top-down camera feed.<br>
Analyze each object to determine:

📍 Position<br>
🔄 Orientation<br>
🎨 Color

Transmit this information to a robotic arm for real-time sorting.

## 🎥 The Vision System
The system is built consists of an RGB camera installed directly above the conveyor belt, providing a top-dow view of the moving objects.<br>
As objects pass beneath the camera, the system must detect and process the following information for each one:

📌 Precise (X, Y) position in real-world units (meters)<br>
📐 Angle of orientation relative to the conveyor<br>
🔴🔵 Color classification (Red or Blue)

 ## 🖥️ Blender Simulation
To simulate the test environment, a moving conveyor belt setup was created using Blender, a 3D modeling and animation tool.<br>
🖼️ The image below illustrates a 3D top-down view of the simulated conveyor system:

🧱 The conveyor belt is represented by a black rectangular plane.<br>
🔷🔴 Five colored objects (blue and red), each with different sizes and shapes, are placed on the belt to simulate variety.<br>
📷 An RGB camera is positioned directly above the conveyor belt, mimicking the real-world top-down camera setup described in the vision system.

This simulated environment serves as the input for the vision-based object detection pipeline.
   
![blender_sim_cropped](https://github.com/user-attachments/assets/cc3acd95-a2e0-4bbf-946e-9be187823151)

The video below was used to perform the object detection test in Python. As shown, the conveyor belt moves from right to left, allowing each object to pass beneath the overhead camera.<br>
As the objects move, the vision system will detect their:

📍 Position<br>
🔄 Orientation<br>
🎨 Color

https://github.com/user-attachments/assets/a5aaf23c-5af6-408e-8320-8b77f29ecd23

### ⚠️ Assumptions
To simplify and focus this test, several key assumptions were made:

- The simulated objects are rectangular in shape, with uniform texture and solid color.<br>
- The scene is subjected to consistent and uniform lighting conditions.

These assumptions reduce the complexity of the detection task. As a result, basic image processing techniques are sufficient to extract key object properties such as position, orientation, and color.<br>
🔍 The final section will explore the limitations of this setup and discuss how performance might change with more realistic conditions — such as irregularly shaped objects, variable sizes, and less distinctive colors.

## Run the test
Follow these steps to run the project on your local machine:

### 1️⃣ Clone the Repository
Use the following command to clone the repository:<br>

   ```https://github.com/ahmed-mans/Conveyor-Object_Detection.git ```
### 2️⃣ Install Dependencies
Navigate to the cloned project directory and install the required Python packages:<br>
   
   ``` pip install -r requirements.txt ```<br>

✅ The ``` requirements.txt``` file includes all necessary libraries such as ```opencv-python, numpy, pyyaml```, and others needed for running the vision system.

### 3️⃣ Run the Main Script: 
Start the vision tracking system with: <br>
   
   ``` python main.py ```

### 4️⃣ Output Overview
Upon running the script, you’ll observe two main outputs:

🎥 Visual Output: A live video window showing objects detected by the vision system. Each object is tracked with a unique ID as it passes under the camera.<br>
🗃️ Data Output: ```detected_objects.json``` file (to open manually) that logs real-time data for each object, including:

- Object ID: A unique identifier assigned to each object to consistently track it across frames.<br>
- Center Position (X, Y): The object’s current center coordinates in the frame, expressed in meters (m). <br>
- Orientation Angle: The object’s rotation angle (in degrees) relative to the horizontal axis in the current frame.<br>
- Predicted Center Position: The estimated center coordinates (in meters) of the object in the next frame, based on conveyor speed and system latency <br>
- Color Classification — The identified color of the object: either Red or Blue.<br>
- Timestamp: Records the exact time of detection, providing essential information for synchronization with the robotic arm.

Here is an example of what the ```detected_objects.json``` contains:
```
{
    "object_id": 0,
    "Current Pose": [
      0.164,
      0.1022,
      0.0
    ],
    "Predicted Pose": [
      0.1874,
      0.1022
    ],
    "color": "Blue",
    "timestamp": "2025-06-01T23:11:23.355921"
  }
```
✅ The purpose of this file is for the robotic arm operator to use it as an input for the robotic arm to pick up each object on the conveyor belt at the right location and time.

# 🧠 Object Detection Pipeline
This section outlines the key steps used to implement the object detection algorithm during this test.

To closely replicate a real-world industrial scenario, the Blender simulation was designed with realistic dimensions:

The conveyor belt is 80 cm wide (0.8 meters)<br>
The objects on the belt range from 10 cm to 40 cm in length and 4 cm to 10 cm in depth<br>
The RGB camera provides a top-down view with a resolution of 1920x1080 pixels

Since the RGB camera only provides pixel-based information (such as position within the image), these pixel coordinates are not directly usable by the robotic arm to locate and pick up the objects.<br>
To bridge this gap, an absolute reference coordinate system (in meters) must be established. This allows both the camera and the robot to interpret object locations consistently within the same spatial frame.<br>
The first step toward this goal is to calibrate the camera to determine the relationship between pixel dimensions and real-world measurements.

## 1) Calibration
Calibration is the process of converting pixel coordinates from the camera into real-world measurements (e.g., meters or centimeters). This step is essential to ensure that the detected object positions can be interpreted by the robotic system in physical space.

### Step 1: Capture a Reference Frame
To begin calibration, a reference frame must be captured. This frame should closely resemble the actual video frames used for object detection with one key difference: it must include an object of known dimensions.
In this test, a green square measuring 10×10×1 cm was placed next to the conveyor belt, as shown in the image below.

![calibration](https://github.com/user-attachments/assets/9cbba7de-13ce-4002-8b7a-fd479fb240c8)

### Step 2: Measure in Pixels
Using basic image processing techniques (e.g., contour detection), the width of the reference object in pixels can be measured.

### Step 3: Compute the Pixel-Per-Meter (PPM) Ratio

Once the pixel width of the known object is determined, the Pixel-Per-Meter (PPM) ratio can be calculated:

**Pixel-Per-Meter (PPM)** = (Object width in pixels) / (Object width in meters)

This ratio defines how many pixels correspond to one meter in the current camera view, and will be used throughout the detection pipeline to convert all image-based measurements to real-world units.

✅ Note that the depth of objects in this test can be computed as well since it can have an impact for the robotic arm. However, in this project only the position and angle are required. Therefore, the depth is not mentionned.

## 2) Region of Interest (ROI) Masking

This step focuses on isolating the region of the conveyor belt to optimize image processing.<br>
Since objects of interest are only located on the conveyor belt, the rest of the image can be safely ignored.

By creating a mask that highlights only the belt area, we can:

Reduce unnecessary computations.<br>
Eliminate background noise.<br>
Improve detection accuracy and speed.<br>

This ensures that the object detection algorithm processes only the relevant part of the image, as shown in the picture below.

![mask_cropped](https://github.com/user-attachments/assets/6e7e5116-0c28-4863-a60e-3b860f543659)


## 3) Detection Process
Each video frame undergoes several steps to detect and track objects on the conveyor belt:

### 1. Grayscale Conversion
The RGB frame is converted to a grayscale image to simplify processing.

### 2. Thresholding
A binary threshold is applied to highlight the objects (white pixels) against the background (black pixels). The threshold value is chosen empirically.

### 3. Contour Detection
Using the binary image, contours of the white regions (objects) are detected. From each contour, we compute:

- The center position of the object.
- The orientation angle (anti-clockwise) with respect to the horizontal.

### 4. Object Tracking

- Detected objects are assigned unique IDs and tracked across frames by computing the euclidean distance of the center position between 2 consecutive frames.
- Their positions and angles are updated in each new frame.
- If a new object appears, it is added as a new detection with a new ID.

#### 4.1 Detection Window Strategy
To ensure accurate detection and tracking, the vision system operates within a specific spatial window of the frame—namely, from ¾ (75%) to ¼ (25%) of the frame's width.

This restriction ensures that each object is fully visible beneath the camera before being analyzed, allowing the system to compute a reliable orientation and center position.

Indeed, if an object is partially entering the frame from the right or just exiting on the left, only part of its contour will be detected. This partial view leads to:

- Incorrect estimation of the object’s orientation relative to the horizontal.
- Inaccurate updates to the object’s data in the detected_objects.json file.

By applying this spatial constraint, we reduce the chance of tracking errors and ensure data precision.
✅ Concerning continuous tracking of objects for the robotic arm, its operator can read the updated values of the center position of the objects. When the values stop updating (from ¼ of the frame's width), the operator can create a feedback loop to compute the predicted values of the center position of the objects based on the converyor speed to keep tracking the object's position for pick up.

### 5. Coordinate conversion
The center position of each object is converted from pixel (Px, Py) coordinate to an absolute reference coordinate (X,Y) as shown in the image below.

![conversion](https://github.com/user-attachments/assets/f2a7e731-1729-42b7-a211-dfaa6174eb44)

### 6. JSON file update
As objects are detected and tracked frame by frame, the file ```detected_objects.json``` is continuously updated.
Each entry in the file contains real-time data for every object, including:

- Object ID
- Position (X, Y in meters)
- Orientation angle (in degrees)
- Predicted position in the next frame
- Color (Red or Blue)
- Frame timestamp

Assuming the robotic arm is positioned further to the left of the vision system, it can use the absolute reference coordinate system to align its movements.
By adding an offset in the X component, the robotic arm knows its exact location relative to the camera. Using this information, it can:

- Compare its grip position to the predicted center position of an object.
- Compute the optimal path and timing to pick up the object precisely as it arrives.

✅ Note: This object detection system provides precision up to 10 mm when predicting the position of an object based on the conveyor belt speed.



# Custom setup
If one wants to use this object detection for his/her own custom setup to detect blue and red objects on a conveyor belt, here are the steps to follow : 

## 1. Calibrate your camera
If the camera used for the custom setup does not introduce distortion and does not have a significant dept, the method mentioned above can be used to calibrate the camera and compute the PPM.
For that, in the ```config.yaml``` file in the /config directory, one can change :

- the calibration image path:
  
```
calibration_image_path: add your calibration image path
```

- the reference object coordinate ```[x1, y1, x2, y2]``` in pixels in the calibration image:
```
reference_object_coordinate : [x1, y1, x2, y2]
```




## New cases ?
Indeed, the industrial vision system must detects red and blue platic objects. Such objects can have differents sizes, shapes (square, circle, complexe irregular shapes), textures and color variations (light red/ blue, dark red/blue, etc).
However, this test contains 5 objects of rectangular shapes only. Moreover,
