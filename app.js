const input = document.querySelector("#folder");
const entry = document.querySelector("#entry");
const run = document.querySelector("#run");
const reload = document.querySelector("#reload");
const clear = document.querySelector("#clear");
const preview = document.querySelector("#preview");
const status = document.querySelector("#status");

let files = new Map();
let currentEntry = "";

function clean(path) {
  const out = [];
  for (const p of path.replaceAll("\\", "/").split("/")) {
    if (!p || p === ".") continue;
    if (p === "..") out.pop();
    else out.push(p);
  }
  return out.join("/");
}

async function loadFolder(fileList) {
  const map = new Map();

  for (const file of fileList) {
    const relative = clean(file.webkitRelativePath || file.name);
    const parts = relative.split("/");
    const virtualPath = parts.length > 1 ? parts.slice(1).join("/") : parts[0];
    map.set(virtualPath, file);
  }

  return map;
}

function chooseEntry() {
  if (files.has("index.html")) return "index.html";
  if (files.has("Index.html")) return "Index.html";
  if (files.has("index.php")) return "index.php";
  return [...files.keys()].find(p => /\.html?$/i.test(p)) || "";
}

function refreshEntries() {
  entry.innerHTML = "";

  const candidates = [...files.keys()]
    .filter(p => /\.(html?|php)$/i.test(p))
    .sort();

  for (const path of candidates) {
    const option = document.createElement("option");
    option.value = path;
    option.textContent = path;
    entry.appendChild(option);
  }

  currentEntry = chooseEntry();
  if (currentEntry) entry.value = currentEntry;

  entry.disabled = candidates.length === 0;
  run.disabled = !currentEntry;
}

async function sendFilesToWorker() {
  if (!navigator.serviceWorker.controller) {
    throw new Error("Service Workerが準備されていません。ページを再読み込みしてください。");
  }

  const payload = [];

  for (const [path, file] of files) {
    payload.push({
      path,
      type: file.type || "application/octet-stream",
      data: await file.arrayBuffer()
    });
  }

  await new Promise((resolve, reject) => {
    const channel = new MessageChannel();

    channel.port1.onmessage = event => {
      if (event.data?.ok) resolve();
      else reject(new Error(event.data?.error || "ファイル登録に失敗しました。"));
    };

    navigator.serviceWorker.controller.postMessage(
      {type:"SET_FILES", files:payload},
      [channel.port2]
    );
  });
}

async function execute() {
  if (!currentEntry) return;

  try {
    await sendFilesToWorker();

    const url = new URL(
      "__example__/" + currentEntry,
      location.href
    );

    url.searchParams.set("v", Date.now());
    preview.src = url.href;

    reload.disabled = false;
    status.textContent =
      `${files.size}個のファイルをブラウザ内へ読み込み、${currentEntry}を実行しています。`;
  } catch (error) {
    status.textContent = "エラー: " + error.message;
  }
}

input.addEventListener("change", async () => {
  if (!input.files.length) return;

  try {
    files = await loadFolder(input.files);
    refreshEntries();

    status.textContent =
      `${files.size}個のファイルを読み込みました。Exampleはサーバーへアップロードされていません。`;
  } catch (error) {
    status.textContent = "エラー: " + error.message;
  }
});

entry.addEventListener("change", () => {
  currentEntry = entry.value;
});

run.addEventListener("click", execute);

reload.addEventListener("click", () => {
  if (preview.src) {
    preview.src = preview.src.split("?")[0] + "?v=" + Date.now();
  }
});

clear.addEventListener("click", () => {
  files.clear();
  currentEntry = "";
  input.value = "";
  entry.innerHTML = "";
  entry.disabled = true;
  run.disabled = true;
  reload.disabled = true;
  preview.src = "about:blank";
  status.textContent = "クリアしました。";
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js", {scope:"./"})
    .then(() => navigator.serviceWorker.ready)
    .then(() => location.reload())
    .catch(error => {
      status.textContent =
        "Service Workerを登録できませんでした: " + error.message;
    });
} else {
  status.textContent = "このブラウザはService Workerに対応していません。";
}
