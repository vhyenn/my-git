import sys
import os
from pathlib import Path
import hashlib
import zlib
from collections import OrderedDict


# Ensure the user entered a git command
def check_sys():
    if len(sys.argv) < 2:
        sys.exit("Enter Command")


# Initialize a new .git directory
def init():
    full_path = os.getcwd()

    # Prevent initializing an already existing repository
    if os.path.isdir(f"{full_path}/.git"):
        sys.exit("Already initialized")

    # Create the basic Git directory structure
    else:
        create_folders(os.path.join(full_path, ".git"))
        create_folders(os.path.join(full_path, ".git", "objects"))
        create_folders(os.path.join(full_path, ".git", "refs"))

        # Empty HEAD file
        with open(f"{full_path}/.git/HEAD", "a") as file:
            pass

        # Simple text-based index used by this project
        with open(f"{full_path}/.git/index", "a") as file:
            pass


# Mimics `git hash-object`
# Creates a blob object and optionally stores it
def hash_object():

    if len(sys.argv) < 3:
        sys.exit("Enter a file you want to hash")

    if len(sys.argv) > 4:
        sys.exit("Too many arguments")

    if len(sys.argv) == 4 and sys.argv[2] != "-w":
        sys.exit("Not a valid flag")

    # Only print the SHA-1 hash
    if len(sys.argv) == 3:

        file_name = Path(sys.argv[2])

        blob_hash, blob, raw_bytes = create_hash(file_name)
        print(blob_hash)

    # Write the blob into .git/objects
    elif len(sys.argv) == 4 and sys.argv[2] == "-w":

        file_name = Path(sys.argv[3])

        blob_hash, blob, raw_bytes = create_hash(file_name)

        write_in_hash(blob_hash, blob)


# Mimics `git cat-file`
# Reads an object from .git/objects and displays information about it
def cat_file():

    if len(sys.argv) < 3:
        sys.exit("Enter a file you want to hash")

    if len(sys.argv) != 4:
        sys.exit("No Hash Object Mentioned")

    if sys.argv[2] not in ["-p", "-t", "-s", "-e"]:
        sys.exit("No Flag Mentioned")

    # Git stores objects as:
    # .git/objects/aa/bbbbb....
    folder1 = str(sys.argv[3])[:2]
    file1 = str(sys.argv[3])[2:]

    # Walk upwards until a .git directory is found
    current_dir = Path.cwd()
    current_dir_len = str(current_dir).split("\\")

    for i in range(len(current_dir_len)):
        pathh = current_dir / ".git" / "objects" / folder1 / file1
        if pathh.is_file():
            break

        current_dir = current_dir.parent
    else:
        sys.exit(f"No Hash Object named {sys.argv[3]} Found in Current Directory")

    # Read and decompress the stored object
    with open(pathh, "rb") as file:

        file_content = file.read()
        x = zlib.decompress(file_content)

        # Blob format:
        # blob <size>\0<contents>
        for i in range(len(x)):
            if x[i] == 0:
                split_number = i
                break

        header = x[:split_number]

        header = header.decode()
        typee, sizee = header.split(" ")

    # Print blob contents
    if sys.argv[2] == "-p":
        try:
            content = x[split_number + 1:].decode()
        except UnicodeDecodeError:
            sys.exit("Couldn't Fetch it as its not text")

        sys.exit(content)

    # Print object type
    elif sys.argv[2] == "-t":
        sys.exit(typee)

    # Print object size
    elif sys.argv[2] == "-s":
        sys.exit(sizee)

    # Check object existence
    elif sys.argv[2] == "-e":
        sys.exit("Exists")

    else:
        sys.exit("Not a Valid Flag")


# Helper for creating directories
def create_folders(path):
    os.mkdir(f"{path}")


# Create a Git blob object in memory
# Returns:
# SHA1 hash
# blob bytes
# raw SHA1 bytes
def create_hash(file_name):

    if file_name.is_file():

        file_stats = os.stat(file_name)
        file_size = file_stats.st_size

        # Git hashes:
        # blob <size>\0<data>
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

        return blob_hash, blob, h.digest()

    else:
        sys.exit("File Doesn't Exist")


