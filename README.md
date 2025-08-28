# 🎬 Advanced Video Downloader

A powerful Streamlit-based video downloader that supports multiple platforms with advanced features for high-quality, fast downloads.

## ✨ Features

- **Multi-Platform Support**: Download from YouTube, Facebook, Instagram, and LinkedIn
- **High Quality Downloads**: Support for highest quality videos up to 4K
- **Audio-Only Option**: Download audio-only content as MP3 files
- **Quality Selection**: Choose from multiple video qualities (highest, 720p, 480p, 360p)
- **Playlist Support**: Download entire playlists with a single click
- **Retry Mechanism**: Automatic retry on failed downloads (configurable up to 10 attempts)
- **Progress Indicators**: Real-time download progress with speed and ETA
- **Smart File Naming**: Files are named using original video titles
- **Video Previews**: Preview videos before downloading
- **Thumbnail Support**: Embedded thumbnails for audio files

## 🚀 Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## 📋 Usage

1. Enter the video URL in the input field
2. Select download format (video or audio)
3. Choose video quality if downloading video
4. Set retry attempts if needed (default: 3)
5. Check "Download entire playlist" if you want to download playlists
6. Click "Download Now" to start the download
7. Once completed, click the download button to save the file

## 🛠️ Technical Details

- Built with **Streamlit** for the web interface
- Uses **yt-dlp** for robust video downloading capabilities
- Supports multiple video formats and codecs
- Includes proper HTTP headers to bypass restrictions
- Automatic retry mechanism for reliable downloads

## 🔧 Troubleshooting

### Common Issues

1. **403 Forbidden Errors**: The app includes optimized headers to bypass restrictions. Increase retry attempts if needed.

2. **Slow Downloads**: Try selecting a lower quality option or check your internet connection.

3. **Playlist Not Downloading**: Ensure "Download entire playlist" is checked and the URL points to a playlist.

4. **Audio Conversion Issues**: Make sure FFmpeg is installed on your system for audio conversion.

### Requirements

- Python 3.7+
- FFmpeg (for audio conversion and format processing)
- Stable internet connection

## 📝 License

This project is for educational and personal use only. Please respect copyright laws and terms of service of the platforms you download from.
