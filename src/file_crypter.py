from escape_filenames import escape_filename

def open_file(file_path, mode='rb'):
    """Opens a file and returns the file object."""
    #!!! Does not load entire file into memory
    escaped_file_name = escape_filename(file_path)

    try:
        file_object = open(escaped_file_name, mode)
        return file_object
    except FileNotFoundError:
        print("File not found:", escaped_file_name)
    except Exception as e:
        print("An error occurred:", e)
    return None
    
def read_chunk(file_object, chunk_size):
    """Reads a chunk of data from a file and loads it into memory."""
    return file_object.read(chunk_size)

def write_chunk_to_file(file_object, chunk):
    """Writes a chunk of data to a file object."""
    file_object.write(chunk)

def xor_chunk(chunk, key):
    """Xors a chunk of data."""
    xord_chunk = b''

    for byte in chunk:
        xord_chunk += bytes([byte ^ ord(key)])
    return xord_chunk

def xor_encrypt(chunk, key):
    """Encrypts a chunk of data."""
    return xor_chunk(chunk, key)

def xor_decrypt(chunk, key):
    """Decrypts a chunk of data."""
    return xor_chunk(chunk, key)

def xor_file(file_object, cipher_method=xor_encrypt, key='q', chunk_size=1024):
    """xor an entire file chunk by chunk."""
    if file_object is None: return

    while True:
        chunk = read_chunk(file_object, chunk_size)
        if not chunk: 
            break    
        # Returns a generator of processed(ciphered) chunks that can be used with a list or iterable
        yield cipher_method(chunk, key)
