import cv2
import json

class ImageData:
    def __init__(self, filepath):
        self.filepath = filepath
        self.image = cv2.imread(filepath)
        self.translationX = 0
        self.translationY = 0
        self.rotation = 0
        self.skew = 0
        self.zoom = 0

    def to_dict(self):
        return {
            'filepath': self.filepath,
            'translationX': self.translationX,
            'translationY': self.translationY,
            'rotation': self.rotation,
            'skew': self.skew,
            'zoom': self.zoom
        }

    @classmethod
    def from_dict(cls, data):
        image_data = cls(data['filepath'])
        image_data.translationX = data['translationX']
        image_data.translationY = data['translationY']
        image_data.rotation = data['rotation']
        image_data.skew = data['skew']
        image_data.zoom = data['zoom']
        return image_data

def save_image_data(images):
    data = [img.to_dict() for img in images]
    with open('image_data.json', 'w') as f:
        json.dump(data, f, indent=2)

def load_image_data():
    try:
        with open('image_data.json', 'r') as f:
            data = json.load(f)
            return [ImageData.from_dict(img_data) for img_data in data]
    except FileNotFoundError:
        # Return default images if no saved data exists
        return [
            ImageData('data/watertower01.jpg'),
            ImageData('data/watertower02.jpg'),
            ImageData('data/watertower03.jpg')
        ]
