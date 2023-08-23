import json
import base64

def save_base64_as_image(json_path, output_path):
    # Load the JSON data
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Extract base64 image data
    image_base64 = data['image']

    # Convert base64 to bytes
    image_data = base64.b64decode(image_base64)

    # Save the image
    with open(output_path, 'wb') as f:
        f.write(image_data)

    print(f"Image saved to {output_path}")


# Usage example
if __name__ == '__main__':
    json_file_path = '/Users/tupolev/Downloads/image-data.json'
    output_image_path = './output_image.png'
    save_base64_as_image(json_file_path, output_image_path)
