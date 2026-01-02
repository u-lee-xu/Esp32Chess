with open(r'C:\Users\Mia\Documents\esp32chess\esp32_chess_ai\build\esp32_chess_ai.bin', 'rb') as f:
    data = f.read(8)
    print("Original bin file magic number:", ' '.join(f'{b:02x}' for b in data))