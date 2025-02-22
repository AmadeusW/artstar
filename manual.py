import cv2
import numpy as np
from image_data import ImageData, save_image_data, load_image_data

# Initialize list of images instead of individual variables
useEdgeDetection = False
useBlending = False
direction = False
currentIndex = 0
deltaTranslation = 20
edgeA = 100
edgeB = 200
images = load_image_data()

def getImage(index, useEdgeDetection):
    imageData = images[index]
    image = imageData.image
    h, w = image.shape[:2]
    #print(f"Image #{index} `{imageData.filepath}`, {w}x{h} edge {useEdgeDetection}.")

    if useEdgeDetection:
        edgeDetected = cv2.Canny(imageData.image, edgeA, edgeB)
        image = cv2.cvtColor(edgeDetected, cv2.COLOR_GRAY2RGB)
    
    # Calculate perspective transform matrix
    # skew_factor determines how much the top/bottom edge shrinks
    # Positive skew shrinks top edge, negative shrinks bottom edge
    skew_factor = np.tan(np.radians(imageData.skew))
    offset = abs(int(w * skew_factor / 2))
    
    # Source points are the four corners of the image
    src_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    
    if imageData.skew >= 0: # Shrink top edge
        dst_pts = np.float32([[offset, 0], [w - offset, 0], [w, h], [0, h]])
    else: # Shrink bottom edge
        dst_pts = np.float32([[0, 0], [w, 0], [w - offset, h], [offset, h]])
    
    # Perspective transform matrix
    perspective_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    transformed = cv2.warpPerspective(image, perspective_matrix, (w, h))

    # Rotation and translation
    angle = np.radians(imageData.rotation)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    transform_matrix = np.float32([
        [cos_a, -sin_a, imageData.translationX],
        [sin_a, cos_a, imageData.translationY]
    ])
    transform_matrix = transform_matrix * (1 + imageData.zoom)
    transformed = cv2.warpAffine(transformed, transform_matrix, (w, h))

    return transformed

def getBlendedIndex():
    return currentIndex - 1 if direction else currentIndex + 1

def updateImages():
    if useBlending:
        return cv2.addWeighted(
            getImage(currentIndex, False), 1,
            getImage(getBlendedIndex() % len(images), useEdgeDetection), 0.5,
            0)
    else:
        return getImage(currentIndex, False)

def drawImageInfo(image):
    # Create text with current image data
    info_text = f"File: {images[currentIndex].filepath}\n"
    info_text += f"Transform: "
    info_text += f"x {images[currentIndex].translationX}, y {images[currentIndex].translationY} "
    info_text += f"r {images[currentIndex].rotation} "
    info_text += f"p {images[currentIndex].skew} "
    info_text += f"s {images[currentIndex].zoom:.2f}\n"

    if useBlending:
        info_text += f"Overlay: {images[getBlendedIndex()].filepath}\n"

    # Split text into lines
    lines = info_text.split('\n')

    # Set text parameters
    font = cv2.FONT_HERSHEY_PLAIN
    font_scale = 1
    thickness = 1
    padding = 10
    line_spacing = 25

    # Create a copy of the image to avoid modifying the original
    image_with_text = image.copy()

    # Draw black background and white text for each line
    y = padding
    for line in lines:
        size = cv2.getTextSize(line, font, font_scale, thickness)[0]
        cv2.putText(image_with_text, line, (padding, y + size[1]), font, font_scale, (255,255,255), thickness)
        y += line_spacing

    return image_with_text

def updateWindow(image):
    window_name = 'Art Star'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    screen = cv2.getWindowImageRect(window_name)

    # Apply transform
    if screen[2] > 0 and screen[3] > 0:  # If window dimensions are valid
        scale = min(screen[2] / image.shape[1], screen[3] / image.shape[0])
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

    # Add image info
    image = drawImageInfo(image)
    cv2.imshow('Art Star', image)

def update():
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
            print(f"useEdgeDetection {useEdgeDetection}")
        case 'B':
            useBlending = not useBlending
            print(f"useBlending {useBlending}")
        case '`':
            direction = not direction
            print(f"direction {direction}")
        case 'Q':
            print(f"Saving on close...")
            save_image_data(images)
            break
        case 'C':
            print(f"Copied transformation of {copied_data}")
            copied_data = images[currentIndex]
        case 'V':
            print(f"Pasted transformation {copied_data}")
            images[currentIndex].applyTransformation(copied_data)
        case '=':
            currentIndex = (currentIndex + 1) % len(images)
            print(f"currentIndex {currentIndex}")
        case '-':
            currentIndex = (currentIndex - 1) % len(images)
            print(f"currentIndex {currentIndex}")
        case '[':
            edgeA = constrain_value(edgeA, -10, 0, 255)
            print(f"edgeA {edgeA}")
        case ']':
            edgeA = constrain_value(edgeA, 10, 0, 255)
            print(f"edgeA {edgeA}")
        case '{':
            edgeB = constrain_value(edgeB, -10, 0, 255)
            print(f"edgeB {edgeB}")
        case '}':
            edgeB = constrain_value(edgeB, 10, 0, 255)
            print(f"edgeB {edgeB}")
        case 'r':
            images[currentIndex].skew = constrain_value(images[currentIndex].skew, -1, -45, 45)
            print(f"skew {images[currentIndex].skew}")
        case 'w':
            images[currentIndex].translationY -= deltaTranslation
            print(f"translationY {images[currentIndex].translationY}")
        case 'f':
            images[currentIndex].skew = constrain_value(images[currentIndex].skew, 1, -45, 45)
            print(f"skew {images[currentIndex].skew}")
        case 's':
            images[currentIndex].translationY += deltaTranslation
            print(f"translationY {images[currentIndex].translationY}")
        case 'q':
            images[currentIndex].rotation = constrain_value(images[currentIndex].rotation, -1, -180, 180)
            print(f"rotation {images[currentIndex].rotation}")
        case 'a':
            images[currentIndex].translationX -= deltaTranslation
            print(f"translationX {images[currentIndex].translationX}")
        case 'e':
            images[currentIndex].rotation = constrain_value(images[currentIndex].rotation, 1, -180, 180)
            print(f"rotation {images[currentIndex].rotation}")
        case 'd':
            images[currentIndex].translationX += deltaTranslation
            print(f"translationX {images[currentIndex].translationX}")
        case 'z':
            images[currentIndex].zoom -= 0.05
            print(f"zoom {images[currentIndex].zoom}")
        case 'x':
            images[currentIndex].zoom += 0.05
            print(f"zoom {images[currentIndex].zoom}")
    update()

cv2.destroyAllWindows()