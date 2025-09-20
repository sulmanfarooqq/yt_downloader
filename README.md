# y2mate CLI Downloader

A beautiful, modern CLI interface for downloading YouTube videos and audios using the y2mate API.

<p align="center">
 <img src="https://github.com/Simatwa/y2mate-api/blob/main/assets/logo.png?raw=true" height="70px" width="70px">
</p>

<h1 align="center">y2mate CLI Downloader</h1>

<p align="center">
<a href="#"><img alt="Python version" src="https://img.shields.io/pypi/pyversions/y2mate-api"/></a>
<a href="LICENSE"><img alt="License" src="https://img.shields.io/static/v1?logo=GPL&color=Blue&message=MIT&label=License"/></a>
<a href="https://pypi.org/project/y2mate-api"><img alt="PyPi" src="https://img.shields.io/pypi/v/y2mate-api"></a>
</p>

> Download YouTube videos and audios with a beautiful CLI interface

## 🌟 Features

- 🎨 Beautiful, modern terminal interface using Rich
- 🔍 Search for videos or enter direct YouTube URLs
- 📋 View available formats and qualities in elegant tables
- 🚀 Progress bars for downloads
- 📂 Download history tracking
- 🛡️ Cloudflare bypass support
- 📱 Responsive design that works on all terminal sizes

## 📋 Requirements

- Python 3.9 or higher
- All dependencies listed in `requirements.txt`

## 🚀 Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Usage

1. Run the downloader:
   ```bash
   python downloader.py
   ```
   
   Or if installed via pip:
   ```bash
   y2mate
   ```

2. Follow the interactive prompts:
   - Enter a YouTube URL or search term
   - Provide your CF clearance cookie (see below)
   - Select a video from the search results
   - Choose your preferred format and quality
   - Specify download location
   - Enjoy your download with a beautiful progress bar!

## 🔐 Cloudflare Clearance

Due to Cloudflare protection on y2mate.com, you need to provide a CF clearance cookie:

1. Install the **Http Tracker** Chrome extension using [this link](https://chromewebstore.google.com/detail/http-tracker/fklakbbaaknbgcedidhblbnhclijnhbi)
2. Using **Chrome Browser**, navigate to [y2mate.com](https://y2mate.com) and pass the bot verification stage
3. Start the *Http Tracker* extension
4. On the search section of y2mate.com, key-in anything and press Enter
5. Return to the Http Tracker window and look for any of the recent URLs containing `*y2mate.com*` and click it
6. Navigate down to the cookies section and copy the value of key `cf_clearance`

⚠️ **Important**: The cookie expires frequently, so you may need to update it regularly.

## 📸 Screenshots

The CLI features a beautiful interface with:

- Colorful welcome screen
- Progress indicators
- Elegant tables for video listings
- Format selection menus
- Download progress bars

## ⚠️ Disclaimer

This repository is intended for educational and personal use only. The use of this repository for any commercial or illegal purposes is strictly prohibited. The repository owner does not endorse or encourage the downloading or sharing of copyrighted material without permission. The repository owner is not responsible for any misuse of the software or any legal consequences that may arise from such misuse.

This script has no official relation with y2mate.com.
currently not working.