# Store a compressed object inside .git/objects
def write_in_hash(blob_hash, blob):

    current = Path.cwd()
    current_length = str(current).split("\\")

    # Find repository root
    for i in range(len(current_length)):

        git_objects = current / ".git" / "objects"

        if git_objects.is_dir():
            break

        current = current.parent

    else:
        sys.exit("Git not initialized")

    # Split SHA1 into directory + filename
    hash_string = str(blob_hash)
    folder1 = hash_string[:2]
    file1 = hash_string[2:]

    hash_file_path = os.path.join(git_objects, folder1, file1)

    compressed_blob = zlib.compress(blob)

    # Create object directory if necessary
    if not os.path.isdir(os.path.join(git_objects, folder1)):
        create_folders(os.path.join(git_objects, folder1))

    # Don't overwrite existing objects
    if not os.path.isfile(os.path.join(git_objects, folder1, file1)):
        with open(hash_file_path, "wb") as file:
            file.write(compressed_blob)


# Stage a file by writing its metadata into the index
def add():

    if len(sys.argv) < 3:
        sys.exit("Enter file you want to add")

    if len(sys.argv) > 3:
        sys.exit("Too many arguments")

    index_dict = {}

    current_dir = Path.cwd()
    current_dir_len = str(current_dir).split("\\")

    # Locate repository root
    for i in range(len(current_dir_len)):

        pathh = current_dir / ".git" / "index"

        if pathh.is_file():
            break

        current_dir = current_dir.parent

    else:
        sys.exit(f"Git Not Initialized")

    file_name = Path(sys.argv[2])

    if not file_name.is_file():
        sys.exit("File Doesn't Exist")

    # Store blob object
    blob_hash, blob, raw_bytes = create_hash(file_name)
    write_in_hash(blob_hash, blob)

    # Determine executable permissions
    if os.access(file_name, os.X_OK):
        mode = "100755"
    else:
        mode = "100644"

    # Store path relative to repository root
    keyy = file_name.resolve()
    keyy = str(Path(keyy).relative_to(current_dir))

    # Load existing index
    file_stats = os.stat(pathh)
    file_size = file_stats.st_size

    if file_size > 0:

        with open(pathh, "r") as file:

            for line in file:

                values = line.strip().split(" ")

                index_dict[values[2]] = (values[0], values[1])

    # Replace existing entry if file already staged
    index_dict[keyy] = (mode, blob_hash)

    # Rewrite the index
    with open(pathh, "w") as file:

        for key, (modee, blobb_hash) in index_dict.items():
            file.write(f"{modee} {blobb_hash} {key}\n")


# Build an in-memory tree from the index
# 
# Example:
#
# src/main.py
# src/utils/helper.py
#
# becomes:
#
# {
#     "src": {
#         "main.py": (...),
#         "utils": {
#             "helper.py": (...)
#         }
#     }
# }
def write_tree_dict():

    tree_dict = {}

    current_dir = Path.cwd()
    current_dir_len = str(current_dir).split("\\")

    # Find repository root
    for i in range(len(current_dir_len)):

        pathh = current_dir / ".git" / "index"

        if pathh.is_file():
            break

        current_dir = current_dir.parent

    else:
        sys.exit(f"Git Not Initialized")

    # Read every staged file
    with open(pathh) as file:

        for line in file:

            values = line.strip().split(" ")

            # File is in repository root
            if not "\\" in values[2]:

                tree_dict[values[2]] = (values[0], values[1])

            # Nested file
            else:

                temp_var = values[2].split("\\")

                current = tree_dict

                # Walk through each directory,
                # creating nested dictionaries as needed
                for i in range(len(temp_var)):

                    if current.get(temp_var[i]) == None:

                        if len(temp_var) - 1 != i:

                            current[temp_var[i]] = {}

                            current = current[temp_var[i]]

                        else:
                            
                            current[temp_var[i]] = (values[0], values[1])
                            

                            break

                    else:

                        current = current[temp_var[i]]

    
    return tree_dict


    


# Stores every complete tree object generated during recursion,
# so build_tree() can write them all to .git/objects afterward.
global_trees_list = []

