import os
import chardet

# Define the chunk size for reading the file
chunk_size = 1024  # You can adjust this value as needed

# Open the file in binary mode for reading
with open('C:\\BrightCom\\GitHub\\mstjernfelt\\m3uMetamorph\\local\\Monsteriptv.m3u', 'rb') as file:
    print('Reading file')

    # Initialize variables for tracking progress
    total_bytes_read = 0
    total_file_size = os.path.getsize(file.name)

    # Initialize variables for storing the detected encoding
    detected_encoding = None

    while True:
        # Read a chunk of data
        chunk = file.read(chunk_size)
        if not chunk:
            break

        # Update the total bytes read
        total_bytes_read += len(chunk)

        # Detect encoding for the current chunk
        result = chardet.detect(chunk)
        encoding = result['encoding']

        # Store the detected encoding if not already set
        if not detected_encoding:
            detected_encoding = encoding

        # Calculate and display progress
        progress = (total_bytes_read / total_file_size) * 100
        print(f'Reading... {progress:.2f}% complete', end='\r')

# Print the final detected encoding
print(f'\nDetected encoding: {detected_encoding}')
