let virtualFiles = new Map();

self.addEventListener("install", event => {
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(self.clients.claim());
});

function normalize(path) {
  const out = [];

  for (const p of path.replaceAll("\\", "/").split("/")) {
    if (!p || p === ".") continue;
    if (p === "..") out.pop();
    else out.push(p);
  }

  return out.join("/");
}

function mime(path) {
  const ext = path.split(".").pop().toLowerCase();

  return ({
    html:"text/html; charset=utf-8",
    htm:"text/html; charset=utf-8",
    css:"text/css; charset=utf-8",
    js:"text/javascript; charset=utf-8",
    mjs:"text/javascript; charset=utf-8",
    json:"application/json; charset=utf-8",
    svg:"image/svg+xml",
    png:"image/png",
    jpg:"image/jpeg",
    jpeg:"image/jpeg",
    gif:"image/gif",
    webp:"image/webp",
    ico:"image/x-icon",
    txt:"text/plain; charset=utf-8",
    xml:"application/xml; charset=utf-8",
    php:"text/html; charset=utf-8"
  })[ext] || "application/octet-stream";
}

self.addEventListener("message", event => {
  if (event.data?.type === "SET_FILES") {
    const next = new Map();

    for (const item of event.data.files) {
      next.set(normalize(item.path), {
        data:item.data,
        type:item.type || mime(item.path)
      });
    }

    virtualFiles = next;

    if (event.ports[0]) {
      event.ports[0].postMessage({ok:true});
    }
  }
});

self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  const marker = "/__example__/";

  if (!url.pathname.includes(marker)) return;

  event.respondWith((async () => {
    let path = normalize(
      decodeURIComponent(url.pathname.split(marker)[1] || "")
    );

    if (path.endsWith("/")) {
      if (virtualFiles.has(path + "index.html")) path += "index.html";
      else if (virtualFiles.has(path + "index.php")) path += "index.php";
    }

    const file = virtualFiles.get(path);

    if (!file) {
      return new Response(
        "Not found in selected Example folder: " + path,
        {
          status:404,
          headers:{"Content-Type":"text/plain; charset=utf-8"}
        }
      );
    }

    return new Response(file.data, {
      status:200,
      headers:{
        "Content-Type":file.type || mime(path),
        "Cache-Control":"no-store"
      }
    });
  })());
});
