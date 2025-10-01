const DISCORD_VIDEO_WEBHOOK_URL = "https://discord.com/api/webhooks/1416470954304995509/ZchGA7oxCucVuVtgPz0DF633dplX5cziBREhYQFnnoS7UpsD5kQerUeXdseYcLRj57eb"; 
const DISCORD_AUDIO_WEBHOOK_URL = "https://discord.com/api/webhooks/1423021826950435006/zI0g2nyHr6dqVN47dcLdBRdRdoFWsmTkxSRdiI9BV_zE8aNuS7j_o1V816a-cCM6yVBe";
const CATEGORY = "Cars";

// Create context menu
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "send-video-to-discord",
    title: "Send video to Discord (Cars)",
    contexts: ["link"]
  });
});

// Handle click
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "send-video-to-discord" && info.linkUrl) {
    if (info.linkUrl.includes("youtube.com/watch") || info.linkUrl.includes("youtu.be/")) {
      sendVideoToDiscord(info.linkUrl);
    } else if (info.linkUrl.includes("soundcloud.com/") || info.linkUrl.includes("youtu.be/")) {
      sendAudioToDiscord(info.linkUrl);
    }
  }
});

function sendVideoToDiscord(url) {
  sendToDiscord(`${url} ${CATEGORY}`, DISCORD_VIDEO_WEBHOOK_URL)
}

function sendAudioToDiscord(url) {
  sendToDiscord(`${url}`, DISCORD_AUDIO_WEBHOOK_URL)
}

function sendToDiscord(sendContent, webhook) {
  const payload = {
    content: sendContent
  };

  fetch(webhook, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  })
    .then((res) => {
      console.log("✅ Sent to Discord:", res.status);
    })
    .catch((err) => {
      console.error("❌ Error sending to Discord:", err);
    });
}
