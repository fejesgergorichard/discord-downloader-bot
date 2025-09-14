const DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1416470954304995509/ZchGA7oxCucVuVtgPz0DF633dplX5cziBREhYQFnnoS7UpsD5kQerUeXdseYcLRj57eb"; 
const CATEGORY = "Cars";

// Create context menu
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "send-to-discord",
    title: "Send video to Discord (Cars)",
    contexts: ["link"]
  });
});

// Handle click
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "send-to-discord" && info.linkUrl) {
    if (
      info.linkUrl.includes("youtube.com/watch") ||
      info.linkUrl.includes("youtu.be/")
    ) {
      sendToDiscord(info.linkUrl);
    }
  }
});

function sendToDiscord(url) {
  const payload = {
    content: `${url} ${CATEGORY}`
  };

  fetch(DISCORD_WEBHOOK_URL, {
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
