#!/usr/bin/env python3

import argparse
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich import box
from y2mate_api import Handler, session
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s : %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

# Handle Unicode encoding issues on Windows
try:
    console = Console()
except UnicodeEncodeError:
    # Fallback for Windows cmd.exe which doesn't support Unicode well
    console = Console(force_terminal=False)

# Quality options for videos and audios
VIDEO_QUALITIES = [
    "4k", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p", "auto", "best", "worst"
]
AUDIO_QUALITIES = ["mp3", "m4a", ".m4a", "128kbps", "192kbps", "328kbps"]

def display_welcome():
    """Display a beautiful welcome message"""
    console.clear()
    welcome_text = Text("y2mate CLI Downloader", style="bold blue")
    welcome_text.justify = "center"
    
    panel = Panel(
        welcome_text,
        box=box.DOUBLE,
        padding=(1, 2),
        title="* Welcome",
        border_style="bright_blue"
    )
    console.print(panel)
    console.print("Download YouTube videos and audios with ease!\n", style="green")

def get_cf_clearance():
    """Get CF clearance cookie from user"""
    console.print("Cloudflare Protection Notice", style="bold yellow")
    console.print("Due to Cloudflare protection on y2mate.com, you need to provide a CF clearance cookie.")
    console.print("\nHow to get CF clearance cookie:")
    console.print("1. Install the Http Tracker Chrome extension")
    console.print("2. Navigate to y2mate.com and pass the bot verification")
    console.print("3. Use Http Tracker to find the cf_clearance cookie value")
    console.print("\n[WARNING] The cookie expires frequently, so you may need to update it regularly.\n")
    
    cf_clearance = Prompt.ask("[bold cyan]Enter your cf_clearance cookie value[/bold cyan]")
    return cf_clearance

def search_videos(query, cf_clearance):
    """Search for videos based on query"""
    # Update session with CF clearance cookie
    session.cookies.update({"cf_clearance": cf_clearance})
    
    with console.status("[bold green]Searching for videos...", spinner="earth") as status:
        try:
            handler = Handler(query)
            handler._Handler__make_first_query()
            
            if handler.query_one.is_link:
                # If it's a direct link, get the video info
                handler._Handler__make_second_query().__next__()
                videos = [{
                    'title': handler.query_one.title,
                    'vid': handler.query_one.vid,
                    'author': getattr(handler.query_one, 'a', 'Unknown'),
                    'duration': getattr(handler.query_one, 't', 'Unknown')
                }]
            else:
                # If it's a search query, get the results
                videos = []
                for i, video_dict in enumerate(handler.vitems[:15]):  # Limit to 15 results
                    videos.append({
                        'title': video_dict.get('t', 'Unknown Title')[:60] + '...' if len(video_dict.get('t', '')) > 60 else video_dict.get('t', 'Unknown Title'),
                        'vid': video_dict.get('v', ''),
                        'author': 'Unknown',
                        'duration': 'Unknown'
                    })
            
            return videos
        except Exception as e:
            console.print(f"[bold red]Error searching videos:[/bold red] {str(e)}")
            return []

