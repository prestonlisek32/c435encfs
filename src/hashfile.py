import os

from escape_filenames import escape_filename, unescape_filename
import hashlib
#-----------------------------------------------
#   This file deals with all hashing functions needed 
#   for the filesystem. It contains files to hash, check
#   and update hashes
#-----------------------------------------------

def hashfile(filepath): 
    '''Takes the name of a file and return the md5sum of that file'''
    print(f"hashing file: {filepath}")
    md5 = hashlib.md5()
    print("\n Attempting to Compute Sum")
    try:
        with open(filepath, "rb") as f:
            print("File Opened")
            data = f.read(1024)
            print("First chunk Read")
            while data:
                print(data)
                md5.update(data) 
                data = f.read(1024)
        print("File Read")
    except ValueError as e:
        print(e)
        # The file does not exist. There is no content.
        print("Failed to Read File (It may not exist)")
        pass
    print("Returning HextDigest")
    return md5.hexdigest() 

def comparehash(prefix, absfilepath, checksumpath): 
    '''Compares the md5 sum stored to the current one for a file name'''
    stored = fetchsum(absfilepath, checksumpath)
    if (stored == "Failed" or stored != hashfile(prefix + absfilepath)):
        return False
    else: 
        return True
    
    
def fetchsum(absfilepath, checksumpath): 
    '''Searches the checksums.txt file for the hash of the file, returns it'''

    print(f"fetchsum: looking for path: {absfilepath}")
    #Open File
    with open(checksumpath, 'r') as file:
        line = file.readline()
        while line:
            if line == "\n":
                line = file.readline()
                continue

            try:
                hash, path = line.split(' ',1)
                if path[-1] == "\n":
                    # Remove the ending newline.
                    path = path[:-1]
            except ValueError:
                print(f"fetchsum: bad line found: {line}")
                line = file.readline()
                continue

            if path == escape_filename(absfilepath): 
                print(f"fetchsum: found line: {line}")
                return hash
            else:
                line = file.readline()
    return "Failed"

def addsum(prefix, absfilepath, checksumpath):  
    '''Ran when a file is closed when mounted. Takes in a file path and the absfilepath of the checksum.txt file. Updates the checksum.txt with an updated version for the file'''
    #Read lines
    with open(checksumpath, 'r') as file:
        lines = file.readlines()
    #Search for absfilepath
    found = False
    updatedLine = hashfile(prefix + absfilepath) + " " + escape_filename(absfilepath) + "\n"
    for i in range(len(lines)):
        if lines[i] == "" or lines[i] == "\n":
            continue
        hashsum, path = lines[i].split(" ", 1)

        if path[-1] == "\n":
            path = path[:-1]

        if path == escape_filename(absfilepath):
            found = True
            lines[i] = updatedLine
            break
    #Append line if absfilepath not found
    if found == False:
        lines.append(updatedLine)
    #Update checksum file
    with open(checksumpath, 'w') as file:
        file.write(''.join(lines))
    return not(found)        


def FileRenamed(newpath, checksumpath, filechecksum, oldfilepath):
    '''Ran if a file gets renamed or moved to a new directory. Modifies the checksum.txt with the new name'''
    #Open File
    print(f'Renaming File: {oldfilepath} to {newpath}')
    found = False
    with open(checksumpath, 'r') as file:
            #Look for File path
            lines = file.readlines()
            for i in range(len(lines)):
                if lines[i] == "" or lines[i] == "\n":
                    continue
                hashsum, path = lines[i].split(" ", 1)
                if path[-1] == "\n":
                    path = path[:-1]
                #If found
                if filechecksum == hashsum and escape_filename(oldfilepath) == path:
                    found = True
                    lines[i] = hashsum +" "+ escape_filename(newpath) +"\n"
                    #Change that index with the new info
                    break
    if found:
        #Only write to the file if there was a change
        with open(checksumpath, 'w') as file:
            file.write(''.join(lines))
    return found
    
    
    
def FileMoved(newpath,checksumpath,filechecksum,oldfilepath):
    '''Calls the File Rename function, as they both accomplish the same task'''
    return FileRenamed(newpath,checksumpath,filechecksum,oldfilepath)
#Just a different name to be clear when called for readability

def FileDeleted(filepath, checksumpath):
    with open(checksumpath, 'r') as file:
        #opens File
        lines = file.readlines()
        edited_lines = []

        #Reads all lines, and stores the contents
        for i in range(len(lines)):
            #Splits up the path and lines
            if lines[i] == "" or lines[i] == "\n":
                continue
            hashsum, path = lines[i].split(" ", 1)

            if path[-1] == "\n":
                path = path[:-1]

            if path != escape_filename(filepath):
                #If the given line is not the deleted file, add it to the lines
                edited_lines.append(lines[i])

    with open(checksumpath, 'w') as file:
        file.write("".join(edited_lines))
    return
