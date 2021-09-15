import os
import cv2
import numpy as np
import glob


# User Parameters/Constants to Set
MATCH_CL = 0.70 # Minimum confidence level (CL) required to match golden-image to scanned image
SNAPSHOTS_DIRECTORY = "Images/Snapshots/"
STITCHED_IMAGES_DIRECTORY = "Images/Stitched_Images/"


def deleteDirContents(dir):
    # Deletes photos in path "dir"
    # # Used for deleting previous cropped photos from last run
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


# Comparison scan window-image to golden-image
def getMatch(window, goldenImage, x, y):
    h1, w1, c1 = window.shape
    h2, w2, c2 = goldenImage.shape
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
            return ("null", "null", "null", "null", "null")


# MAIN():
# =============================================================================
# Clears some of the screen for asthetics
print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

# Deletes contents in Stitched-Images folder
deleteDirContents("./Images/Stitched_Images/")

numDir = len(glob.glob(SNAPSHOTS_DIRECTORY + "*") )
isFirstTime = 1
rowNum = 1

# Stitches appropriate snapshots horizontaly
print("Starting horizontal stitching!")
cutYSize = 10
for imagePath in glob.glob(SNAPSHOTS_DIRECTORY + "*"):
    print("")
    image = cv2.imread(imagePath)
    if isFirstTime == 1:
        newImage = np.zeros((image.shape[0]+20, image.shape[1], \
                                   image.shape[2]), dtype = np.uint8)
        newImage[cutYSize:-cutYSize, :, :] = image
        growingImage = newImage
        isFirstTime = 0
        continue
    
    x1, y1, x2, y2, matchedCL = getMatch(growingImage[cutYSize:-cutYSize,-300:,:], image[cutYSize:-cutYSize,:50,:], 0, 0)
    if x1 == "null":
        print("x1 is null")
        if rowNum < 10:
            print("\nSaving Row Stitched Image!\n")
            cv2.imwrite("./Images/Stitched_Images/Stitched_Image-Row_0{}.png".format(rowNum), growingImage)
        else: 
            print("\nSaving Row Stitched Image!\n")
            cv2.imwrite("./Images/Stitched_Images/Stitched_Image-Row_{}.png".format(rowNum), growingImage)
        newImage = np.zeros((image.shape[0]+20, image.shape[1], \
                                   image.shape[2]), dtype = np.uint8)
        newImage[cutYSize:-cutYSize, :, :] = image
        growingImage = newImage
        rowNum += 1
    else: 
        newImage = np.zeros((growingImage.shape[0], image.shape[1], \
                                   image.shape[2]), dtype = np.uint8)
        newImage[(y1):(y2+2*cutYSize), :, :] = image
        image = newImage
        growingImage = np.hstack( (growingImage[:, :-300+x1+10], image[:,10:]) )

print("\n\nSaving Row Stitched Image!\n\n")
cv2.imwrite("./Images/Stitched_Images/Stitched_Image-Row_{}.png".format(rowNum), growingImage)


# Removes files under 8 mb
file = "./Images/Stitched_Images/"
for f in os.listdir(file): 
    if os.path.getsize(os.path.join(file, f)) < 8000000:
        os.remove(os.path.join(file, f))


isFirstTime = 1

# Stitches horizontaly stitched-snapshots vertically and completes
#   full-wafer stitchin
print("Starting vertical stitching!")
for imagePath in glob.glob(STITCHED_IMAGES_DIRECTORY + "*"):
    print("")
    print(imagePath)
    bottomImage = cv2.imread(imagePath)
    if isFirstTime == 1:
        topImage = bottomImage
        isFirstTime = 0
        continue
    
    if bottomImage.shape[1] > topImage.shape[1]:
        x1, y1, x2, y2, matchedCL = getMatch(bottomImage[cutYSize:300,:,:], topImage[-100:-cutYSize,:,:], 0, 0)
        
        newTopImage = np.zeros((topImage.shape[0], bottomImage.shape[1], \
                                   topImage.shape[2]), dtype = np.uint8)
        newTopImage[:, x1:x2, :] = topImage
        topImage = newTopImage
        
        topImage = np.concatenate((topImage[:-15, :], bottomImage[(y2-15):,:]) )
        waferImage = topImage
    else: 
        x1, y1, x2, y2, matchedCL = getMatch(topImage[-300:,:,:], bottomImage[:100,:,:], 0, 0)
        
        newBottomImage = np.zeros((bottomImage.shape[0], topImage.shape[1], \
                                   bottomImage.shape[2]), dtype = np.uint8)
        newBottomImage[:, x1:x2, :] = bottomImage
        bottomImage = newBottomImage
        
        topImage = np.concatenate((topImage[:(-300+y1+15), :], bottomImage[15:,:]) )
        waferImage = topImage
cv2.imwrite("./Images/Stitched_Images/Wafer_Image.png", waferImage)
print("\n\nDone!\n")

