from PIL import Image
import numpy as np
import os
import base64
from io import BytesIO

class ImageProcessor:
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def save_uploaded_file(file, upload_folder):
        filename = file.filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filepath
    
    @staticmethod
    def preprocess_image(image_path, target_size=(512, 512)):
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        img_array = np.array(img)
        
        return img_array
    
    @staticmethod
    def image_to_base64(image_path):
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    @staticmethod
    def get_image_info(image_path):
        img = Image.open(image_path)
        return {
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.width,
            'height': img.height
        }
    
    @staticmethod
    def enhance_image(image_path):
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        from PIL import ImageEnhance
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)
        
        return img
