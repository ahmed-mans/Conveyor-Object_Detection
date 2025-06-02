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

The video below was used to perform the object detection test. As shown, the conveyor belt moves from right to left, allowing each object to pass beneath the overhead camera.<br>
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





















































## Diff shapes sizes ?
Indeed, the industrial vision system must detects red and blue platic objects. Such objects can have differents sizes, shapes (square, circle, complexe irregular shapes), textures and color variations (light red/ blue, dark red/blue, etc).
However, this test contains 5 objects of rectangular shapes only. Moreover,
