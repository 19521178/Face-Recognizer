import cv2
from .extractor import FaceEmbeddingExtractor
from .repository import QdrantRepository


class Predictor:
    def __init__(self):
        self.extractor = FaceEmbeddingExtractor()
        self.repository = QdrantRepository("faces")

    def predict(self, image_path):
        result: dict = {}

        faces = self.extractor.detect(image_path)

        main_face = self.extractor.get_biggest_face(faces)

        result["bbox"] = main_face.bbox
        result["detection_score"] = main_face.det_score
        
        [closest_point] = self.repository.search(main_face.embedding, limit=1)
        if closest_point is None or closest_point.score < 0.4:
            result["recognition_score"] = 0
            result["name"] = "Unknown"
        else:
            result["recognition_score"] = closest_point.score
            result["name"] = closest_point.payload["name"]
            result["payload"] = closest_point.payload
        return result
    
    def render_result(self, result, image_path):
        img = cv2.imread(image_path)
        cv2.rectangle(img, (int(result["bbox"][0]), int(result["bbox"][1])), (int(result["bbox"][2]), int(result["bbox"][3])), (0, 255, 0), thickness=2)
        return img

        
if __name__ == "__main__":
    predictor = Predictor()
    image_path = "../scripts/images_test/crowded.jpg"
    result = predictor.predict(image_path)
    img = predictor.render_result(result, image_path)
    cv2.imshow("result", img)
    cv2.waitKey(0)

