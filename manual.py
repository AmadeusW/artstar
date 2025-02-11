import cv2
import numpy as np

useEdgeDetection = False
xTranslationA = 0
yTranslationA = 0
xTranslationB = 0
yTranslationB = 0
deltaTranslation = 20
imageA = cv2.imread('data/watertower01.jpg')
imageB = cv2.imread('data/watertower02.jpg')
visibleImageA = imageA
visibleImageB = imageB

def updateImages():
    if useEdgeDetection:
        visibleImageA = cv2.Canny(imageA, 100, 200)
        visibleImageB = cv2.Canny(imageB, 100, 200)
    else:
        visibleImageA = imageA
        visibleImageB = imageB

    print("edge detection", useEdgeDetection)    
    translation_matrixA = np.float32([[1, 0, xTranslationA], [0, 1, yTranslationA]])
    translation_matrixB = np.float32([[1, 0, xTranslationB], [0, 1, yTranslationB]])
    visibleImageA = cv2.warpAffine(visibleImageA, translation_matrixA, (imageA.shape[1], imageA.shape[0]))
    visibleImageB = cv2.warpAffine(visibleImageB, translation_matrixB, (imageB.shape[1], imageB.shape[0]))
    blended = cv2.addWeighted(visibleImageA, 0.5, visibleImageB, 0.5, 0)
    return blended

def updateWindow(image):
    window_name = 'Art Star'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    screen = cv2.getWindowImageRect(window_name)
    if screen[2] > 0 and screen[3] > 0:  # If window dimensions are valid
        scale = min(screen[2] / image.shape[1], screen[3] / image.shape[0])
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    cv2.imshow('Art Star', image)

def update():
    print("updating")
    finalImage = updateImages()
    updateWindow(finalImage)

while True:
    key = cv2.waitKey(0)
    match (chr(key & 0xFF) if key != -1 else '\0', bool(key & 0xFF00)):  # (key char, is_ctrl_pressed)
        case 'e', False:
            useEdgeDetection = not useEdgeDetection
        case 'q', False:
            break
        case ('w', True):
            yTranslationB -= deltaTranslation
        case ('w', False):
            yTranslationA -= deltaTranslation
        case ('s', True):
            yTranslationB += deltaTranslation
        case ('s', False):
            yTranslationA += deltaTranslation
        case ('a', True):
            xTranslationB -= deltaTranslation
        case ('a', False):
            xTranslationA -= deltaTranslation
        case ('d', True):
            xTranslationB += deltaTranslation
        case ('d', False):
            xTranslationA += deltaTranslation
    update()

cv2.destroyAllWindows()