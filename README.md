# Intent_Detection
This is a repository for the Voxel51 hackathon.

Our goal in this hackathon is to detect the intent of an object of interest. By doing this, we can take appropriate actions, such as using the output to move a car away from or towards the object.

The problem statement addresses any scenario, but we focused on detecting the intent of pedestrians while the car is moving to determine if the car should move forward, turn, or switch lanes.

The input to the system will consist of a few frames, along with bounding box information to enable tracking. We will use this information to predict the possible direction of the object of interest and output a set of x, y points that can be used to plan ahead and react accordingly.
