# YouTube Downloader (GY YouTube Downloader) v2.6.2
GY YouTube Downloader is a user-friendly desktop application developed using Python and CustomTkinter. This application allows you to easily download YouTube videos and playlists in MP4 (video) or MP3 (audio) formats. Its simple interface makes it accessible and straightforward for anyone to use.

Features
Single Video Download: Download a specific YouTube video as MP4 or MP3.
Playlist Download: Download entire YouTube playlists as MP3.
Resolution Options: Choose from various video resolutions (e.g., 1080p, 720p) for MP4 downloads.
Audio Quality Options: Select different bitrates (e.g., 320kbps, 192kbps) for MP3 downloads.
Bulk Download: Automatically download multiple URLs listed in a text file.
Download History: Keeps a record of all your downloads and allows re-downloading from history.
User-Friendly Interface: Modern and intuitive CustomTkinter GUI for ease of use.
Theme Selection: Customizable appearance with Dark and Light theme options.
Progress Bar & Status Messages: Monitor the download process in real-time.
Automatic Folder Creation: Automatically creates the specified output folder if it doesn't exist.
License Verification System: Includes a basic token verification system to restrict unauthorized use (optional and easily manageable).
Screenshots
(Insert screenshots of your application here. Show different modes (light/dark theme), and different sections (main window, history window, bulk download dialog, etc.). This will make your project more appealing.)

Installation and Setup
Prerequisites
Python 3.x: Make sure you have Python 3.x installed on your system. You can download it from python.org.
yt-dlp and customtkinter libraries: These are the core Python libraries.
FFmpeg (Crucial!): FFmpeg must be installed and added to your system's PATH environment variable. This is essential for MP3 conversion and merging certain video formats. You can download FFmpeg from ffmpeg.org/download.html.
Steps
Clone the Repository or Download:

Bash

git clone https://github.com/YourGitHubUsername/gy-youtube-downloader.git
cd gy-youtube-downloader
(Replace YourGitHubUsername with your actual GitHub username.)

Install Required Python Libraries:

It's recommended to create a virtual environment first, but you can also install globally.

Using a virtual environment (recommended):

Bash

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
Without a virtual environment (less recommended for general development):

Bash

pip install customtkinter yt-dlp Pillow
(If you want to create a requirements.txt file, navigate to your project directory in the terminal and run: pip freeze > requirements.txt)

FFmpeg Setup (Important!)
Ensure FFmpeg is downloaded and added to your system's PATH. If you're unsure how to do this, a quick search for "add ffmpeg to path [your operating system]" will provide detailed instructions.

Token File Setup (Optional, for development/testing)
The application includes a basic token verification system. If you plan to use this, create a file named tokens.txt in the root directory of the project. Each line in this file should contain a valid token. The application will hash these tokens for verification.
Example tokens.txt:

mysecrettoken123
anotherValidToken456
(If this file is not present or empty, the application's token verification will fail unless bypassed in the code, or a valid token is provided at startup.)

Run the Application:

Bash

python youtube_indirici_gurkan_v4.py
Usage
Launch the application.
Paste a YouTube video or playlist URL into the "YouTube URL" field.
Select the desired download type (MP4 Video, MP3 Audio, Playlist MP3).
Adjust the quality options (video resolution for MP4, audio bitrate for MP3) that appear based on your selection.
Choose an output folder or use the default (indirilen_icerikler).
Click the "Download" button to start the download.
For bulk downloads, click "Bulk Download" and select a .txt file containing your list of URLs.
Access your previous downloads by clicking the "History" button.
Development Notes
This project was developed as a practice in creating a modern and functional GUI using Python's CustomTkinter library. The yt-dlp library handles the actual YouTube content downloading and conversion processes.

Contributing
Your feedback and contributions are always welcome! If you find any bugs or wish to suggest new features, please feel free to open an "Issue" or submit a "Pull Request."

License
This project is developed by Gürkan Yılmaz. All rights reserved. For commercial use or redistribution, please contact the developer.

Developer Contact
Gürkan Yılmaz - gurkanyilmaz.k@gmail.com
