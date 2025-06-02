import cv2

    
def calibration(calibration_image_path, ref_object_coord, threshold):
    
    """
    This function computes the PPM (Pixel-per-Meter) ratio : number of pixels representing a distance of 1 meter.

    Args:
        calibration_image_path ('.png', '.jpg', etc): Path to image used for calibration.
        
        This image should represent a top down view of the converyor belt on which objects to be detected will be placed.
        This scene must contain a reference object of known size (width, height and depth) next to the conveyor belt. This object will be used to calibrate the camera

        ref_object_coord (list) : Provide the top left (x1, y1) and bottom right (x2,y2) pixel coordinates of the reference object of known size in the image.
                                  Keep a margin : 
                                    (x1, y1) should be some pixels smaller to the actual top left of the reference object
                                    (x2, y2) should be some pixels bigger to the actual bottom right of the reference object
    Returns:
        int: PPM
    """
    
    # Read image and convert it to grayscale
    image = cv2.imread(calibration_image_path)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    
    x1, y1, x2, y2 = ref_object_coord[0], ref_object_coord[1], ref_object_coord[2], ref_object_coord[3] 
    
    # Crop the reference object from the image
    cropped_gray = image_gray[y1:y2, x1:x2]
    
    # Get binary image and detect contours of the reference object
    ret,thresh1 = cv2.threshold(cropped_gray,threshold,255,cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Get the width value of the reference object (in pixels)
    x, y, w_px, h_px = cv2.boundingRect(contours[0])
    print(f"The width of the reference object is {w_px} pixels.")
    
    # Provide the real width of the reference object in meters
    real_width = 0.1 # m
    print(f"The width of the reference object is {real_width} meters.")
    
    # Compute Pixels-Per-Meter (PPM) Ratio
    PPM = w_px / real_width 
    
    print("Calibration done : ")
    print(f"{int(PPM)} pixels represent 1 meter in the simulated world of the conveyor belt.")
    return int(PPM)

def convert_pixel_to_real(frame, last_pos, ppm):
    
    """
    This function uses the PPM ratio to convert the center of a detected objects in pixel coordinates (x,y) to real world coordinate in a metric system (X,Y)

    Args:
        frame (np.ndarray):     currrent frame of the conveyor belt with objects.
        last_pos (tuple) :      tuple containing (x,y,theta) where x,y are the 2D center coordinate of the object in the cuurent frame
                                and theta is its orientation with respect to the horizontal.
        
    Returns:
        float: X, Y coordinate of the object's center in meter 
    """
    
    # Get the frame's origin coordinates in pixels
    x0, y0 = int(frame.shape[1]/2), int(frame.shape[0]/2)
    
    # Compute real world coordinates X, Y [m]
    new_x_object, new_y_object = x0 - last_pos[0], y0 - last_pos[1]
    X, Y = new_x_object/ppm,  new_y_object/ppm
    
    return X,Y
