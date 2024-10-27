 import cv2
import os
from ultralytics import YOLO 

def get_bounding_box_center_video(video_path, model, names, object_class):
    cap = cv2.VideoCapture(video_path)
    centers = []
    frame_num = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_num += 1
        results = model(frame)
        person_detected = False

        for result in results:
            detections = []
            print("Frame number: ", frame_num)

            for r in result.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                x1 = int(x1)
                x2 = int(x2)
                y1 = int(y1)
                y2 = int(y2)

                class_name = names.get(class_id)

                if class_name == object_class and score > 0.5:
                    if not person_detected:
                        person_detected = True
                        detections.append([x1, y1, x2, y2, round(score, 2), class_name])
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        centers.append((center_x, center_y))
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

            if not detections:
                centers.append("Not detected")

    cap.release()
    return centers 

def get_bounding_box_center_frame(frame, model, names, object_class):
    centers = []
    results = model(frame)
    person_detected = False

    for result in results:
        detections = []

        for r in result.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            x1 = int(x1)
            x2 = int(x2)
            y1 = int(y1)
            y2 = int(y2)

            class_name = names.get(class_id)

            if class_name == object_class and score > 0.5:
                if not person_detected:
                    person_detected = True
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    centers.append((center_x, center_y))

    if not person_detected:
        centers.append("Not detected")

    return centers 

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math

class KalmanFilter(object):
    def _init_(self, dt, INIT_POS_STD, INIT_VEL_STD, ACCEL_STD, GPS_POS_STD):

        """
        :param dt: sampling time (time for 1 cycle)
        :param INIT_POS_STD: initial position standard deviation in x-direction
        :param INIT_VEL_STD: initial position standard deviation in y-direction
        :param ACCEL_STD: process noise magnitude
        :param GPS_POS_STD: standard deviation of the measurement
        """

        # Define sampling time
        self.dt = dt

        # Intial State
        self.x = np.zeros((4, 1))

        # State Estimate Covariance Matrix
        cov = np.zeros((4, 4))
        cov[0, 0] = INIT_POS_STD ** 2
        cov[1, 1] = INIT_POS_STD ** 2
        cov[2, 2] = INIT_VEL_STD ** 2
        cov[3, 3] = INIT_VEL_STD ** 2
        self.P = cov

        # State Transition Matrix
        self.F = np.array([[1, 0, self.dt, 0],
                           [0, 1, 0, self.dt],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])

        # Covariance of Process model noise
        q = np.zeros((2, 2))
        q[0, 0] = ACCEL_STD ** 2
        q[1, 1] = ACCEL_STD ** 2
        self.q = q

        # Process Model Sensitivity Matrix
        L = np.zeros((4, 2))
        L[0, 0] = 0.5 * self.dt ** 2
        L[1, 1] = 0.5 * self.dt ** 2
        L[2, 0] = self.dt
        L[3, 1] = self.dt
        self.L = L

        # Process model noise
        self.Q = np.dot(self.L, np.dot(self.q, (self.L).T))

        # Define Measurement Mapping Matrix
        self.H = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]])

        # Measurement Covariance Matrix
        R = np.zeros((2, 2))
        R[0, 0] = GPS_POS_STD ** 2
        R[1, 1] = GPS_POS_STD ** 2
        self.R = R

    # PREDICTION STEP
    def predict(self):
        self.x = np.dot(self.F, self.x)
        self.P = np.dot(self.F, np.dot(self.P, (self.F).T)) + self.Q

        x_pred = self.x[0]
        y_pred = self.x[1]
        return x_pred, y_pred

    # UPDATE STEP
    def update(self, z):
        # Innovation
        z_hat = np.dot(self.H, self.x)
        self.y = z - z_hat

        # Innovation Covariance
        self.S = np.dot(self.H, np.dot(self.P, (self.H).T)) + self.R

        # Kalman Gain
        self.K = np.dot(self.P, np.dot((self.H).T, np.linalg.inv(self.S)))

        I = np.eye(4)

        self.x = self.x + np.dot(self.K, self.y)
        self.P = np.dot((I - np.dot(self.K, self.H)), self.P)

        x_updated = self.x[0]
        y_updated = self.x[1]
        return x_updated, y_updated

