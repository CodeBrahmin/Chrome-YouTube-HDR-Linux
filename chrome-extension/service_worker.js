// Show on all pages
/*chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
  chrome.action.show(tabId);
});
*/

// Send current tabs url to MPV server
async function checkIfURLHasHDR(url) {
  chrome.storage.sync.get(
    {
      server_url: null,
      maxheight: null,
      mpv_args: null,
    },
    async function (opts) {
      if (!opts.server_url) opts.server_url = "http://localhost:7531";
      if (opts.mpv_args) {
        opts.mpv_args = opts.mpv_args.split(/\n/);
      } else {
        opts.mpv_args = [];
      }
      if (opts.maxheight) {
        opts.mpv_args.splice(0, 0, ``);
      }
      const query = `?check_if_hdr_url=` + url;

      const response = await fetch(`${opts.server_url}/${query}`, {
        method: "GET",
      });

      const result = await response.json();

      chrome.tabs.query({ url: "https://*.youtube.com/*" }, function (tabs) {
        tabs.forEach((tab) =>
          chrome.tabs.sendMessage(tab.id, {
            type: "hdr_check_result",
            url: url,
            ...result,
          })
        );
      });
    }
  );
}

function playUrl(url, pause) {
  chrome.storage.sync.get(
    {
      server_url: null,
      maxheight: null,
      mpv_args: null,
    },
    function (opts) {
      if (!opts.server_url) opts.server_url = "http://localhost:7531";
      if (opts.mpv_args) {
        opts.mpv_args = opts.mpv_args.split(/\n/);
      } else {
        opts.mpv_args = [];
      }
      if (opts.maxheight) {
        opts.mpv_args.splice(
          0,
          0,
          `--ytdl-format=bestvideo[height<=?${opts.maxheight}]+bestaudio/best`
        );
      }
      const query =
        `?play_url=` +
        encodeURIComponent(url) +
        [""].concat(opts.mpv_args.map(encodeURIComponent)).join("&mpv_args=");

      fetch(`${opts.server_url}/${query}`, {
        method: "GET",
      }).then((res) => {
        console.log(res);
      });

      // Pause videos in tab
      pause &&
        chrome.tabs.query({ url: "https://*.youtube.com/*" }, function (tabs) {
          tabs.forEach((tab) =>
            chrome.tabs.sendMessage(tab.id, {
              type: "pause_video",
              url: url,
              pause_video: true,
            })
          );
        });
    }
  );
}

function handleXHR() {
  // console.log("XHR", arguments)
}

chrome.runtime.onInstalled.addListener(function () {
  var parent = chrome.contextMenus.create({
    id: "thann.play-with-mpv",
    title: "Play with MPV",
    contexts: ["page", "link", "video", "audio"],
  });
});

chrome.contextMenus.onClicked.addListener(function (info, tab) {
  // console.log("item " + info.menuItemId + " was clicked");
  // console.log("info: " + JSON.stringify(info));
  // console.log("tab: " + JSON.stringify(tab));
  playUrl(info["linkUrl"] || info["srcUrl"] || info["pageUrl"], true);

  console.log("context menu clicked");
});

chrome.commands.onCommand.addListener(function (command) {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    playUrl(tabs[0].url, true);
  });
});

chrome.action.onClicked.addListener((tab) => {
  playUrl(tab.url, true);
});

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.type == "check_if_HDR") {
    console.log("checking for hdr");
    checkIfURLHasHDR(request.url);
  } else if (request.type == "open_in_mpv") {
    playUrl(request.url, true);
  } else {
    console.log(request);
  }

  return true;
});
