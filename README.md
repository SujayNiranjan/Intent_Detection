# Intent_Detection
## Objective
This is a repository for the Voxel51 hackathon.

Our goal in this hackathon is to detect the intent of an object of interest. By doing this, we can take appropriate actions, such as using the output to move a car away from or towards the object.

The problem statement addresses any scenario, but we focused on detecting the intent of pedestrians while the car is moving to determine if the car should move forward, turn, or switch lanes.

The input to the system will consist of a few frames, along with bounding box information to enable tracking. We will use this information to predict the possible direction of the object of interest and output a set of x, y points that can be used to plan ahead and react accordingly.

## Classical Approach
Our classical approach has three submodules. 
1. The first one is detecting the object of interest using bounding boxes. This can be done using models like YOLO (with a customized final layer) or even with models like Grounding DINO.
2. The next module uses optical flow or tracking DINO to track the object of interest in the scene.
3. Using Newton-Euler methods in our final module, we predict the next set of x, y points or trajectories.

## Unet + LSTM
The machine learning approach we plan to use involves a combination of UNet and LSTM. UNet will be utilized to generate a latent space representation of the initially fed scene or image, and this latent space will subsequently be used to train the LSTM to predict the future state of the scene.

The UNet training will be unsupervised, while the LSTM training will be supervised based on the outputs of the UNet.

By doing this, we can estimate or predict the future actions of the object. 
