import time
import os
import shutil
import cv2
import numpy as np
import glob



# User Parameters/Constants to Set
SNAPSHOTS_DIRECTORY = "Images/Snapshots/"
STITCHED_IMAGES_DIRECTORY = "Images/Stitched_Images/"
COLUMN_LIMIT = 55 # Number of snapshots to be used to stitched together horizontally
ROW_LIMIT = 4 # Number of horizontal stitched-images that can be stitched together vertically
# Note: leave Row_Limit = 0 to stitch full-wafer

def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0}:{1}:{2}".format(int(hours) ,int(mins), round(sec)))


def deleteDirContents(dir):
    # Deletes photos in path "dir"
    # # Used for deleting previous cropped photos from last run
    for f in os.listdir(dir):
        fullName = os.path.join(dir, f)
        shutil.rmtree(fullName)


def fillMissingSnapshot(slotDir):
    dirList = glob.glob(slotDir + "/*")
    for i in range(len(dirList) ): 
        if not str(int(dirList[0][-11:-7])+i) in dirList[i]:
            print("Missing file after this one:")
            print(dirList[i-1])
            cv2.imwrite(dirList[0][:-11] + "{}.p0.jpg".format(int(dirList[0][-11:-7])+i), cv2.imread(dirList[i-1]))
            break


# MAIN():
# =============================================================================
# Starting stopwatch to see how long process takes
start_time = time.time()

# Clears some of the screen for asthetics
print("\n\n\n\n\n\n\n\n\n\n\n\n\n")

# Deletes contents in Stitched-Images folder
deleteDirContents("./Images/Stitched_Images/Horizontal_Stitched_Images/")
deleteDirContents("./Images/Stitched_Images/Vertical_Stitched_Images/")

# Main snapshot directory
mainSnapDir = glob.glob(SNAPSHOTS_DIRECTORY + "*")


# Runs through each slot file within the main file within snapshot folder
for slotDir in glob.glob(mainSnapDir[0] + "/*"): 
    # Create stitched image directory
    os.makedirs("./Images/Stitched_Images/Horizontal_Stitched_Images/" + \
        slotDir[17:-3] + "/" + slotDir[-2:], exist_ok=True)
    os.makedirs("./Images/Stitched_Images/Vertical_Stitched_Images/" + \
        slotDir[17:-3] + "/" + slotDir[-2:], exist_ok=True)
    
    # If a snapshot is missing, below will put a placeholder
    fillMissingSnapshot(slotDir)

    numDir = len(glob.glob(slotDir + "/*") )
    rowNum = 1
    colNum = 1
    
    # Stitches appropriate snapshots horizontaly
    for imagePath in glob.glob(slotDir + "/*"):
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
            if rowNum < 10:
                cv2.imwrite("./Images/Stitched_Images/Horizontal_Stitched_Images/" \
                    + slotDir[17:-3] + "/" + slotDir[-2:] + \
                    "/Slot_{}-Row_0{}.png".format(slotDir[-2:], rowNum), leftImage)
            else: 
                cv2.imwrite("./Images/Stitched_Images/Horizontal_Stitched_Images/" \
                    + slotDir[17:-3] + "/" + slotDir[-2:] + \
                    "/Slot_{}-Row_{}.png".format(slotDir[-2:], rowNum), leftImage)
            print("Saved Row", rowNum, "Image")
            rowNum += 1
            colNum = 1


    # Stitches horizontaly stitched-snapshots vertically and completes
    #   full-wafer stitching
    if ROW_LIMIT == 0:
        isFirstTime = 1
        print("\nStarted vertical stitching!")
        for imagePath in glob.glob("./Images/Stitched_Images/Horizontal_Stitched_Images/" \
                + slotDir[17:-3] + "/" + slotDir[-2:] + "/*"):
            bottomImage = cv2.imread(imagePath)
            if isFirstTime == 1:
                topImage = bottomImage
                isFirstTime = 0
                continue
                
            topImage = np.concatenate((topImage[:-287+10, :], bottomImage[10:,:]) )
            waferImage = topImage
        
        print("Saving Wafer Image")
        cv2.imwrite("./Images/Stitched_Images/Vertical_Stitched_Images/" \
            + slotDir[17:-3] + "/" + slotDir[-2:] + "//Slot_{}.png".format(slotDir[-2:]), waferImage)
        print("\nDone!\n")
    # Stitches horizontaly stitched-snapshots vertically and completes
    #   ROW_LIMIT Rows of snapshots stitching
    else:
        i = 1
        print("\nStarting vertical stitching!")
        for imagePath in glob.glob("./Images/Stitched_Images/Horizontal_Stitched_Images/" \
                + slotDir[17:-3] + "/" + slotDir[-2:] + "/*"):
            bottomImage = cv2.imread(imagePath)
            if ((i-1) % (ROW_LIMIT-1)) == 0:
                
                if i != 1:
                    topImage = np.concatenate((topImage[:-287+10, :], bottomImage[10:,:]) )
                    waferImage = topImage
                    print("Saving Wafer Image", round((i-1) / 3) )
                    cv2.imwrite("./Images/Stitched_Images/Vertical_Stitched_Images/" \
                        + slotDir[17:-3] + "/" + slotDir[-2:] + \
                        "//Slot_{}-Row_{}.png".format(slotDir[-2:], round((i-1) / 3) ), waferImage)
                    print("Saved")
                topImage = bottomImage
                i += 1
                continue
            topImage = np.concatenate((topImage[:-287+10, :], bottomImage[10:,:]) )
            waferImage = topImage
            i += 1
        print("\nDone!\n")

# Starting stopwatch to see how long process takes
end_time = time.time()
time_lapsed = end_time - start_time
time_convert(time_lapsed)