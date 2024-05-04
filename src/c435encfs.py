#!/usr/bin/env python

# Importing the necessary modules
from __future__ import with_statement
import os
import sys
import errno
from fusepy import FUSE, FuseOSError, Operations, fuse_get_context

from file_crypter import xor_encrypt, xor_decrypt
import hashfile

class Passthrough(Operations):
    # Constructor method
    def __init__(self, root):
        self.root = root

        # Creating a directory to store data if it doesn't exist
        self.data_dir = os.path.join(root, "data")
        if not os.path.isdir(self.data_dir):
            os.mkdir(self.data_dir)

        self.checksums_path = os.path.join(root, "checksums.txt")

        # Creating a file to store checksums if it doesn't exist
        if not os.path.isfile(self.checksums_path):
            with open(self.checksums_path, "w") as _:
                pass

    # Helper method to get the full path
    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, "data", partial)
        return path

    # Filesystem methods
    # ==================

    # Access method  - Checks if the user has permission to access a file or directory
    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    # Change mode method  - Changes the mode (permissions) of a file or directory
    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    # Change owner method  - Changes the owner of a file or directory
    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    # Get attributes method - Retrieves the attributes of a file or directory
    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    # Read directory method  - Lists the contents of a directory
    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    # Read link method - Retrieves the target of a symbolic link
    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    # Make node method
    def mknod(self, path, mode, dev):
        # Attempt to create a node at the specified path
        return os.mknod(self._full_path(path), mode, dev)


    # Create directory method - Creates a new directory
    def mkdir(self, path, mode):
        uid, gid, pid = fuse_get_context()
        full_path = self._full_path(path)
        status = os.mkdir(self._full_path(path), mode)
        os.chown(full_path, uid, gid) #chown to context uid & gid
        return status

    # Get filesystem statistics method
    def statfs(self, path):
        # Not implemented yet
        full_path = self._full_path(path)
        # Get filesystem statistics
        stv = os.statvfs(full_path)
        # Return a dictionary with relevant statistics
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    # Remove directory method
    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    # Unlink method - Removes a file
    def unlink(self, path):
        full_path = self._full_path(path)
        if os.path.islink(full_path):
            # It is a symlink.
            return os.unlink(full_path)
        else:
            # It is a regular file.
            print("unlink: deleting regular file")
            hashfile.FileDeleted(path, self.checksums_path)
            return os.unlink(full_path)

    # Create symlink method - Creates a symbolic link
    def symlink(self, name, target):
        return os.symlink(target, self._full_path(name))

    # Rename method
    def rename(self, old, new):
        #Runs Hashfile to update checksum.txt with the new path
        oldpath = self._full_path(old)
        newpath = self._full_path(new)
        if os.path.isfile(oldpath) and not os.path.islink(oldpath):
            hashfile.FileRenamed(
                new,
                self.checksums_path,
                hashfile.fetchsum(old, self.checksums_path),
                old
                )
        return os.rename(oldpath, newpath)

    # Create link method - Creates a hardlink
    def link(self, target, name):
        print("Hardlinks are not supported.")
        raise FuseOSError(errno.EBADF)
        full_path_target = self._full_path(target)
        hashfile.addsum(self.data_dir, target, self.checksums_path)
        return os.link(self._full_path(name), full_path_target)

    # Update file access and modification times method
    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============


        # Open method - Opens a new file
    def open(self, path, flags):
        '''  The open() system call opens the file specified by pathname.  If
        the specified file does not exist, it may optionally (if O_CREAT
        is specified in flags) be created by open().'''

        full_path = self._full_path(path)
        # First we need to see if the checksums are unchanged
        if hashfile.comparehash(self.data_dir, path, self.checksums_path):
            # Open the file with given flags
            return os.open(full_path, flags)
        else:
            print("File either failed to be read, or the checksum failed to authenticate")
            raise FuseOSError(errno.EBADF)


    # Create file method - Creates a new file
    def create(self, path, mode, fi=None):
        uid, gid, pid = fuse_get_context()
        full_path = self._full_path(path)
        #Not needed, leaving here in case that changes
        fd = os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)
        os.chown(full_path,uid,gid) #chown to context uid & gid
        return fd

     # Read file method - Reads data from a file
    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        plain_text = os.read(fh, length)
        return xor_decrypt(plain_text, "q")

     # Write file method - Writes data to a file
    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        plain_text = buf
        cipher_text = xor_encrypt(plain_text, "q")
        return os.write(fh, cipher_text)

    # Truncate file method - Truncates a file to a specified length
    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    # Flush method - Flushes buffered data to a file
    def flush(self, path, fh):
        return os.fsync(fh)

    # Release method - Releases an open file
    def release(self, path, fh):
        hashfile.addsum(
            self.data_dir,
            path,
            self.checksums_path
            )
        return os.close(fh)

   # Sync method - Synchronizes a file's in-memory state with its on-disk state
    def fsync(self, path, fdatasync, fh):
        return os.fsync(fh)

# Main function to mount the filesystem
def main(mountpoint, root):
    FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True, allow_other=True)

# Entry point of the script
if __name__ == '__main__':
    # Parsing command line arguments and calling the main function
    main(sys.argv[2], sys.argv[1])

