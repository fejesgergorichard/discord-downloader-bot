const DISCORD_VIDEO_WEBHOOK_URL = "https://discord.com/api/webhooks/1416470954304995509/ZchGA7oxCucVuVtgPz0DF633dplX5cziBREhYQFnnoS7UpsD5kQerUeXdseYcLRj57eb"; 
const DISCORD_AUDIO_WEBHOOK_URL = "https://discord.com/api/webhooks/1423021826950435006/zI0g2nyHr6dqVN47dcLdBRdRdoFWsmTkxSRdiI9BV_zE8aNuS7j_o1V816a-cCM6yVBe";

chrome.runtime.onInstalled.addListener(() => {
  // Links
  chrome.contextMenus.create({
    id: "send-link-to-discord",
    title: "Send link to Discord (Cars/SongSamples)",
    contexts: ["link"]
  });

  // Page
  chrome.contextMenus.create({
    id: "send-page-to-discord",
    title: "Send current page URL to Discord",
    contexts: ["page"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "send-link-to-discord" && info.linkUrl) {
    handleUrl(info.linkUrl);
  }

  if (info.menuItemId === "send-page-to-discord" && tab?.url) {
    handleUrl(tab.url);
  }
});

function handleUrl(url) {
  if (url.includes("youtube.com/watch") || url.includes("youtu.be/")) {
    sendVideoToDiscord(url, "Cars");
  } else if (url.includes("pinterest.com/")) {
    sendVideoToDiscord(url, "pinterest");
  } else if (url.includes("soundcloud.com/")) {
    sendAudioToDiscord(url);
  }
}

function sendVideoToDiscord(url, category) {
  sendToDiscord(`${url} ${category}`, DISCORD_VIDEO_WEBHOOK_URL);
}

function sendAudioToDiscord(url) {
  sendToDiscord(`${url}`, DISCORD_AUDIO_WEBHOOK_URL);
}

function sendToDiscord(sendContent, webhook) {
  const payload = { content: sendContent };

  fetch(webhook, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
    .then((res) => {
      console.log("✅ Sent to Discord:", res.status);
    })
    .catch((err) => {
      console.error("❌ Error sending to Discord:", err);
    });
}