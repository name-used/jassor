from io import TextIOBase, BufferedIOBase


with open('x.txt', 'w') as f:
    print(type(f))
    print(isinstance(f, TextIOBase))
    print(isinstance(f, BufferedIOBase))
