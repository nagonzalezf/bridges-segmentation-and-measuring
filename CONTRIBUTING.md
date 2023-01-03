# Contributing

The current model provides a foundation for a variety of potential paths. It can be considered a starting point for preprocessing detection models based on convolutional networks or it can be reformulated as an automated machine learning algorithm.

## Code Optimization

The current code is rudimentary, it could be optimized by implementing functions or objects in such a way that they perform the same task using fewer lines of code.

## Model Automation

This is a complicated task. To automate the model it is necessary to eliminate the need for the user to manually enter the parameters when switching between images.

The parameters that present the most difficulty for this task are the hysteresis parameters of the Canny edge detector, the angle of rotation of the image and the diagonal parameters for tril & triu operations.

* Hysteresis parameters

  Tt may be possible to develop a model that determines the optimal parameters to use in the Canny edge detector. One way to do this would be to train a machine learning model with a set of input images and the expected outputs (the edges detected by Canny with different parameters). Then, the trained model could be used to predict which set of parameters should be used to achieve the best results on new images.

* Angle of Rotation

  This seems to be more manageable. One way to perform image alignment is to use feature-based methods, which identify distinctive features in the images and use them to determine the transformation needed to align the images. Another approach is to use intensity-based methods, which minimize the difference in intensity between the images being aligned.

  Once the transformation needed to align the images has been determined, the angle of rotation can be calculated from the transformation matrix. It is also possible to use machine learning techniques, such as a convolutional neural network, to learn the transformation needed to align the images from a training set of aligned images.

* Tril & Triu Parameters

  To eliminate the need to manually determine these parameters, It may be useful to use some of these morphological operations to improve the processing. For example, erosion can be used to remove noise or dilation can be used to connect parts of an object that have been separated by an edge detector.
