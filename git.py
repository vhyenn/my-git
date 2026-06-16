import sys
import os
from pathlib import Path
from hashlib import blake2b
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
            
            h = blake2b(digest_size=20)
            h.update(blob)
            blob_hash = h.hexdigest()
            print(blob_hash)
        
        else:
            print("File Doesn't Exist")
    
    elif len(sys.argv) == 4 and sys.argv[3] == "-w":
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
            
            h = blake2b(digest_size=20)
            h.update(blob)
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
