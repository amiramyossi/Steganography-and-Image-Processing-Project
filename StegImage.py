from collections import Counter
import heapq
from Node import Node
import pyinputplus as pyip
import os
from PIL import Image


def is_legal_file_path(file_path):
    # Check if the path is valid without checking existence
    return os.path.exists(os.path.dirname(file_path))


def is_valid_path(file_path, supposed_to_exist=None, png=None):

    if not is_legal_file_path(file_path):
        raise Exception("The path you have entered is illegal. ")
    
    _, file_extension = os.path.splitext(file_path)

    if supposed_to_exist and not os.path.isfile(file_path):
        raise Exception("The path you have entered is invalid. ")
    if png and file_extension.lower() != '.png':
        raise Exception("The path you have entered is not of type png. ")
    if not png and file_extension.lower() != '.txt':
        raise Exception("The path you have entered is not of type txt. ")
    else:
        return file_path
    











def string_to_tuples(s):
    counter = Counter(s)
    return [Node(count, char) for char, count in counter.items()]

def huffman_tree_generator(lst):
    heapq.heapify(lst)
    
    while len(lst) > 1:
        # Extract the two nodes with the smallest frequencies
        left = heapq.heappop(lst)
        right = heapq.heappop(lst)
        
        # Create a new node with these two nodes as children
        new_node = Node(left.freq + right.freq, left=left, right=right)
        
        # Insert the new node back into the heap
        heapq.heappush(lst, new_node)
    
    # The remaining node is the root of the Huffman tree
    return lst[0]

def generate_codes(node, prefix="", codebook={}):
    if node.char is not None:
        # It's a leaf node
        codebook[node.char] = prefix
    else:
        # Internal node, traverse its children
        if node.left:
            generate_codes(node.left, prefix + "0", codebook)
        if node.right:
            generate_codes(node.right, prefix + "1", codebook)
            
    return codebook

def encode_string(s, codebook):
    return ''.join(codebook[char] for char in s)




def main_huffman_code_generator(input_string):
    tuple_list = string_to_tuples(input_string)
    huffman_tree = huffman_tree_generator(tuple_list)
    codebook = generate_codes(huffman_tree)
    encoded_string = encode_string(input_string, codebook)
    print(codebook)
    return encoded_string, codebook



def reverse_codebook(codebook):
    return {v: k for k, v in codebook.items()}

def main_decoder(encoded_string, codebook):
    # Step 1: Reverse the codebook
    reversed_codebook = reverse_codebook(codebook)
    
    # Step 2: Decode the input string
    decoded_string = []
    current_code = ""
    
    for bit in encoded_string:
        current_code += bit
        if current_code in reversed_codebook:
            decoded_string.append(reversed_codebook[current_code])
            current_code = ""
    
    return ''.join(decoded_string)







def hide_text_in_image(image_path, text_path, output_image_path):
    # Read the content of the text file
    with open(text_path, 'r') as file:
        secret_message = file.read()
        print(secret_message)
    
    # Generate Huffman encoded binary string
    encoded_string, codebook = main_huffman_code_generator(secret_message)
    
    # Get the size of the encoded message
    encoded_length = len(encoded_string)
    encoded_length_binary = f'{encoded_length:032b}'  # 32-bit binary representation
    
    # Load the image
    image = Image.open(image_path)
    pixels = image.load()
    
    # Flatten the image pixels
    width, height = image.size
    pixel_list = []
    for y in range(height):
        for x in range(width):
            pixel_list.append(pixels[x, y])
    
    # Hide the length of the binary string in the first 32 LSBs
    binary_index = 0
    for i in range(11):  # First 11 pixels can hold 32 bits
        pixel = pixel_list[i]
        r, g, b = pixel[:3]
        if binary_index < 32:
            r = (r & 0xFE) | int(encoded_length_binary[binary_index])
            binary_index += 1
        if binary_index < 32:
            g = (g & 0xFE) | int(encoded_length_binary[binary_index])
            binary_index += 1
        if binary_index < 32:
            b = (b & 0xFE) | int(encoded_length_binary[binary_index])
            binary_index += 1
        pixel_list[i] = (r, g, b)
    
    # Reset binary index to start hiding the encoded string from the 33rd LSB
    binary_index = 0
    for i in range(11, len(pixel_list)):
        if binary_index >= len(encoded_string):
            break
        pixel = pixel_list[i]
        r, g, b = pixel[:3]
        if binary_index < len(encoded_string):
            r = (r & 0xFE) | int(encoded_string[binary_index])
            binary_index += 1
        if binary_index < len(encoded_string):
            g = (g & 0xFE) | int(encoded_string[binary_index])
            binary_index += 1
        if binary_index < len(encoded_string):
            b = (b & 0xFE) | int(encoded_string[binary_index])
            binary_index += 1
        pixel_list[i] = (r, g, b)
    
    # Save the modified image
    new_image = Image.new(image.mode, image.size)
    new_pixels = new_image.load()
    pixel_iter = iter(pixel_list)
    for y in range(height):
        for x in range(width):
            new_pixels[x, y] = next(pixel_iter)
    new_image.save(output_image_path)




