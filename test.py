# class MyClass:
#     x = 10
#
#     @classmethod
#     def Update(cls):
#         cls.x += 1
#
#
#     def __init__(self):
#         self.y = self.x
#
# a = MyClass()
# MyClass.Update()
# print(a.y)


import os

def generate_file_paths(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

# Пример использования
directory_path = 'Data/Sprites/Conv'
for file_path in generate_file_paths(directory_path):
    print(file_path)
