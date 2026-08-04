let SERVER_URL = "http://127.0.0.1:9191";
let activeUrl = "";

// Load server URL from storage if configured
if (chrome.storage && chrome.storage.local) {
  chrome.storage.local.get(["serverUrl"], function(items) {
    if (items.serverUrl) {
      SERVER_URL = items.serverUrl.replace(/\/$/, "");
    }
    checkServerHealth();
  });
} else {
  checkServerHealth();
}

function checkServerHealth() {
  const badge = document.getElementById("statusBadge");
  const text = document.getElementById("statusText");
  const sbtn = document.getElementById("sbtn");

  fetch(`${SERVER_URL}/health`)
    .then(r => r.json())
    .then(d => {
      badge.className = "status-badge online";
      text.textContent = "Server Connected";
      sbtn.disabled = false;
    })
    .catch(() => {
      badge.className = "status-badge";
      text.textContent = "Server Offline (Click to retry)";
      sbtn.disabled = true;
    });
}

document.getElementById("statusBadge").onclick = checkServerHealth;

// Auto-fill active tab URL if available
chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
  if (tabs && tabs[0] && tabs[0].url) {
    const u = tabs[0].url;
    if (u.startsWith("http://") || u.startsWith("https://")) {
      document.getElementById("urlInput").value = u;
      activeUrl = u;
    }
  }
});

document.getElementById("sbtn").onclick = async function() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tabs && tabs[0]) {
    activeUrl = tabs[0].url;
    searchFormats();
  }
};

document.getElementById("urlInput").addEventListener("keypress", function(e) {
  if (e.key === "Enter") {
    activeUrl = document.getElementById("urlInput").value.trim();
    if (activeUrl) searchFormats();
  }
});

async function searchFormats() {
  activeUrl = activeUrl || document.getElementById("urlInput").value.trim();
  if (!activeUrl || activeUrl.startsWith("chrome://") || activeUrl.startsWith("edge://")) {
    showMsg("Please open a valid video or track webpage first!", "err");
    return;
  }

  showMsg("Analyzing video links & formats...", "info");
  document.getElementById("box").style.display = "none";

  try {
    const r = await fetch(`${SERVER_URL}/formats`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: activeUrl })
    });
    const d = await r.json();

    if (d.success && d.formats && d.formats.length) {
      const sel = document.getElementById("sel");
      sel.innerHTML = "";
      d.formats.forEach(f => {
        const o = document.createElement("option");
        o.value = JSON.stringify({ id: f.id, type: f.type });
        o.textContent = f.label;
        sel.appendChild(o);
      });
      document.getElementById("box").style.display = "block";
      showMsg(d.title || "Media ready to download", "ok");
    } else {
      showMsg(d.error || "No downloadable media found", "err");
    }
  } catch (e) {
    showMsg("Failed to connect to backend server", "err");
  }
}

document.getElementById("dbtn").onclick = async function() {
  const selVal = JSON.parse(document.getElementById("sel").value);
  const btn = document.getElementById("dbtn");

  btn.disabled = true;
  btn.textContent = "⌛ Processing Download...";
  showMsg("Downloading media file... Please wait", "info");

  try {
    const downloadApi = `${SERVER_URL}/download?url=${encodeURIComponent(activeUrl)}&format_id=${encodeURIComponent(selVal.id)}&type=${selVal.type}`;
    const r = await fetch(downloadApi);

    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.error || "Download failed");
    }

    const blob = await r.blob();
    const disposition = r.headers.get("content-disposition");
    let filename = "download_" + Date.now() + (selVal.type === "audio" ? ".mp3" : ".mp4");

    if (disposition) {
      const m = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (m && m[1]) {
        filename = m[1].replace(/['"]/g, "");
        try { filename = decodeURIComponent(filename); } catch (e) {}
      }
    }

    const blobUrl = URL.createObjectURL(blob);
    chrome.downloads.download({
      url: blobUrl,
      filename: filename,
      saveAs: false,
      conflictAction: "uniquify"
    }, function(id) {
      btn.disabled = false;
      btn.textContent = "⚡ Download Media";
      if (chrome.runtime.lastError) {
        showMsg("Error: " + chrome.runtime.lastError.message, "err");
      } else {
        showMsg("🎉 Download Complete & Saved!", "ok");
        setTimeout(() => {
          URL.revokeObjectURL(blobUrl);
        }, 5000);
      }
    });
  } catch (e) {
    btn.disabled = false;
    btn.textContent = "⚡ Download Media";
    showMsg("Error: " + e.message, "err");
  }
};

document.getElementById("openOptions").onclick = function(e) {
  e.preventDefault();
  if (chrome.runtime.openOptionsPage) {
    chrome.runtime.openOptionsPage();
  }
};

function showMsg(m, type) {
  const el = document.getElementById("statusMsg");
  el.textContent = m;
  el.className = "msg " + type;
  el.style.display = "block";
}
