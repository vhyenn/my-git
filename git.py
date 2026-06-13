import sys
import os
from pathlib import Path
from hashlib import blake2b
    
def check_sys():
    if len(sys.argv) < 2:
        sys.exit("Enter Command")
    
def init(): 
    full_path = os.getcwd() 
    
    #checking if git is already initialized
    if os.path.isdir(f"{full_path}/.git"):
        sys.exit("Already initialized")
    
    #Creating git folders
    else:
        create_folders(f"{full_path}/.git")
        create_folders(f"{full_path}/.git/objects")
        create_folders(f"{full_path}/.git/refs")
        with open(f"{full_path}/.git/HEAD", "a") as file:
            pass
        
        with open(f"{full_path}/.git/index", "a") as file:
            pass

def hash_object():
    if len(sys.argv) != 3:
        sys.exit("Enter a file you want to hash")

    if "/" in sys.argv[2]:
        full_path = sys.argv[2]
        if not os.path.isfile(full_path):
            sys.exit("Specified path/file does not exist")
        else: 
            
            file_name= Path(sys.argv[2])
            
    else:
        current_directory = os.getcwd() 
        file_path = f"{current_directory}/{sys.argv[2]}"
        if not os.path.isfile(file_path):
            sys.exit("Specified file does not exist")
        
        else:
            file_name = sys.argv[2]
    
    file_stats = os.stat(file_name)
    file_size = file_stats.st_size
    blob = f"blob {file_size}\0"
    blob = blob.encode()
    try:
        with open(file_name, "rb") as file:
            file_content = file.read()
            blob += file_content
    
    except IOError:
        sys.exit("File not found")
    
    h = blake2b()
    h.update(blob)
    blob_hash = h.hexdigest()
    print(blob_hash)
        



def create_folders(path):
    os.mkdir(f"{path}")


def main():
    check_sys()
    if sys.argv[1] == "init":
        init()
    
    if sys.argv[1] == "hash-object":
        hash_object()
    


if __name__ == "__main__":
    main()
