import os,requests,shutil,zipfile,io,time
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
    
def find_top_level_dirname(zipfile):
    items = zipfile.namelist()

    tlds = [item for item in items if item.endswith("/") and item.count("/") == 1]

    if tlds:
        return tlds[0]

def apply_update(zip_file):
    top_level_dirname = ""

    print("Applying update/installation...")
    for i in tqdm(range(100), desc="Unzipping files", ascii=" █", colour="green"):
        time.sleep(0.02)  # Simulate a cool loading effect
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        extracted_folder_dirname = find_top_level_dirname(zip_ref)
        zip_ref.extractall(os.getcwd())  # Extract in the current directory 
    print("Update applied successfully!")

    return extracted_folder_dirname

def shift_up_dir_tree(tldn):
    tldn = os.path.abspath(tldn)

    for item in os.listdir(tldn):
        origin = os.path.join(tldn, item)
        dest = os.path.join(os.getcwd(), item)

        shutil.move(origin, dest)
    
    shutil.rmtree(tldn, ignore_errors=True) # ignore errors cos this isn't really important

def install_deps():
    assert os.path.exists(os.path.abspath(os.path.join(os.getcwd(), "requirements.txt")))
    print("Installing necessary dependencies...")
    os.system(f"pip install \"{os.path.abspath(os.path.join(os.getcwd(), 'requirements.txt'))}\"")

def update():
    zip_file = download_update(bro)
    if zip_file:
        tldn = apply_update(zip_file)
        shift_up_dir_tree(tldn)
        install_deps()
    else:
        print("Update failed.")

if __name__ == "__main__":
    update()
    time.sleep(3)