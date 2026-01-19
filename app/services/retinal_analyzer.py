from PIL import Image
import numpy as np
import cv2
from skimage import exposure, filters, morphology
from skimage.feature import canny
from scipy import ndimage as ndi

class RetinalImageAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = None
        self.gray_image = None
        self.features = {}
        
    def load_image(self):
        self.image = np.array(Image.open(self.image_path).convert('RGB'))
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        
    def analyze(self):
        self.load_image()
        
        self.features['image_quality'] = self._assess_image_quality()
        self.features['blood_vessels'] = self._analyze_blood_vessels()
        self.features['optic_disc'] = self._analyze_optic_disc()
        self.features['macula'] = self._analyze_macula()
        self.features['lesions'] = self._detect_lesions()
        self.features['exudates'] = self._detect_exudates()
        self.features['hemorrhages'] = self._detect_hemorrhages()
        self.features['microaneurysms'] = self._detect_microaneurysms()
        
        return self.features
    
    def _assess_image_quality(self):
        sharpness = cv2.Laplacian(self.gray_image, cv2.CV_64F).var()
        brightness = np.mean(self.gray_image)
        contrast = np.std(self.gray_image)
        
        quality_score = {
            'sharpness': float(sharpness),
            'brightness': float(brightness),
            'contrast': float(contrast),
            'quality': 'good' if sharpness > 100 and 50 < brightness < 200 else 'poor'
        }
        
        return quality_score
    
    def _analyze_blood_vessels(self):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(self.gray_image)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(enhanced, cv2.MORPH_TOPHAT, kernel)
        
        _, binary = cv2.threshold(morph, 15, 255, cv2.THRESH_BINARY)
        
        vessel_density = np.sum(binary > 0) / binary.size * 100
        
        vessel_analysis = {
            'vessel_density': float(vessel_density),
            'vessel_pattern': self._analyze_vessel_pattern(binary),
            'abnormalities': self._detect_vessel_abnormalities(binary)
        }
        
        return vessel_analysis
    
    def _analyze_vessel_pattern(self, binary):
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return '无法检测到血管'
        
        avg_length = np.mean([len(c) for c in contours])
        
        if avg_length < 50:
            return '血管稀疏'
        elif avg_length < 150:
            return '血管正常'
        else:
            return '血管密集'
    
    def _detect_vessel_abnormalities(self, binary):
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        abnormalities = []
        
        for contour in contours:
            if len(contour) > 200:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                if aspect_ratio > 3 or aspect_ratio < 0.33:
                    abnormalities.append('血管形态异常')
        
        return abnormalities if abnormalities else ['无明显异常']
    
    def _analyze_optic_disc(self):
        h, w = self.gray_image.shape
        center_x, center_y = w // 2, h // 2
        
        roi_size = 200
        x1 = max(0, center_x - roi_size // 2)
        x2 = min(w, center_x + roi_size // 2)
        y1 = max(0, center_y - roi_size // 2)
        y2 = min(h, center_y + roi_size // 2)
        
        roi = self.gray_image[y1:y2, x1:x2]
        
        _, disc_binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        disc_area = np.sum(disc_binary > 0)
        disc_ratio = disc_area / (roi_size * roi_size) * 100
        
        disc_analysis = {
            'detected': disc_ratio > 1,
            'area_ratio': float(disc_ratio),
            'condition': '正常' if 5 < disc_ratio < 15 else '异常',
            'edges': self._analyze_disc_edges(roi)
        }
        
        return disc_analysis
    
    def _analyze_disc_edges(self, roi):
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size * 100
        
        if edge_density < 5:
            return '边缘模糊'
        elif edge_density < 15:
            return '边缘清晰'
        else:
            return '边缘不规则'
    
    def _analyze_macula(self):
        h, w = self.gray_image.shape
        center_x, center_y = w // 2, h // 2
        
        macula_x = center_x + w // 6
        macula_y = center_y
        
        roi_size = 100
        x1 = max(0, macula_x - roi_size // 2)
        x2 = min(w, macula_x + roi_size // 2)
        y1 = max(0, macula_y - roi_size // 2)
        y2 = min(h, macula_y + roi_size // 2)
        
        macula_roi = self.gray_image[y1:y2, x1:x2]
        
        macula_brightness = np.mean(macula_roi)
        overall_brightness = np.mean(self.gray_image)
        
        macula_analysis = {
            'brightness_ratio': float(macula_brightness / overall_brightness),
            'condition': '正常' if 0.8 < macula_brightness / overall_brightness < 1.2 else '异常',
            'texture': self._analyze_macula_texture(macula_roi)
        }
        
        return macula_analysis
    
    def _analyze_macula_texture(self, roi):
        texture_var = np.var(roi)
        
        if texture_var < 500:
            return '纹理均匀'
        elif texture_var < 1500:
            return '纹理正常'
        else:
            return '纹理异常'
    
    def _detect_lesions(self):
        lesions = {
            'cotton_wool_spots': self._detect_cotton_wool_spots(),
            'neovascularization': self._detect_neovascularization()
        }
        
        return lesions
    
    def _detect_cotton_wool_spots(self):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(self.gray_image)
        
        _, binary = cv2.threshold(enhanced, 200, 255, cv2.THRESH_BINARY)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cotton_wool_count = len([c for c in contours if cv2.contourArea(c) > 100])
        
        return {
            'detected': cotton_wool_count > 0,
            'count': cotton_wool_count,
            'severity': '无' if cotton_wool_count == 0 else '轻度' if cotton_wool_count < 5 else '重度'
        }
    
    def _detect_neovascularization(self):
        hsv = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
        
        red_lower1 = np.array([0, 100, 100])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([160, 100, 100])
        red_upper2 = np.array([180, 255, 255])
        
        red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        neovascular_count = len([c for c in contours if cv2.contourArea(c) > 50])
        
        return {
            'detected': neovascular_count > 0,
            'count': neovascular_count,
            'severity': '无' if neovascular_count == 0 else '轻度' if neovascular_count < 10 else '重度'
        }
    
    def _detect_exudates(self):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(self.gray_image)
        
        _, binary = cv2.threshold(enhanced, 220, 255, cv2.THRESH_BINARY)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        exudate_count = len([c for c in contours if cv2.contourArea(c) > 50])
        total_area = sum([cv2.contourArea(c) for c in contours])
        
        return {
            'detected': exudate_count > 0,
            'count': exudate_count,
            'total_area': float(total_area),
            'severity': '无' if exudate_count == 0 else '轻度' if total_area < 5000 else '重度'
        }
    
    def _detect_hemorrhages(self):
        hsv = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
        
        dark_red_lower = np.array([0, 50, 20])
        dark_red_upper = np.array([10, 255, 100])
        
        dark_red_mask = cv2.inRange(hsv, dark_red_lower, dark_red_upper)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dark_red_mask = cv2.morphologyEx(dark_red_mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(dark_red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hemorrhage_count = len([c for c in contours if cv2.contourArea(c) > 30])
        total_area = sum([cv2.contourArea(c) for c in contours])
        
        return {
            'detected': hemorrhage_count > 0,
            'count': hemorrhage_count,
            'total_area': float(total_area),
            'severity': '无' if hemorrhage_count == 0 else '轻度' if total_area < 3000 else '重度'
        }
    
    def _detect_microaneurysms(self):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(self.gray_image)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        tophat = cv2.morphologyEx(enhanced, cv2.MORPH_TOPHAT, kernel)
        
        _, binary = cv2.threshold(tophat, 30, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        microaneurysm_count = len([c for c in contours if 5 < cv2.contourArea(c) < 100])
        
        return {
            'detected': microaneurysm_count > 0,
            'count': microaneurysm_count,
            'severity': '无' if microaneurysm_count == 0 else '轻度' if microaneurysm_count < 20 else '重度'
        }
