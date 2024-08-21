// Log a message to the console
console.log("Content script has been injected ");

//by default assume SDR so as to hide button before check
containsSDR();
//check if video has HDR
chrome.runtime.sendMessage({
  type: "check_if_HDR",
  url: location.href,
});

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  console.log(request);
  //take action only on messages for the URL this tab is in, since messages are broadcated to every Youtube tab
  if (location.href.includes(request.url)) {
    if (request.type == "hdr_check_result") {
      if (request.dynamic_range == "HDR10") {
        console.log("Video stream is HDR capable, play with MPV?");
        containsHDR();
      } else {
        console.log("Video stream is just SDR, nothing to see here");
        containsSDR();
      }
    } else if (request.type == "pause_video") {
      for (const v of document.getElementsByTagName("video")) {
        v.pause();
      }
    }
  }
});

document.addEventListener("yt-navigate-finish", init);
document.addEventListener("yt-navigate-start", containsSDR);
function init() {
  if (!location.pathname.startsWith("/watch")) {
    return;
  }
  setTimeout(() => {
    var hdrButton = document.getElementById("hdr-button");
    if (hdrButton == null) {
      var divOnSite = document.getElementById("top-row"),
        parent = divOnSite.parentElement,
        div = document.createElement("div");
      (button = document.createElement("button")),
        (text = document.createTextNode("Available"));

      button.setAttribute("id", "hdr-button");
      button.setAttribute("background-color", "gold");
      button.setAttribute(
        "class",
        "yt-spec-button-shape-next yt-spec-button-shape-next--filled yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m"
      );
      button.innerHTML = `<img src="${chrome.runtime.getURL(
        "HDR_10_logo.png"
      )}" "max-height", style="max-height: -webkit-fill-available"/>`;

      button.style.display = "none";
      button.appendChild(text);
      div.append(button);
      parent.insertBefore(div, divOnSite);

      button.addEventListener("click", (event) => {
        chrome.runtime.sendMessage({
          type: "open_in_mpv",
          url: location.href,
        });
      });
    } else {
      button.style.display = "none";

      chrome.runtime.sendMessage({
        type: "check_if_HDR",
        url: location.href,
      });
    }
  }, 1000);
}

function containsHDR() {
  var hdrButton = document.getElementById("hdr-button");
  if (hdrButton != null) {
    button.style.display = "flex";
  }
}
function containsSDR() {
  var hdrButton = document.getElementById("hdr-button");
  if (hdrButton != null) {
    button.style.display = "none";
  }
}
