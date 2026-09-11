"""
Download authentic, working test images of diverse crops for local testing.
Saves all images into sample_test_images/ at repository root.
"""
from pathlib import Path
import httpx
from PIL import Image
import io

ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT_DIR / "sample_test_images"
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

PV_BASE = "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color"

IMAGE_TARGETS = [
    {
        "filename": "tomato_early_blight.jpg",
        "crop": "Tomato",
        "condition": "Early Blight",
        "url": f"{PV_BASE}/Tomato___Early_blight/0012b9d2-2130-4a06-a834-b1f3af34f57e___RS_Erly.B%208389.JPG"
    },
    {
        "filename": "tomato_healthy.jpg",
        "crop": "Tomato",
        "condition": "Healthy Leaf",
        "url": f"{PV_BASE}/Tomato___healthy/000146ff-92a4-4db6-90ad-8fce2ae4fddd___GH_HL%20Leaf%20259.1.JPG"
    },
    {
        "filename": "potato_early_blight.jpg",
        "crop": "Potato",
        "condition": "Early Blight",
        "url": f"{PV_BASE}/Potato___Early_blight/001187a0-57ab-4329-baff-e7246a9edeb0___RS_Early.B%208178.JPG"
    },
    {
        "filename": "potato_late_blight.jpg",
        "crop": "Potato",
        "condition": "Late Blight",
        "url": f"{PV_BASE}/Potato___Late_blight/0051e5e8-d1c4-4a84-bf3a-a426cdad6285___RS_LB%204640.JPG"
    },
    {
        "filename": "corn_maize_common_rust.jpg",
        "crop": "Maize",
        "condition": "Common Rust",
        "url": f"{PV_BASE}/Corn_(maize)___Common_rust_/RS_Rust%201564.JPG"
    },
    {
        "filename": "grape_black_rot.jpg",
        "crop": "Grape",
        "condition": "Black Rot",
        "url": f"{PV_BASE}/Grape___Black_rot/00090b0f-c140-4e77-8d20-d39f67b75fcc___FAM_B.Rot%200376.JPG"
    },
    {
        "filename": "bell_pepper_bacterial_spot.jpg",
        "crop": "Pepper",
        "condition": "Bacterial Spot",
        "url": f"{PV_BASE}/Pepper,_bell___Bacterial_spot/0022d6b7-d47c-4ee2-ae9a-392a53f48647___JR_B.Spot%208964.JPG"
    },
    {
        "filename": "apple_scab.jpg",
        "crop": "Apple",
        "condition": "Apple Scab",
        "url": f"{PV_BASE}/Apple___Apple_scab/00075aa8-d81a-4184-8541-b692b78d398a___FREC_Scab%203335.JPG"
    },
    {
        "filename": "strawberry_leaf_scorch.jpg",
        "crop": "Strawberry",
        "condition": "Leaf Scorch",
        "url": f"{PV_BASE}/Strawberry___Leaf_scorch/0024203d-6e4c-490f-b9a8-e5926df0b76e___RS_L.Scorch%200795.JPG"
    },
    {
        "filename": "peach_bacterial_spot.jpg",
        "crop": "Peach",
        "condition": "Bacterial Spot",
        "url": f"{PV_BASE}/Peach___Bacterial_spot/00130039-8425-42e9-9dd9-15aead7271ff___Rut._Bact.S%203421.JPG"
    },
    {
        "filename": "rice_leaf_blight.jpg",
        "crop": "Rice",
        "condition": "Bacterial Leaf Blight",
        "url": "https://huggingface.co/datasets/Solshine/Rice_Diagnosis_Leaf_Images_FromKaggle/resolve/main/raw/image_folders/auto/rice_leaf_diseases/Bacterial%20leaf%20blight/DSC_0365.JPG"
    },
    {
        "filename": "wheat_leaf_rust.jpg",
        "crop": "Wheat",
        "condition": "Leaf Rust",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Wheat_leaf_rust_on_wheat.jpg"
    },
    {
        "filename": "cotton_leaf.jpg",
        "crop": "Cotton",
        "condition": "Cotton Leaf",
        "url": "https://huggingface.co/datasets/Ashmita2000/Cotton_Leaves/resolve/main/Test/Aphids%20edited/1.jpg"
    },
    {
        "filename": "sugarcane_leaf.jpg",
        "crop": "Sugarcane",
        "condition": "Sugarcane Leaf",
        "url": "https://huggingface.co/datasets/Esmaeilkianii/Sugarcanegap/resolve/main/gap5.jpg"
    }
]


def download_images():
    print(f"Downloading {len(IMAGE_TARGETS)} authentic test images into {OUTPUT_DIR} ...\n")
    downloaded = []

    with httpx.Client(timeout=45.0, follow_redirects=True, headers=HEADERS) as client:
        for item in IMAGE_TARGETS:
            dest = OUTPUT_DIR / item["filename"]
            print(f"Downloading {item['crop']:<12} ({item['condition']}) -> {item['filename']} ...", end=" ", flush=True)
            try:
                resp = client.get(item["url"])
                if resp.status_code == 200 and len(resp.content) > 1000:
                    img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                    # Resize very large multi-megabyte images to reasonable testing dimensions
                    if img.width > 1200 or img.height > 1200:
                        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                    img.save(dest, format="JPEG", quality=92)
                    size_kb = round(dest.stat().st_size / 1024, 1)
                    print(f"[OK] {size_kb} KB, {img.width}x{img.height}")
                    downloaded.append({**item, "path": str(dest)})
                else:
                    print(f"[FAILED: HTTP {resp.status_code}]")
            except Exception as e:
                print(f"[ERROR: {e}]")

    print(f"\nCompleted: {len(downloaded)} / {len(IMAGE_TARGETS)} test images saved to {OUTPUT_DIR}")
    return downloaded


if __name__ == "__main__":
    download_images()
