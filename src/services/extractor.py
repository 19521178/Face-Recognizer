import insightface
import cv2
import numpy as np
from PIL import Image, ImageEnhance

class FaceEmbeddingExtractor:
    def __init__(self, use_gpu=False, detection_threshold=0.2, min_face_size=20):
        self.model = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'] if use_gpu else ['CPUExecutionProvider'])
        self.model.prepare(
            ctx_id=0 if use_gpu else -1,
            det_size=(640, 640),
            det_thresh=detection_threshold
        )
        self.min_face_size = min_face_size

    def preprocess_image(self, img_path):
        """Enhance image quality for better face detection"""
        try:
            # Read image with multiple fallbacks
            img = cv2.imread(img_path)
            if img is None:
                # Try alternative reading methods
                img = Image.open(img_path).convert('RGB')
                img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # Auto-orient based on EXIF
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            img = self.auto_rotate(img)
            
            # Enhance low-quality images
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise Exception(f"Image processing failed: {str(e)}")

    def auto_rotate(self, img):
        """Fix image orientation based on EXIF"""
        try:
            exif = img.getexif()
            if exif:
                orientation = exif.get(0x0112, 1)
                # Rotate based on orientation tag
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except:
            pass
        return img

    def get_biggest_face(self, faces):
        """Filter faces by size and quality"""
        valid_faces = [f for f in faces 
                      if f.bbox[2] - f.bbox[0] > self.min_face_size and 
                         f.bbox[3] - f.bbox[1] > self.min_face_size]
        
        if not valid_faces:
            return None
            
        return sorted(valid_faces, 
                     key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]), 
                     reverse=True)[0]

    def detect(self, img_path, max_attempts=3):
        """Robust extraction with multiple attempts and preprocessing"""
        for attempt in range(max_attempts):
            try:
                img = self.preprocess_image(img_path)
                faces = self.model.get(img)
                
                if faces and len(faces) > 0:
                    return faces
                
                # Try different strategies on retries
                if attempt == 1:
                    # Upscale small images
                    img = cv2.resize(img, (0,0), fx=1.5, fy=1.5)
                    faces = self.model.get(img)
                elif attempt == 2:
                    # Convert to grayscale (better for some models)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    faces = self.model.get(img)
                    
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise Exception(f"Final attempt failed for {img_path}: {str(e)}")
        
        raise Exception(f"No faces detected after {max_attempts} attempts")
    
    def extract(self, img_path, max_attempts=3):
        faces = self.detect(img_path, max_attempts)

        main_face = self.get_biggest_face(faces)
        return main_face.embedding