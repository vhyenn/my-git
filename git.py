import sys
import os
from pathlib import Path
import hashlib
import zlib
    
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
        create_folders(os.path.join(full_path, ".git"))
        create_folders(os.path.join(full_path, ".git", "objects"))
        create_folders(os.path.join(full_path, ".git", "refs"))
        with open(f"{full_path}/.git/HEAD", "a") as file:
            pass
        
        with open(f"{full_path}/.git/index", "a") as file:
            pass

def hash_object():
    if len(sys.argv) < 3:
        sys.exit("Enter a file you want to hash")
    
    
    if len(sys.argv) == 3:
        
        file_name = Path(sys.argv[2])

        if file_name.is_file():

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
            
            h = hashlib.sha1(blob)
            blob_hash = h.hexdigest()
            print(blob_hash)
        
        else:
            print("File Doesn't Exist")
    
    elif len(sys.argv) == 4 and sys.argv[2] == "-w":
        file_name = Path(sys.argv[3])

        if file_name.is_file():
            
            
            
            

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
            
            
            h = hashlib.sha1(blob)
            blob_hash = h.hexdigest()
            

            current = Path.cwd()
            current_length = str(current).split("\\")
            

            for i in range(len(current_length)):
                git_objects = current / ".git" / "objects"
                if git_objects.is_dir():
                    break

                current = current.parent
            else:
                sys.exit("Git not initialized")

            hash_string = str(blob_hash)
            folder1 = hash_string[:2]
            file1 = hash_string[2:]
            hash_file_path = os.path.join(git_objects, folder1, file1)
            compressed_blob = zlib.compress(blob)
            if not os.path.isdir(os.path.join(git_objects, folder1)):
                create_folders(os.path.join(git_objects, folder1))
            if not os.path.isfile(os.path.join(git_objects, folder1, file1)):
                with open(hash_file_path, "wb") as file:
                    file.write(compressed_blob)

        else:
            print("File Doesn't Exist")
        
def cat_file():
    if len(sys.argv) < 3:
        sys.exit("Enter a file you want to hash")
    
    if len(sys.argv) != 4:
        sys.exit("No Hash Object Mentioned")
    
    if sys.argv[2] not in ["-p", "-t", "-s", "-e"]:
        sys.exit("No Flag Mentioned")
    
    folder1 = str(sys.argv[3])[:2]
    file1 = str(sys.argv[3])[2:]
    
    current_dir = Path.cwd()
    current_dir_len = str(current_dir).split("\\")

    for i in range(len(current_dir_len)):
        pathh = current_dir / ".git" / "objects" / folder1 / file1
        if pathh.is_file():
            break
        
        current_dir = current_dir.parent
    else:
        sys.exit(f"No Hash Object named {sys.argv[3]} Found in Current Directory")
    
    with open(pathh, "rb") as file:
        file_content = file.read()
        x = zlib.decompress(file_content)
        
        

        for i in range(len(x)):
            if x[i] == 0:
                split_number = i
                break
        header = x[:split_number]
        header = header.decode()
        typee, sizee = header.split(" ")
        
    
    if sys.argv[2] == "-p":
        try:
            content = x[split_number + 1:].decode()
        except UnicodeDecodeError:
            sys.exit("Couldn't Fetch it as its not text")
        print(content)
        
        
        

    elif sys.argv[2] == "-t":
        print(typee)

    
    elif sys.argv[2] == "-s":
        print(sizee)
    
    elif sys.argv[2] == "-e": 
        print("Exists")
    
    else:
        print("Not a Valid Flag")
    
def create_folders(path):
    os.mkdir(f"{path}")


def main():
    check_sys()
    if sys.argv[1] == "init":
        init()
    
    elif sys.argv[1] == "hash-object":
        hash_object()
    
    elif sys.argv[1] == "cat-file":
        cat_file()
    
    else:
        sys.exit("Not a valid command")
    


if __name__ == "__main__":
    main()
