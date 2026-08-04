document.addEventListener("DOMContentLoaded", () => {
  const urlInput = document.getElementById("serverUrl");
  const saveBtn = document.getElementById("saveBtn");
  const msg = document.getElementById("msg");

  chrome.storage.local.get(["serverUrl"], (items) => {
    urlInput.value = items.serverUrl || "http://127.0.0.1:9191";
  });

  saveBtn.addEventListener("click", () => {
    const val = urlInput.value.trim() || "http://127.0.0.1:9191";
    chrome.storage.local.set({ serverUrl: val }, () => {
      msg.style.display = "block";
      setTimeout(() => { msg.style.display = "none"; }, 2500);
    });
  });
});
