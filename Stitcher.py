import cv2
import numpy as np


# User Parameters/Constants to Set
MATCH_CL = 0.85 # Minimum confidence level (CL) required to match golden-image to scanned image
SPLIT_MATCHES_CL =  0.60 # Splits MATCH_CL to SPLIT_MATCHES_CL (defects) to one folder, rest (no defects) other folder
STICHED_IMAGES_DIRECTORY = "Images/Stitched_Images/"
GOLDEN_IMAGES_DIRECTORY = "Images/Golden_Images/"
SLEEP_TIME = 0.0 # Time to sleep in seconds between each window step


# Comparison scan window-image to golden-image
def getMatch(window, goldenImage, x, y):
    h1, w1, c1 = window.shape
    h2, w2, c2 = goldenImage.shape
    print(c1, c2, h1, h2, w1, w2)
    if c1 == c2 and h2 <= h1 and w2 <= w1:
        method = eval('cv2.TM_CCOEFF_NORMED')
        res = cv2.matchTemplate(window, goldenImage, method)   
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        if max_val > MATCH_CL: 
            print("\nFOUND MATCH")
            print("max_val = ", max_val)
            print("Window Coordinates: x1:", x + max_loc[0], "y1:", y + max_loc[1], \
                  "x2:", x + max_loc[0] + w2, "y2:", y + max_loc[1] + h2)
            
            # Gets coordinates of cropped image
            return (max_loc[0], max_loc[1], max_loc[0] + w2, max_loc[1] + h2, max_val)
        
        else:
            print("HERE")
            return ("null", "null", "null", "null", "null")


im1 = cv2.imread("./Images/1.jpg")
im2 = cv2.imread("./Images/2.jpg")
im3 = cv2.imread("./Images/3.jpg")

x1, y1, x2, y2, matchedCL = getMatch(im1[:,-300:,:], im2[20:-20,:100,:], 0, 0)

newImg = np.zeros((3000, 5000, 3))
newImg[50: 50+im1.shape[0], 50: 50+im1.shape[1], :] = im1
newImg[50-20+y1: 50-20+y1+im2.shape[0], 50+im1.shape[1]-300+x1: 50+im1.shape[1]-300+x1+im2.shape[1]] = im2
# :, im1.shape[1]-300+x1:im1.shape[1]-300+x2] = im2[20:-20,:100,:]

cv2.imwrite("./Images/test.jpg", newImg)


x1, y1, x2, y2, matchedCL = getMatch(im1[:,-300:,:], im2[20:-20,:100,:], 0, 0)

# im2[-20+y1:, :] = im2[:-(-20+y1), :]
# im2[:-20+y1, :] = 0

newImg2 = np.hstack( (im1[:, :-300+x1+10], im2[:,10:]) )
cv2.imwrite("./Images/test2.jpg", newImg2)


x1, y1, x2, y2, matchedCL = getMatch(newImg2[:,-300:,:], im3[20:-20,:100,:], 0, 0)

newImg3 = np.hstack( (newImg2[:, :-300+x1+10], im3[:,10:]) )
cv2.imwrite("./Images/test3.jpg", newImg3)

# image = im1.copy()
# image = cv2.resize(image, (900, 900))
# cv2.imshow("image", image)

# im3 = np.hstack((im1, im2[:,290:,:]))
# cv2.imwrite("./Images/test.jpg", im3)
# cv2.imwrite("./Images/imtest.jpg", im2[:,100:,:])

# imyes = im1.copy()
# imyes = cv2.resize(im3, (900, 900))
# cv2.imshow("Combined", imyes)