current_directory = os.getcwd()
print(current_directory)

# Go back to the parent directory
parent_directory = r"/home/niri/AI/drone_dataset"
print(parent_directory)

# Set input and output directory
video_path =  r"/home/niri/AI/drone_dataset/Drone_Tracking_1.mp4"
output_video_path = os.path.join(parent_directory, 'Output', 'running_4_kf.mp4')
print(video_path)

# Instantiate model
weights_path = r"/home/niri/AI/drone_dataset/runs/best.pt"
model = YOLO(weights_path)
names = model.names
print(names)

# Kalman filter parameters
dt = 1/30  # Sampling time = FPS
INIT_POS_STD = 10  # Initial position standard deviation
INIT_VEL_STD = 10  # Initial velocity standard deviation
ACCEL_STD = 40  # Acceleration standard deviation
GPS_POS_STD = 1  # Measurement position standard deviation 

# Kalman filter initialization
kf = KalmanFilter(dt, INIT_POS_STD, INIT_VEL_STD, ACCEL_STD, GPS_POS_STD) 

# Open the video file
cap = cv2.VideoCapture(video_path)
isFirstFrame = True 

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height)) 

while True:
    # Read frame from the video
    ret, frame = cap.read()

    # Break the loop if there are no more frames to read
    if not ret:
        break

    # Create the legend circles
    true_circle_position = (20, 20)
    predict_circle_position = (20, 50)
    update_circle_position = (20, 80)
    circle_radius = 6
    true_circle_color = (0, 255, 0)  # Green color for data
    predict_circle_color = (255, 0, 0)  # Blue color for forecast
    update_circle_color = (0, 0, 255)  # Red color for forecast
    circle_thickness = 2  # Filled circle

    # Draw the legend circles
    cv2.circle(frame, true_circle_position, circle_radius, true_circle_color, circle_thickness)
    cv2.circle(frame, predict_circle_position, circle_radius, predict_circle_color, circle_thickness)
    cv2.circle(frame, update_circle_position, circle_radius, update_circle_color, circle_thickness)

    # Draw the legend
    cv2.putText(frame, "True", (40, 25), cv2.FONT_HERSHEY_SIMPLEX, .5, true_circle_color, 2)
    cv2.putText(frame, "Predict", (40, 55), cv2.FONT_HERSHEY_SIMPLEX, .5, predict_circle_color, 2)
    cv2.putText(frame, "Update", (40, 85), cv2.FONT_HERSHEY_SIMPLEX, .5, update_circle_color, 2)

    # Process the frame to get bounding box centers
    centers = get_bounding_box_center_frame(frame, model, names, object_class='Drone')
    print(names)

    # Check if center is detected
    if len(centers) > 0:
        center = centers[0]  # Extract the first center tuple

        # Example: Draw circle at the center
        if isinstance(center, tuple):
            print("Center = ", center)
            cv2.circle(frame, center, radius=8, color=(0, 255, 0), thickness=4) # Green

            x_pred, y_pred = kf.predict()
            if isFirstFrame:  # First frame
                x_pred = round(x_pred[0])
                y_pred = round(y_pred[0])
                print("Predicted: ", (x_pred, y_pred))
                isFirstFrame = False
            else:
                x_pred = round(x_pred[0])
                y_pred = round(y_pred[1])
                print("Predicted: ", (x_pred, y_pred))

            cv2.circle(frame, (x_pred, y_pred), radius=8, color=(255, 0, 0), thickness=4) #  Blue

            # Update
            (x1, y1) = kf.update(center)
            x_updt = round(x1[0])
            y_updt =  round(x1[1])
            print("Update: ", (x_updt, y_updt))
            cv2.circle(frame, (x_updt, y_updt), radius=8, color= (0, 0, 255), thickness=4) # Red

    # Write frame to the output video
    out.write(frame)

    # Display the frame with circles
    cv2.imshow("Frame", frame)

    # Wait for the 'q' key to be pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close windows
cap.release()
out.release()
cv2.destroyAllWindows()