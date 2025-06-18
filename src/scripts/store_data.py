import json
import os
from ..services.extractor import FaceEmbeddingExtractor
from ..services.repository import QdrantRepository

def store_data():
    repo = QdrantRepository("faces")
    extractor = FaceEmbeddingExtractor()
    extracted_folders: list = get_extracted_folder()

    image_idx = 200000
    # best_people_folder = json.load(open('best_people_folder.json'))

    for folder in sorted(os.listdir('images')):
        # if (folder not in best_people_folder):
        #     continue

        print("\n---Image idx: ", image_idx)
        if (folder in extracted_folders):
            print("Skipping extracted folder " + folder)
            
            image_idx += len(os.listdir(os.path.join('images', folder))) - 1
            continue

        print(f"Storing data for {folder}")
        image_paths = sorted([os.path.join('images', folder, img) for img in os.listdir(os.path.join('images', folder)) if img != 'info.json'])

        embeddings = []
        for img in image_paths:
            try:
                embeddings.append(extractor.extract(img))
            except Exception as e:
                if str(e) == f"Error processing {img}: No faces detected":
                    print(f"Skipping {img} as no faces detected")
                elif str(e) == "No faces detected after 3 attempts":
                    print(f"Skipping {img} as no faces detected")
                elif str(e) == f"Final attempt failed for {img}: Image processing failed: image file is truncated":    
                    print(f"Skipping {img} as image file is truncated")                
                elif str(e) == f"Final attempt failed for {img}: Image processing failed: could not create decoder object":    
                    #images/bkt0_Thế_Hải/0.jpg
                    print(f"Skipping {img} as could not create decoder object")
                else:
                    raise

        payload = json.load(open(os.path.join('images', folder, 'info.json')))
        repo.store(embeddings, [image_idx + idx for idx in range(len(embeddings))], [payload])

        extracted_folders.append(folder)
        save_extracted_folder(extracted_folders)

        image_idx += len(embeddings)

def get_extracted_folder() -> list:
    try:
        extracted_folder = json.load(open('extracted_folder.json'))
    except FileNotFoundError:
        extracted_folder = []

    return extracted_folder

def save_extracted_folder(extracted_folders):
    with open('extracted_folder.json', 'w') as f:
        json.dump(extracted_folders, f, indent=4)

if __name__ == "__main__":
    store_data()