def extract_encoded_string_from_image(image_path):
    # Load the image
    image = Image.open(image_path)
    pixels = image.load()
    
    # Flatten the image pixels
    width, height = image.size
    pixel_list = []
    for y in range(height):
        for x in range(width):
            pixel_list.append(pixels[x, y])
    
    # Extract the length of the encoded string from the first 32 LSBs
    encoded_length_binary = ""
    binary_index = 0
    for i in range(11):  # First 11 pixels can hold 32 bits
        pixel = pixel_list[i]
        r, g, b = pixel[:3]
        if binary_index < 32:
            encoded_length_binary += str(r & 0x01)
            binary_index += 1
        if binary_index < 32:
            encoded_length_binary += str(g & 0x01)
            binary_index += 1
        if binary_index < 32:
            encoded_length_binary += str(b & 0x01)
            binary_index += 1
    
    encoded_length = int(encoded_length_binary, 2)
    
    # Extract the encoded string using the extracted length
    encoded_string = ""
    binary_index = 0
    for i in range(11, len(pixel_list)):
        if binary_index >= encoded_length:
            break
        pixel = pixel_list[i]
        r, g, b = pixel[:3]
        if binary_index < encoded_length:
            encoded_string += str(r & 0x01)
            binary_index += 1
        if binary_index < encoded_length:
            encoded_string += str(g & 0x01)
            binary_index += 1
        if binary_index < encoded_length:
            encoded_string += str(b & 0x01)
            binary_index += 1
    
    return encoded_string


def reveal_text_from_image(image_path, codebook):
    
    
    # Extract the encoded string from the image
    encoded_string = extract_encoded_string_from_image(image_path)
    
    # Decode the encoded string using the frequency dictionary
    decoded_string = main_decoder(encoded_string, codebook)
    
    print("The original text is:", decoded_string)


# # Example usage:
image_path = pyip.inputCustom(lambda x: is_valid_path(x, supposed_to_exist=True, png=True), prompt="Enter the image path with hidden message: ")
codebook = {'l': '0000', 'u': '000100', "'": '000101', ',': '00011', 'd': '001', 'e': '0100', 'm': '01010', 'c': '010110', 'f': '010111', 'i': '0110', 'n': '01110', 'r': '01111', 'w': '10000', 'g': '1000100', 'o': '1000101', '\n': '100011', 'b': '1001', 'a': '101', 'I': '11000', '!': '1100100', 't': '1100101', 'h': '110011', 'y': '1101', ' ': '111'}
reveal_text_from_image(image_path, codebook)



    
    
# Use input prompts to get the file paths
# image_path = pyip.inputCustom(lambda x: is_valid_path(x, supposed_to_exist=True, png=True), prompt="Enter the image path: ")
# text_path = pyip.inputCustom(lambda x: is_valid_path(x, supposed_to_exist=True, png=False), prompt="Enter the text path: ")
# output_image_path = pyip.inputCustom(lambda x: is_valid_path(x, supposed_to_exist=False, png=True), prompt="Enter the output image path: ")

# # Call the function with the validated paths
# hide_text_in_image(image_path, text_path, output_image_path)


# string_to_tuples("""If I were a rich man, yabadabadbabda didiyayay, all day long I'd biddy biddy bum, if I were a wealthy man!""")


# main_huffman_code_generator("""If I were a rich man, yabadabadbabda didiyayay, all day long I'd biddy biddy bum, if I were a wealthy man!""")
 







    

     

                

