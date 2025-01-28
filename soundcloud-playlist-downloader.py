import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

class SoundCloudDownloader:
    def __init__(self):
        self.base_url = "https://soundcloud.com"
        self.api_base = "https://api.soundcloud.com"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

    def get_playlist_url(self, playlist_url):
        """Extracts individual track URLs from a SoundCloud playlist"""
        response = requests.get(playlist_url, headers={'User-Agent': self.user_agent})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        track_urls = []
        for track in soup.find_all('li', {'class': 'sound'}):
            track_url = f"{self.base_url}{track.find('a')['href']}"
            track_urls.append(track_url)
            
        return track_urls

    def get_track_info(self, track_url):
        """Extracts track information and download URL"""
        response = requests.get(track_url, headers={'User-Agent': self.user_agent})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('title').text.split(' | ')[0]
        artist = soup.find('meta', {'property': 'og:title'})['content']
        
        # Extracting download URL
        track_data = requests.get(f"{self.api_base}{track_url.split(self.base_url)[1]}/download").json()
        if not track_data.get('errors'):
            return {
                'title': title,
                'artist': artist,
                'url': track_data['redirect_uri']
            }
        else:
            print(f"Error: Could not get download URL for {title}")
            return None

    def download_track(self, track_info, output_folder="downloads"):
        """Downloads a single SoundCloud track"""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        filename = f"{track_info['artist']} - {track_info['title']}.mp3"
        filepath = os.path.join(output_folder, filename)
        
        response = requests.get(track_info['url'], stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    
        return filepath

def main():
    """Main function to download SoundCloud playlist"""
    soundcloud = SoundCloudDownloader()
    playlist_url = input("Enter the SoundCloud playlist URL: ")
    
    print("Fetching tracks...")
    track_urls = soundcloud.get_playlist_url(playlist_url)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for url in track_urls:
            future = executor.submit(soundcloud.get_track_info, url)
            futures.append(future)
            
        pbar = tqdm(total=len(futures), desc="Processing tracks")
        results = []
        for future in futures:
            result = future.result()
            if result:
                results.append(result)
            pbar.update(1)
        pbar.close()
        
    print("\nStarting downloads...")
    failed_downloads = 0
    
    with tqdm(total=len(results), desc="Downloading tracks") as pbar:
        for track_info in results:
            try:
                soundcloud.download_track(track_info)
                pbar.update(1)
            except Exception as e:
                print(f"Error downloading track: {e}")
                failed_downloads += 1
                
    print(f"\nDownload complete! Successfully downloaded {len(results) - failed_downloads} tracks.")

if __name__ == "__main__":
    main()
