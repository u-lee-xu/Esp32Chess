with open('app_header.bin', 'rb') as f:
    data = f.read(32)
    print("App header (first 32 bytes):")
    print(' '.join(f'{b:02x}' for b in data))
    print()
    print("First 8 bytes (magic number):", ' '.join(f'{b:02x}' for b in data[:8]))