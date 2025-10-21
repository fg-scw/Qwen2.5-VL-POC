#!/usr/bin/env python3
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from typing import List, Optional
import csv
import time
from datetime import datetime
from tqdm import tqdm

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))
MAX_RETRIES = 3


class VisionClient:
    def __init__(self, api_url: str = API_URL, timeout: int = TIMEOUT):
        self.api_url = api_url
        self.timeout = timeout
        self.results = []
    
    def analyze_image(self, image_path: str, prompt: str = None, retries: int = MAX_RETRIES) -> Optional[dict]:
        for attempt in range(retries):
            try:
                with open(image_path, "rb") as f:
                    files = {"file": f}
                    params = {}
                    if prompt:
                        params["prompt"] = prompt
                    
                    response = requests.post(
                        f"{self.api_url}/analyze-image",
                        files=files,
                        params=params,
                        timeout=self.timeout
                    )
                
                if response.status_code == 200:
                    return response.json()
                elif attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def batch_analyze(self, image_paths: List[str], prompt: str = None) -> List[dict]:
        results = []
        print(f"Processing {len(image_paths)} images...")
        
        for image_path in tqdm(image_paths, desc="Analysis"):
            result = self.analyze_image(image_path, prompt)
            if result:
                results.append({
                    "image": image_path,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
            time.sleep(0.5)
        
        self.results = results
        return results
    
    def export_json(self, filepath: str = "results.json"):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"Exported: {filepath}")
    
    def export_csv(self, filepath: str = "results.csv"):
        if not self.results:
            print("No results to export")
            return
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Image", "Analysis", "Time (s)", "Timestamp"])
            
            for item in self.results:
                writer.writerow([
                    item["image"],
                    item["result"]["analysis"],
                    item["result"].get("inference_time", "N/A"),
                    item["timestamp"]
                ])
        
        print(f"Exported: {filepath}")


def main():
    client = VisionClient()
    
    image_dir = Path("images")
    if image_dir.exists():
        images = list(image_dir.glob("*.{jpg,jpeg,png}"))
        if images:
            results = client.batch_analyze(
                [str(img) for img in images],
                prompt="Describe this image"
            )
            client.export_json("results.json")
            client.export_csv("results.csv")


if __name__ == "__main__":
    main()