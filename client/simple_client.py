#!/usr/bin/env python3
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))


def analyze_image(image_path: str, prompt: str = None):
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"Error: File '{image_path}' not found")
        return None
    
    try:
        print(f"Sending image: {image_path.name}")
        
        with open(image_path, "rb") as f:
            files = {"file": f}
            params = {}
            if prompt:
                params["prompt"] = prompt
            
            response = requests.post(
                f"{API_URL}/analyze-image",
                files=files,
                params=params,
                timeout=TIMEOUT
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to {API_URL}")
        return None
    except requests.exceptions.Timeout:
        print(f"Error: Timeout after {TIMEOUT}s")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_client.py <image_path> [prompt]")
        print("Example: python simple_client.py photo.jpg 'What is this?'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = analyze_image(image_path, prompt)
    
    if result and result.get("success"):
        print("\n" + "="*60)
        print("ANALYSIS RESULT")
        print("="*60)
        print(f"Analysis:\n{result['analysis']}")
        print(f"\nTime: {result['inference_time']:.2f}s")
        print("="*60)


if __name__ == "__main__":
    main()