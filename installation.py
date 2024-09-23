import os,requests,zipfile,io,time
from tqdm import tqdm

global bro 
bro = f"https://github.com/FunWithAlbiYT/lucoin_client/archive/refs/heads/main.zip"

def download_update(url):
    print("Fetching latest update...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        zip_file = io.BytesIO() 
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            zip_file.write(data)
        progress_bar.close()
        if total_size != 0 and progress_bar.n != total_size:
            print("ERROR: Something went wrong during the download.")
            return None
        print("Download successful!")
        return zip_file
    else:
        print("Failed to download the update.")
        return None
    
def apply_update(zip_file):
    print("Applying update/installation...")
    for i in tqdm(range(100), desc="Unzipping files", ascii=" █", colour="green"):
        time.sleep(0.02)  # Simulate a cool loading effect
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(os.getcwd())  # Extract in the current directory 
    print("Update applied successfully!")

def i_want_to_prove_dad_is_wrong():
    zip_file = download_update(bro)
    if zip_file:
        apply_update(zip_file)
    else:
        print("Update failed.")
i_want_to_prove_dad_is_wrong()
time.sleep(3)