# Recursively converts the nested tree dictionary into Git's binary
# tree object format. Returns the raw 20-byte SHA-1 hash of the
# tree built at this level, so the parent call can reference it.
def write_tree_recursive(x: dict):

    current_dir = Path.cwd()
    current_dir_len = str(current_dir).split("\\")

    # Find repository root
    for i in range(len(current_dir_len)):

        pathh = current_dir / ".git"

        if pathh.is_dir():
            break

        current_dir = current_dir.parent

    else:
        sys.exit("Git Not Initialized")

    # Stores the binary tree entries for the current directory
    s = b""

    # Process every file or directory in the current tree
    for key, value in x.items():

        # File entry
        if not isinstance(value, dict):

            mode = value[0]
            file_name = key

            # Convert hexadecimal SHA into raw 20-byte form
            blob_hash = bytes.fromhex(value[1])

            # <mode> <filename>\0<raw SHA bytes>
            s += f"{mode} {file_name}\0".encode() + blob_hash

        # Directory entry
        else:

            dir_name = key

            # Recurse into the subdirectory first, since a tree
            # entry needs the child tree's finished hash, not
            # its contents
            current = value
            raw_bytes = write_tree_recursive(current)

            # 40000 <dirname>\0<child tree SHA>
            s += f"40000 {dir_name}\0".encode() + raw_bytes

    # Wrap the entries in the standard object header: tree <size>\0<entries>
    size = len(s)
    treee = f"tree {size}\0".encode() + s

    # Queue this tree for writing, then hand its hash up to the caller
    global_trees_list.append(treee)
    h = hashlib.sha1(treee)
    return h.digest()

    

# Writes every tree object collected in global_trees_list into
# .git/objects, using the same hash/compress/store scheme as blobs
def build_tree(global_tree):

    pathh = check_git_repo()
    pathh = pathh / "objects"

    if not pathh.is_dir():
        sys.exit("Git Corrupted")

    for i in global_tree:

        h = hashlib.sha1(i)
        hexx = h.hexdigest()

        # .git/objects/aa/bbbbb...
        folder1 = hexx[:2]
        file1 = hexx[2:]

        hash_file_path = os.path.join(pathh, folder1, file1)

        compressed_treee = zlib.compress(i)

        # Create object directory if necessary
        if not os.path.isdir(os.path.join(pathh, folder1)):
            create_folders(os.path.join(pathh, folder1))

        # Don't overwrite existing objects
        if not os.path.isfile(os.path.join(pathh, folder1, file1)):
            with open(hash_file_path, "wb") as file:
                file.write(compressed_treee)
    
    
    


        

# Walks upward from the current directory until a .git folder
# is found, and returns the path to that .git directory
def check_git_repo():

    current_dir = Path.cwd()
    current_dir_len = str(current_dir).split("\\")

    for i in range(len(current_dir_len)):

        pathh = current_dir / ".git"

        if pathh.is_dir():
            break

        current_dir = current_dir.parent

    else:
        sys.exit("Git Not Initialized")
    
    return pathh

# Recursively sorts a tree dictionary alphabetically by key, since
# Git requires entries to be in sorted order before hashing a tree
def sort_tree(tree):

    res = OrderedDict(sorted(tree.items(), key=lambda item: item[0]))

    # Sort nested directories too, not just the top level
    for key, value in res.items():
        if isinstance(value, dict):
            x = sort_tree(value)
        else:
            continue
        
        res[key] = x
    
    return res
        

            
            

        


    

    

    




# Entry point: dispatches to the right git command based on argv[1]
def main():

    check_sys()

    if sys.argv[1] == "init":
        init()

    elif sys.argv[1] == "hash-object":
        hash_object()

    elif sys.argv[1] == "cat-file":
        cat_file()

    elif sys.argv[1] == "add":
        add()

    elif sys.argv[1] == "write-tree":

        # Reset in case write-tree runs more than once in the same process
        global_trees_list.clear()

        tree_dict = write_tree_dict()
        sorted_tree_dict = sort_tree(tree_dict)
        raw_bytes = write_tree_recursive(sorted_tree_dict)
        build_tree(global_trees_list)

        # Print the root tree's hash, like real `git write-tree`
        print(raw_bytes.hex())


    else:
        sys.exit("Not a valid command")

if __name__ == "__main__":
    main()