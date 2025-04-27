# Play YouTube HDR with MPV

Since Chrome on Linux does not yet support HDR, this extension and python server will allow you to play YouTube HDR videos with MPV instead, which does support HDR.  
A fork of [Play with MPV](https://github.com/Thann/play-with-mpv)

## Installation
1. Install the extension. Chrome -> Extensions -> Load Unpacked -> Select the "chrome-extension" folder
2. Install MPV from your package manager
3. Ensure MPV can play HDR by default, use [this tutorial](https://www.reddit.com/r/linux/comments/1e7vljy/intel_now_supports_laptop_hdr_on_linux/).
   If right clicking a HDR file in the file manager and choosing "Open with MPV" results in your face being bathed in light, success!
4. Install yt-dlp through your package manager or [GitHub](https://github.com/yt-dlp/yt-dlp/wiki/Installation)
5. Install fastapi
   ```
   pip install "fastapi[standard]" --break-system-packages
   ```
6. Download our code and run the server:
   `fastapi run --port=7531 /path_to_the_folder/play_with_mpv.py`

   I would recommend you make the server autostart on system startup by using systemd:
   `systemctl edit --full --force --user play-with-mpv`
   Paste the following - computer will log you out immediately you save the file so that it reloads, since it is a user service

   ```
   [Unit]
   Description=Play With MPV
   PartOf=graphical-session.target
   After=graphical-session.target

   [Service]
   Type=simple
   User=<your username>
   ExecStart=python /home/username/.local/bin/fastapi run --port=7531 /path_to_the_folder/play_with_mpv.py

   [Install]
   WantedBy=graphical-session.target
   ```

   Enable the service
   `systemctl --user enable --now play-with-mpv`

7. Install oauth2 plugin with this
   `python3 -m pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip --break-system-packages`
   This plugin will supposedly reduce the error frequency when trying to fetch video metadata. Probably placebo.
   #place the following in ~/yt-dlp.conf
   `--username oauth2 --password ''`
8. Test some random youtube URL so as to get auth credentials. The link will show up as YouTube TV, that's intentional
   `yt-dlp "some_random_youtube_video_link_here" --verbose`
9. ...profit 🤷🏼

## Usage

A nice video to test out with is [this](https://www.youtube.com/watch?v=WBJzp-y4BHA). Go ahead, open the video in Chrome.

When a video has HDR available, a big ass button will appear below the title, takes some seconds.
Clicking this button will pause the video if playing, and open in MPV, takes another several seconds.
That's it, your retina gets burned and you wince in pain... eer I mean joy 🫠
Also, you can always Right-click anywhere on the page and select "Play with MPV", same result
(Ctrl+Space also works) and so does clicking on the add on icon from the extension toolbar

Video is streamed in memory, so that's a good thing.

ENJOY!!
