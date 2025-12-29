# import json
# import requests
# from pathlib import Path
# from tqdm import tqdm
#
# API_URL = "http://127.0.0.1:8000/equipment/create"
# DATASET_DIR = Path("./metallurgy")
# IMAGES_DIR = DATASET_DIR / "images"
# DATA_FILE = DATASET_DIR / "data.json"
#
#
# def upload_item(item):
#         data = {
#             "type": item["type"],
#             "name": item["name"],
#             "description": item["description"],
#             "price": item["price"],
#             "power": item["power"],
#             "year": item["year"],
#         }
#
#         response = requests.post(API_URL, data=data)
#
#         if response.status_code != 200:
#             print("❌ Ошибка:", response.text)
#         else:
#             print("✅ Загружено:", item["name"])
#
#
# def main():
#     with open(DATA_FILE, "r", encoding="utf-8") as f:
#         dataset = json.load(f)
#
#     for item in tqdm(dataset):
#         upload_item(item)
#
#
# # if __name__ == "__main__":
# #     main()
