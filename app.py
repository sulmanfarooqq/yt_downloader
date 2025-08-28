import streamlit as st
import yt_dlp
import os
import time
from typing import Optional, List

# Ensure 'videos/' directory exists
if not os.path.exists('videos'):
    os.makedirs('videos')

# Progress hook for yt-dlp
def progress_hook(d):
    if d['status'] == 'downloading':
        progress = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        st.session_state.download_progress = f"Downloading: {progress} | Speed: {speed} | ETA: {eta}"
    elif d['status'] == 'finished':
        st.session_state.download_progress = "Download completed! Processing..."

# Function to download video using yt-dlp with retry mechanism
def download_video(url: str, format_type: str, quality: str, max_retries: int = 3) -> Optional[str]:
    # Determine format options based on user selection
    if format_type == "audio":
        format_option = "bestaudio/best"
        ext = "mp3"
    elif format_type == "video":
        if quality == "highest":
            format_option = "bestvideo+bestaudio/best"
        elif quality == "720p":
            format_option = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif quality == "480p":
            format_option = "bestvideo[height<=480]+bestaudio/best[height<=480]"
        elif quality == "360p":
            format_option = "bestvideo[height<=360]+bestaudio/best[height<=360]"
        else:
            format_option = "bestvideo+bestaudio/best"
        ext = "mp4"
    else:
        format_option = "bestvideo+bestaudio/best"
        ext = "mp4"

    # Get video title for filename
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video').replace(' ', '_').replace('/', '_')[:50]
    except:
        title = "video"

    output_template = f'videos/{title}.%(ext)s'

    ydl_opts = {
        'format': format_option,
        'outtmpl': output_template,
        'progress_hooks': [progress_hook],
        'noplaylist': False,  # Allow playlist downloads
        'ignoreerrors': True,  # Continue on download errors
        'retries': max_retries,
        'fragment_retries': max_retries,
        'continue_dl': True,
        'nooverwrites': True,
        'writethumbnail': True,
        'embedthumbnail': True if format_type == "audio" else False,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            } if format_type == "audio" else {}
        ],
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    }

    # Remove empty postprocessors
    ydl_opts['postprocessors'] = [pp for pp in ydl_opts['postprocessors'] if pp]

    for attempt in range(max_retries):
        try:
            st.session_state.download_progress = f"Attempt {attempt + 1}/{max_retries}: Starting download..."
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                
                # Get the actual downloaded file path
                if info_dict:
                    if '_type' in info_dict and info_dict['_type'] == 'playlist':
                        # For playlists, return the directory
                        return f"videos/{title}_playlist"
                    else:
                        # For single videos, find the actual file
                        expected_filename = output_template.replace('%(ext)s', ext)
                        if os.path.exists(expected_filename):
                            return expected_filename
                        # Try to find any file in the videos directory with the title
                        for file in os.listdir('videos'):
                            if file.startswith(title):
                                return f"videos/{file}"
            
            st.session_state.download_progress = f"Attempt {attempt + 1} failed. Retrying..."
            time.sleep(2)  # Wait before retry
            
        except Exception as e:
            st.session_state.download_progress = f"Attempt {attempt + 1} failed with error: {str(e)}"
            time.sleep(2)  # Wait before retry
            continue

    return None

# Function to get available formats
def get_available_formats(url: str) -> List[dict]:
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('formats', [])
    except Exception as e:
        st.error(f"Error getting formats: {e}")
        return []

# Streamlit Interface
st.title("🎬 Advanced Video Downloader")

# Initialize session state
if 'download_progress' not in st.session_state:
    st.session_state.download_progress = "Ready to download"

# Input box for URL
url = st.text_input("Enter the video URL (YouTube, Facebook, Instagram, LinkedIn)", 
                   placeholder="https://www.youtube.com/watch?v=...")

# Check if URL is entered
if url:
    try:
        # Video preview
        st.sidebar.write("📺 Video Preview:")
        st.sidebar.video(url)
        
        # Get video info for title
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 0)
                st.sidebar.write(f"**Title:** {title}")
                if duration > 0:
                    minutes, seconds = divmod(duration, 60)
                    st.sidebar.write(f"**Duration:** {int(minutes)}m {int(seconds)}s")
        except:
            pass
            
    except Exception as e:
        st.sidebar.error(f"Unable to load preview: {e}")

    # Download options
    col1, col2 = st.columns(2)
    
    with col1:
        format_type = st.radio("Download Format:", ["video", "audio"], horizontal=True)
    
    with col2:
        if format_type == "video":
            quality = st.selectbox("Video Quality:", 
                                 ["highest", "720p", "480p", "360p"],
                                 index=0)
        else:
            quality = "audio"

    # Additional options
    retry_count = st.slider("Max Retry Attempts:", 1, 10, 3)
    download_playlist = st.checkbox("Download entire playlist (if available)", value=True)

    # Download button
    if st.button("🚀 Download Now", type="primary"):
        st.info("Starting download process...")
        
        # Create progress area
        progress_placeholder = st.empty()
        progress_placeholder.info(st.session_state.download_progress)
        
        # Start download
        file_path = download_video(url, format_type, quality, retry_count)
        
        # Update progress
        progress_placeholder.empty()
        
        # Check if download was successful
        if file_path:
            if os.path.isdir(file_path):
                # It's a playlist directory
                st.success(f"✅ Playlist downloaded successfully to: {file_path}")
                st.info("Multiple files were downloaded as part of the playlist.")
            elif os.path.exists(file_path):
                # Single file download
                st.success("✅ Download completed successfully!")
                
                # Show file info
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                st.write(f"**File:** {os.path.basename(file_path)}")
                st.write(f"**Size:** {file_size:.2f} MB")
                
                # Download button
                with open(file_path, "rb") as file:
                    st.download_button(
                        "⬇️ Download File", 
                        file, 
                        file_name=os.path.basename(file_path),
                        mime="video/mp4" if format_type == "video" else "audio/mpeg"
                    )
            else:
                st.error("❌ Download completed but file not found.")
        else:
            st.error("❌ Failed to download the video after all retry attempts.")
            st.info("Please check the URL or try again later.")

# Display current progress in sidebar
st.sidebar.write("---")
st.sidebar.write("**Download Status:**")
st.sidebar.info(st.session_state.download_progress)

# Instructions
st.sidebar.write("---")
st.sidebar.write("**Supported Platforms:**")
st.sidebar.write("• YouTube")
st.sidebar.write("• Facebook")
st.sidebar.write("• Instagram") 
st.sidebar.write("• LinkedIn")

st.sidebar.write("**Tips:**")
st.sidebar.write("• Use 'highest' quality for best results")
st.sidebar.write("• Audio format downloads as MP3")
st.sidebar.write("• Increase retry attempts if downloads fail")
