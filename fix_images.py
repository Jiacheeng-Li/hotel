import os
import requests
import sqlite3
import random

# Setup directories
IMG_DIR = os.path.join("hotelweb", "static", "img", "hotels")
os.makedirs(IMG_DIR, exist_ok=True)
DB_PATH = os.path.join("hotelweb", "instance", "hotel.db")

# URLs found in the DB (some might be known broken)
# I'll put the known broken one last or handle 404s
URLS = [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1524936964167-d8679f40076a?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1625244724120-1fd1d34d00f6?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1571896349842-6e635aa13971?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80"
]

downloaded_images = []

print("Starting download...")
for i, url in enumerate(URLS):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filename = f"hotel_{i}.jpg"
            filepath = os.path.join(IMG_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            downloaded_images.append(f"/static/img/hotels/{filename}")
            print(f"Downloaded {filename}")
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

if not downloaded_images:
    print("No images downloaded! Exiting.")
    exit(1)

print(f"Successfully downloaded {len(downloaded_images)} images.")

# Update Database
print("Updating database...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all hotels
cursor.execute("SELECT id FROM hotel")
hotels = cursor.fetchall()

for hotel_id in hotels:
    # Assign a random image from the downloaded set
    new_image = random.choice(downloaded_images)
    cursor.execute("UPDATE hotel SET image_url = ? WHERE id = ?", (new_image, hotel_id[0]))

conn.commit()
conn.close()
print("Database updated.")
