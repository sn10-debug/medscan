import json
import requests
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.signal import find_peaks
import os


def maxima_indices(column_data):
    peaks, _ = find_peaks(column_data)
    local_maxima = column_data[peaks]
    print(local_maxima)


def get_intensity(image):


    image_array =  np.array(image)

    

    # Define the step size a5nd the slit width
    step_size = 1
    slit_width = 15

    # Initialize a list to hold the average intensities

    average_intensities = []
    if image_array.shape[0]> image_array.shape[1]:

        # Iterate over the image in steps of 10 along the y-axis
        for y_coordinate in range(0, image_array.shape[0], step_size):
            # Ensure the slit does not go out of bounds
            if y_coordinate + slit_width <= image_array.shape[0]:
                # Extract the horizontal slit
                horizontal_slit = image_array[y_coordinate:y_coordinate + slit_width, :image_array.shape[1]]
                # Calculate the average color intensity
                average_intensity = np.mean(horizontal_slit)
                # Append the average intensity to the list
                average_intensities.append(average_intensity)
    else:
        for x_coordinate in range(0, image_array.shape[1], step_size):
            # Ensure the slit does not go out of bounds
            if x_coordinate + slit_width <= image_array.shape[1]:
                # Extract the horizontal slit
                horizontal_slit = image_array[:((image_array.shape[0])),x_coordinate:x_coordinate + slit_width]
                # Calculate the average color intensity
                average_intensity = np.mean(horizontal_slit)
                # Append the average intensity to the list
                average_intensities.append(average_intensity)



    # Assuming average_intensities is a list of average intensity values

    intensities_array = np.array(average_intensities)

    local_minima_indices = find_peaks(-intensities_array)[0]


    minima_intensities=[average_intensities[i] for i in local_minima_indices]

    minima_intensities_2=[average_intensities[i] for i in local_minima_indices]
    minima_intensities.sort()

    

    return minima_intensities[0:2]





    # Plot the original image and the intensity plot
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))

    # Plot the image
    ax[0].imshow(image_array, cmap='gray')
    ax[0].set_title('Original Image')
    ax[0].axis('off')

    # Plot the intensity values
    ax[1].plot(range(0, len(average_intensities) * step_size, step_size), average_intensities, marker='o')
    ax[1].set_title('Average Intensity per Section')
    ax[1].set_xlabel('Y Coordinate')
    ax[1].set_ylabel('Average Intensity')

    plt.tight_layout()
    plt.show()



def findIntensity(bufferedImage,cvImage):

    url = "https://api.ultralytics.com/v1/predict/PZ60cJ9fMQXhh2Lay7Ti"
    headers = {"x-api-key": "7744483b1013727e3037f27aca22f11ed7ea57c45b"}
    data = {"size": 640, "confidence": 0.25, "iou": 0.45}
  

    
    response = requests.post(url, headers=headers, data=data, files={"image": bufferedImage})

    # Check for successful response
    response.raise_for_status()

    # Parse inference results
    inference_result = response.json()
    print(json.dumps(inference_result, indent=2))

    height, width, _ = cvImage.shape
    image = cv2.cvtColor(cvImage, cv2.COLOR_BGR2GRAY)

    bounding_box_mask = np.zeros_like(cvImage)





    image2=None

    for item in inference_result["data"]:
        xcenter = item["xcenter"] * width
        ycenter = item["ycenter"] * height
        box_width = item["width"] * width
        box_height = item["height"] * height

        # Calculate the bounding box coordinates

        left = int(xcenter - box_width / 2)
        right = int(xcenter + box_width / 2)
        top = int(ycenter - box_height / 2)
        bottom = int(ycenter + box_height / 2)

        image2=image[top:bottom,left:right]

    return get_intensity(image2)


    
