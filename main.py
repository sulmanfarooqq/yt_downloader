import os
import yt_dlp
from os import system
import re

def clear_screen():
    """Clears the screen depending on the OS"""
    system('cls' if os.name == 'nt' else 'clear')

def filter_formats(formats):
    """Filters formats to include only the highest quality for each resolution"""
    resolutions = {}
    for fmt in formats:
        resolution = fmt.get('format_note')
        if resolution not in resolutions or fmt.get('tbr', 0) > resolutions[resolution].get('tbr', 0):
            resolutions[resolution] = fmt
    return list(resolutions.values())

def merge_audio_video(video_path, audio_path, output_path):
    """Merges audio and video using FFmpeg"""
    cmd = f'ffmpeg -y -i "{video_path.replace("\\", "\\\\")}" -i "{audio_path.replace("\\", "\\\\")}" -c:v copy -c:a aac "{output_path.replace("\\", "\\\\")}"'
    os.system(cmd)

def sanitize_filename(filename):
    """Sanitizes a filename to remove invalid characters."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_and_merge(url, folder, cookies_file, quality, title):
    """
    Downloads and merges audio and video into a single file with unlimited retries.
    """
    clear_screen()
    # Sanitize the title to create valid filenames
    sanitized_title = sanitize_filename(title)
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    video_path = os.path.join(folder, f"{sanitized_title}_video.mp4")
    audio_path = os.path.join(folder, f"{sanitized_title}_audio.mp4")
    output_path = os.path.join(folder, f"{sanitized_title}.mp4")

    ydl_opts_video = {
        'cookiefile': cookies_file,
        'quiet': False,
        'outtmpl': video_path,
        'format': quality['format_id']
    }

    while True:  # Retry until successful
        try:
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                ydl.download([url])
            break  # Exit the loop if download is successful
        except Exception as e:
            print(f"Video download failed: {e}")
            print("Retrying video download...")

    if quality.get('acodec') == 'none':  # Check if audio is missing
        print("Downloading audio...")
        ydl_opts_audio = {
            'cookiefile': cookies_file,
            'quiet': False,
            'outtmpl': audio_path,
            'format': 'bestaudio'
        }
        while True:  # Retry until successful
            try:
                with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                    ydl.download([url])
                break  # Exit the loop if download is successful
            except Exception as e:
                print(f"Audio download failed: {e}")
                print("Retrying audio download...")

        print("Merging audio and video...")
        merge_audio_video(video_path, audio_path, output_path)
        os.remove(video_path)
        os.remove(audio_path)
        print(f"Download and merge completed: {output_path}")
    else:
        print(f"Download completed: {video_path}")

def download_playlist(playlist_url, folder, cookies_file):
    """Downloads all videos in a playlist with a single quality choice"""
    ydl_opts = {
        'cookiefile': cookies_file,
        'quiet': True,
        'extract_flat': True,  # Only extract video URLs, do not download yet
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': False
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        entries = playlist_info.get('entries', [])
        print(f"Playlist contains {len(entries)} videos.")

        # Get the first video's URL and ask for quality
        first_video_url = entries[0]['url']
        print("\nFetching available qualities for the playlist...")
        quality, _ = get_video_quality(first_video_url, cookies_file)

        for idx, entry in enumerate(entries, start=1):
            print(f"\nProcessing video {idx}/{len(entries)}: {entry['title']}")
            video_url = entry['url']
            title = entry['title']
            download_and_merge(video_url, folder, cookies_file, quality, title)


def get_video_quality(video_url, cookies_file):
    """Lists available qualities and returns the user's choice"""
    ydl_opts = {
        'cookiefile': cookies_file,
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        formats = info_dict.get('formats', [])
        duration = info_dict.get('duration', 0)
        valid_formats = [fmt for fmt in formats if fmt.get('ext') == 'mp4']
        filtered_formats = filter_formats(valid_formats)

        print("Available qualities (filtered):")
        qualities = {i + 1: fmt for i, fmt in enumerate(filtered_formats)}
        for i, fmt in qualities.items():
            bitrate = fmt.get('tbr', 0)  # Bitrate in kbps
            size_mb = (bitrate * duration) / (8 * 1024) if bitrate and duration else "Unknown"
            print(f"{i}. {fmt['format_note']} - Codec: {fmt['vcodec']}, Audio: {fmt.get('acodec', 'None')}, "
                  f"Bitrate: {fmt.get('tbr', 'Unknown')} kbps, Estimated Size: {size_mb:.2f} MB")

        while True:
            try:
                choice = int(input("Select the quality (by number): "))
                if choice not in qualities:
                    raise ValueError
                return qualities[choice], info_dict['title']
            except ValueError:
                print("Invalid choice, please select a valid number from the list.")

def main():
    """Main function to display menu and handle user input"""
    clear_screen()
    while True:
        print("1. Download Single Video")
        print("2. Download Playlist")
        print("3. Exit")
        choice = input("Select an option (1-3): ")

        if choice == '1':
            video_url = input("Enter the video URL: ")
            folder = input("Enter folder name: ")
            quality, title = get_video_quality(video_url, 'cookies.txt')
            download_and_merge(video_url, folder, 'cookies.txt', quality, title)
        elif choice == '2':
            playlist_url = input("Enter the playlist URL: ")
            folder = input("Enter folder name: ")
            download_playlist(playlist_url, folder, 'cookies.txt')
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
