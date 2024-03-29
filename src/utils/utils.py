import os
import json
import zipfile
from urllib.request import urlretrieve

def calculate_area(bbox: list) -> int:
    """Calculates the area of a bounding box."""
    width = max(bbox[2] - bbox[0], 0)
    height = max(bbox[3] - bbox[1], 0)
    return width * height

def intersect_bbox(bbox1: list, bbox2: list) -> list:
    """Calculates the intersection of two bounding boxes."""
    xA = max(bbox1[0], bbox2[0])
    yA = max(bbox1[1], bbox2[1])
    xB = min(bbox1[2], bbox2[2])
    yB = min(bbox1[3], bbox2[3])
    return [xA, yA, xB, yB]

def calculate_intersect_area(bbox1: list, bbox2: list) -> int:
    """Calculates the intersected area between given bounding boxes."""
    intersect_bbox = intersect_bbox(bbox1, bbox2)
    return calculate_area(intersect_bbox)

def get_bbox_inside_image(label_bbox: list, image_bbox: list) -> list:
    """Corrects label_bbox to ensure it's inside the image bbox."""
    return intersect_bbox(label_bbox, image_bbox)

def list_annotation_paths(directory: str, ignore_background_only: bool = True) -> list:
    """Lists JSON file paths in a directory, optionally ignoring background-only images."""
    image_bbox = [0, 0, 1080, 1920]
    file_paths = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                try:
                    with open(os.path.join(root, file), "r") as f:
                        data = json.load(f)
                        label_bbox = [min(pos[0] for pos in data["quad"]),
                                      min(pos[1] for pos in data["quad"]),
                                      max(pos[0] for pos in data["quad"]),
                                      max(pos[1] for pos in data["quad"])]
                        if ignore_background_only and calculate_intersect_area(label_bbox, image_bbox) < 1:
                            continue
                        file_paths.append(os.path.join(root, file).replace("\\", "/"))
                except Exception as e:
                    print(f"Error processing {file}: {e}")
                    continue

    print(f"There are {len(file_paths)} image files in folder {os.path.basename(directory)}.")
    return file_paths

def create_dir(dir_path: str):
    """Creates a directory if it doesn't exist."""
    os.makedirs(dir_path, exist_ok=True)

class DownloadProgressBar(tqdm):
    """A progress bar for file downloads using tqdm."""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download(url: str, save_dir: str):
    """Downloads a file from a URL to a specified directory."""
    create_dir(save_dir)
    file_path = os.path.join(save_dir, url.split("/")[-1])
    with DownloadProgressBar(unit="B", unit_scale=True, miniters=1, desc=url.split("/")[-1]) as t:
        urlretrieve(url, filename=file_path, reporthook=t.update_to)

def unzip(file_path: str, dest_dir: str):
    """Unzips a .zip file to a specified directory."""
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)