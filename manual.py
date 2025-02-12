import cv2
import numpy as np

# Define a class to hold image data
class ImageData:
    def __init__(self, filepath):
        self.filepath = filepath
        self.image = cv2.imread(filepath)
        self.translationX = 0
        self.translationY = 0
        self.rotation = 0
        self.skew = 0
        self.zoom = 0

# Initialize list of images instead of individual variables
useEdgeDetection = False
useBlending = False
currentIndex = 0
deltaTranslation = 20
edgeA = 100
edgeB = 200
images = [
    ImageData('data/watertower01.jpg'),
    ImageData('data/watertower02.jpg'),
    ImageData('data/watertower03.jpg')
]

def getImage(index):
    imageData = images[index]
    print("using ", index, imageData.filepath)
    image = cv2.Canny(imageData.image, edgeA, edgeB) if useEdgeDetection else imageData.image
    # Create transformation matrix incorporating translation, rotation and skew
    angle = np.radians(imageData.rotation)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    skew_rad = np.radians(imageData.skew)
    transform_matrix = np.float32([
        [cos_a, -sin_a + np.tan(skew_rad), imageData.translationX],
        [sin_a, cos_a, imageData.translationY]
    ])
    transform_matrix = transform_matrix * (1 + imageData.zoom)
    transformed = cv2.warpAffine(image, transform_matrix,
                                   (imageData.image.shape[1], imageData.image.shape[0]))
    return transformed

def updateImages():
    print("update. blending ", useBlending)
    if useBlending:
        return cv2.addWeighted(
            getImage(currentIndex), 0.5,
            getImage((currentIndex - 1) % len(images)), 0.5,
            0)
    else:
        return getImage(currentIndex)

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

def constrain_value(value, delta, min_val, max_val):
    new_value = value + delta
    return max(min_val, min(new_value, max_val))

update()
while True:
    key = cv2.waitKey(0)
    if key == -1:
        continue

    match chr(key & 0xFF):
        case 'E':
            useEdgeDetection = not useEdgeDetection
        case 'B':
            useBlending = not useBlending
        case 'Q':
            break
        case '=':
            currentIndex = (currentIndex + 1) % len(images)
        case '-':
            currentIndex = (currentIndex - 1) % len(images)
        case '[':
            edgeA = constrain_value(edgeA, -10, 0, 255)
        case ']':
            edgeA = constrain_value(edgeA, 10, 0, 255)
        case '{':
            edgeB = constrain_value(edgeB, -10, 0, 255)
        case '}':
            edgeB = constrain_value(edgeB, 10, 0, 255)
        case 'r':
            images[currentIndex].skew = constrain_value(images[currentIndex].skew, -1, -89, 89)
        case 'w':
            images[currentIndex].translationY -= deltaTranslation
        case 'f':
            images[currentIndex].skew = constrain_value(images[currentIndex].skew, 1, -89, 89)
        case 's':
            images[currentIndex].translationY += deltaTranslation
        case 'q':
            images[currentIndex].rotation = constrain_value(images[currentIndex].rotation, -1, -180, 180)
        case 'a':
            images[currentIndex].translationX -= deltaTranslation
        case 'e':
            images[currentIndex].rotation = constrain_value(images[currentIndex].rotation, 1, -180, 180)
        case 'd':
            images[currentIndex].translationX += deltaTranslation
        case 'z':
            images[currentIndex].zoom -= 0.05
        case 'x':
            images[currentIndex].zoom += 0.05
    update()

cv2.destroyAllWindows()