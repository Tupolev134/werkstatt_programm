// Map to store objectURLs against download ids
let urlMap = new Map();

function base64ToUint8Array(base64) {
    let binary_string = atob(base64);
    let len = binary_string.length;
    let bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes;
}

function handleError(error, context) {
  console.error(`Error in ${context} :`, error);
}

function parts_parse_listener(details) {
  let filter = browser.webRequest.filterResponseData(details.requestId);

  let chunks = [];

  filter.ondata = event => {
    chunks.push(event.data);
    filter.write(event.data);
  };

  filter.onstop = event => {
    let combinedData = new Uint8Array(chunks.reduce((acc, val) => acc + val.byteLength, 0));
    let position = 0;
    for (let chunk of chunks) {
      combinedData.set(new Uint8Array(chunk), position);
      position += chunk.byteLength;
    }


    // Convert the byte data to a string
    let jsonString = new TextDecoder("utf-8").decode(combinedData);

    // Parse the string into a JSON object
    let jsonResponse = JSON.parse(jsonString);

    if (!jsonResponse.crumbs) {
      console.warn("Expected crumbs property missing in the response");
      filter.close();
      return; // Exit if the expected data is missing
    }
    let names = jsonResponse.crumbs.map(crumb => crumb.name);
    let filename = names.join('_') + '.json';


    let records = jsonResponse.data.records;
    let recordsJson = JSON.stringify(records);

    let blob = new Blob([recordsJson], {type: 'application/json'});
    let objectURL = URL.createObjectURL(blob);

    let downloading = browser.downloads.download({
      url: objectURL,
      filename: filename,
    });

    downloading.then(id => {
      // Store the objectURL against the download id
      urlMap.set(id, objectURL);
    }).catch(error => console.error("Unexpected error:", error));

    filter.close();
  }
}

function image_download_listener(details) {
  let filter = browser.webRequest.filterResponseData(details.requestId);
  // This variable will accumulate the chunks of data
  let chunks = [];

  filter.ondata = event => {
    chunks.push(event.data);
    filter.write(event.data);
  };

  filter.onstop = event => {
    let combinedData = new Uint8Array(chunks.reduce((acc, val) => acc + val.byteLength, 0));
    let position = 0;
    for(let chunk of chunks) {
      combinedData.set(new Uint8Array(chunk), position);
      position += chunk.byteLength;
    }

    // Convert the byte data to a string
    let jsonString = new TextDecoder("utf-8").decode(combinedData);

    // Parse the string into a JSON object
    let jsonResponse = JSON.parse(jsonString);

    // Extract the base64 image string
    let base64data = jsonResponse.image;

    let blob = new Blob([base64ToUint8Array(base64data)], {type: 'image/png'});
    let objectURL = URL.createObjectURL(blob);

    let downloading = browser.downloads.download({
      url: objectURL,
      filename: "image-data.png",
      saveAs: true,
    });

    downloading.then(id => {
      // Store the objectURL against the download id
      urlMap.set(id, objectURL);
    }).catch(error => console.error("Unexpected error:", error));

    filter.close();
  };
}

browser.webRequest.onBeforeRequest.addListener(
  image_download_listener,
  { urls: ["https://www.partslink24.com/imageserver/ext/api/images/*"], types: ["xmlhttprequest"] },
  ["blocking"]
);

browser.webRequest.onBeforeRequest.addListener(
  parts_parse_listener,
  { urls: ["https://www.partslink24.com/p5jlr/extern/bom/*"], types: ["xmlhttprequest"] },
  ["blocking"]
);

browser.downloads.onChanged.addListener((delta) => {
  if (delta.state && delta.state.current === "complete") {
    // Retrieve the objectURL using the download id, then revoke it
    let objectURL = urlMap.get(delta.id);
    if (objectURL) {
      URL.revokeObjectURL(objectURL);
      urlMap.delete(delta.id);
    }
  }
});