def display_videos(videos):
    """Display videos in a beautiful table"""
    if not videos:
        console.print("[bold yellow]No videos found.[/bold yellow]")
        return None
        
    table = Table(title="Search Results", box=box.ROUNDED)
    table.add_column("No.", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Author", style="green")
    table.add_column("Duration", style="blue")
    
    for i, video in enumerate(videos, 1):
        table.add_row(
            str(i),
            video['title'],
            video['author'],
            str(video['duration'])
        )
    
    console.print(table)
    
    # Ask user to select a video
    try:
        choice = int(Prompt.ask("[bold cyan]Select a video (number)[/bold cyan]", choices=[str(i) for i in range(1, len(videos)+1)]))
        return videos[choice-1]
    except (ValueError, IndexError):
        console.print("[bold red]Invalid selection.[/bold red]")
        return None

def get_available_formats(vid, cf_clearance):
    """Get available formats for a video"""
    from y2mate_api.main import first_query, second_query
    
    with console.status("[bold green]Fetching available formats...", spinner="clock") as status:
        try:
            # Update session with CF clearance cookie
            session.cookies.update({"cf_clearance": cf_clearance})
            
            # Create the query objects
            query_one = first_query("https://www.youtube.com/watch?v={}".format(vid))
            query_one.main()
            
            query_two = second_query(query_one)
            query_two.video_dict = {"v": vid, "t": "Video Title"}
            query_two.main()
            
            # Get available formats
            formats = []
            
            # Add video formats
            if hasattr(query_two, 'video'):
                for key, value in query_two.video.items():
                    formats.append({
                        'type': 'video',
                        'quality': value.get('q', 'Unknown'),
                        'format': value.get('f', 'mp4'),
                        'size': value.get('size', 'Unknown'),
                        'key': key
                    })
            
            # Add audio formats
            if hasattr(query_two, 'audio'):
                for key, value in query_two.audio.items():
                    formats.append({
                        'type': 'audio',
                        'quality': value.get('q', 'Unknown'),
                        'format': value.get('f', 'mp3'),
                        'size': value.get('size', 'Unknown'),
                        'key': key
                    })
            
            return formats, query_two.title
        except Exception as e:
            console.print("[bold red]Error fetching formats:[/bold red] {}".format(str(e)))
            return [], "Unknown Title"

def display_formats(formats, title):
    """Display available formats in a beautiful table"""
    if not formats:
        console.print("[bold yellow]No formats available.[/bold yellow]")
        return None, None
        
    console.print("\n[bold blue]Available formats for:[/bold blue] {}".format(title))
    
    # Separate videos and audios
    videos = [f for f in formats if f['type'] == 'video']
    audios = [f for f in formats if f['type'] == 'audio']
    
    # Display video formats
    if videos:
        video_table = Table(title="Video Formats", box=box.ROUNDED)
        video_table.add_column("No.", style="cyan", no_wrap=True)
        video_table.add_column("Quality", style="green")
        video_table.add_column("Format", style="yellow")
        video_table.add_column("Size", style="magenta")
        
        for i, video in enumerate(videos, 1):
            video_table.add_row(
                str(i),
                video['quality'],
                video['format'],
                video['size']
            )
        
        console.print(video_table)
    
    # Display audio formats
    if audios:
        audio_table = Table(title="Audio Formats", box=box.ROUNDED)
        audio_table.add_column("No.", style="cyan", no_wrap=True)
        audio_table.add_column("Quality", style="green")
        audio_table.add_column("Format", style="yellow")
        audio_table.add_column("Size", style="magenta")
        
        for i, audio in enumerate(audios, len(videos)+1):
            audio_table.add_row(
                str(i),
                audio['quality'],
                audio['format'],
                audio['size']
            )
        
        console.print(audio_table)
    
    # Ask user to select a format
    try:
        max_choice = len(formats)
        choice = int(Prompt.ask(
            "[bold cyan]Select a format (number)[/bold cyan]", 
            choices=[str(i) for i in range(1, max_choice+1)]
        ))
        
        selected_format = formats[choice-1]
        return selected_format['type'], selected_format['quality']
    except (ValueError, IndexError):
        console.print("[bold red]Invalid selection.[/bold red]")
        return None, None

def download_video(vid, format_type, quality, cf_clearance, download_path):
    """Download the selected video/audio"""
    try:
        # Update session with CF clearance cookie
        session.cookies.update({"cf_clearance": cf_clearance})
        
        handler = Handler("https://www.youtube.com/watch?v={}".format(vid))
        
        # Ensure download directory exists
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Downloading...", total=100)
            
            # Run the handler to get the download link
            for entry in handler.run(format=format_type, quality=quality):
                if entry and entry.get('dlink'):
                    # Update progress to show we're starting download
                    progress.update(task, description="Starting download...", completed=20)
                    
                    # Download the file
                    filename = handler.generate_filename(entry)
                    save_path = os.path.join(download_path, filename)
                    
                    # Save the file with progress
                    saved_path = handler.save(
                        entry, 
                        dir=download_path,
                        progress_bar=False,
                        quiet=True
                    )
                    
                    progress.update(task, description="Download complete!", completed=100)
                    
                    console.print("\n[bold green][SUCCESS] Download completed successfully![/bold green]")
                    console.print("[bold blue]Saved to:[/bold blue] {}".format(saved_path))
                    return True
                break
        
        console.print("[bold red][ERROR] Failed to get download link.[/bold red]")
        return False
    except Exception as e:
        console.print("[bold red]❌ Error downloading video:[/bold red] {}".format(str(e)))
        return False

def main():
    """Main function"""
    display_welcome()
    
    # Get search query
    query = Prompt.ask("[bold cyan]Enter YouTube URL or search term[/bold cyan]")
    if not query:
        console.print("[bold red]No query provided. Exiting.[/bold red]")
        return
    
    # Get CF clearance cookie
    cf_clearance = get_cf_clearance()
    if not cf_clearance:
        console.print("[bold red]No CF clearance cookie provided. Exiting.[/bold red]")
        return
    
    # Search for videos
    videos = search_videos(query, cf_clearance)
    if not videos:
        return
    
    # Display videos and get selection
    selected_video = display_videos(videos)
    if not selected_video:
        return
    
    # Get available formats
    formats, title = get_available_formats(selected_video['vid'], cf_clearance)
    if not formats:
        return
    
    # Display formats and get selection
    format_type, quality = display_formats(formats, title)
    if not format_type or not quality:
        return
    
    # Get download path
    download_path = Prompt.ask(
        "[bold cyan]Enter download path[/bold cyan]", 
        default=os.path.join(os.getcwd(), "downloads")
    )
    
    # Confirm download
    if not Confirm.ask("[bold yellow]Download {} with quality {}?[/bold yellow]".format(format_type, quality)):
        console.print("[bold blue]Download cancelled.[/bold blue]")
        return
    
    # Download the video/audio
    success = download_video(
        selected_video['vid'], 
        format_type, 
        quality, 
        cf_clearance, 
        download_path
    )
    
    if success:
        console.print("\n[bold green][SUCCESS] Thank you for using y2mate CLI Downloader![/bold green]")
    else:
        console.print("\n[bold red][ERROR] Download failed.[/bold red]")

if __name__ == "__main__":
    main()