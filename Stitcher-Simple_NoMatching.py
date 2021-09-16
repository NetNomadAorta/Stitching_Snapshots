import os
import cv2
import numpy as np
import glob



# User Parameters/Constants to Set
SNAPSHOTS_DIRECTORY = "Images/Snapshots/"
STITCHED_IMAGES_DIRECTORY = "Images/Stitched_Images/"
COLUMN_LIMIT = 55


def deleteDirContents(dir):
    # Deletes photos in path "dir"
    # # Used for deleting previous cropped photos from last run
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


# MAIN():
# =============================================================================
# Clears some of the screen for asthetics
print("\n\n\n\n\n\n\n\n\n\n\n\n\n")

# Deletes contents in Stitched-Images folder
deleteDirContents("./Images/Stitched_Images/")

numDir = len(glob.glob(SNAPSHOTS_DIRECTORY + "*") )
rowNum = 1
colNum = 1

# Stitches appropriate snapshots horizontaly
for imagePath in glob.glob(SNAPSHOTS_DIRECTORY + "*"):
    rightImage = cv2.imread(imagePath)
    if colNum == 1:
        leftImage = rightImage
        colNum += 1
        continue
    
    leftImage = np.hstack( (leftImage[:, :-287+10], rightImage[:,10:]) )
    
    if colNum != COLUMN_LIMIT: 
        colNum += 1
    else: 
        print("Saving Row", rowNum, "Image")
        cv2.imwrite("./Images/Stitched_Images/Stitched_Image-Row_{}.png".format(rowNum), leftImage)
        print("Saved Row", rowNum, "Image")
        rowNum += 1
        colNum = 1


isFirstTime = 1
# Stitches horizontaly stitched-snapshots vertically and completes
#   full-wafer stitchin
print("Starting vertical stitching!")
for imagePath in glob.glob(STITCHED_IMAGES_DIRECTORY + "*"):
    bottomImage = cv2.imread(imagePath)
    if isFirstTime == 1:
        topImage = bottomImage
        isFirstTime = 0
        continue
        
    topImage = np.concatenate((topImage[:-287+10, :], bottomImage[10:,:]) )
    waferImage = topImage

print("Saving Wafer Image")
cv2.imwrite("./Images/Stitched_Images/Wafer_Image.png", waferImage)
print("\n\nDone!\n")

