import requests
from bs4 import BeautifulSoup
import os

def download_soundcloud_artwork(url):
    try:
        # Send a GET request to the SoundCloud page
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all image tags on the page
        images = soup.find_all('img')
        
        # Look for the artwork image URL
        artwork_url = None
        for img in images:
            img_url = img.get('src')
            if img_url and 'artworks' in img_url:
                artwork_url = img_url
                break
        
        if not artwork_url:
            print("Could not find the artwork image URL.")
            return
        
        # Determine the file format from the URL
        file_format = os.path.splitext(artwork_url)[1]
        
        # Download the image
        response_img = requests.get(artwork_url)
        if response_img.status_code != 200:
            print(f"Failed to download the artwork. Status code: {response_img.status_code}")
            return
        
        # Save the image to a file
        filename = f"soundcloud_artwork{file_format}"
        with open(filename, 'wb') as file:
            file.write(response_img.content)
        
        print(f"Artwork saved as {filename}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
url = input("Enter the SoundCloud track URL: ")
download_soundcloud_artwork(url)
