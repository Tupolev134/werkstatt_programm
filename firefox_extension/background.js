// Map to store objectURLs against download ids
let urlMap = new Map();

let export_folder = "parts_link_exports/";

let sharedState = {
    currentFilename: null
};

function parseEssentials(inputStr) {
    // Split the string by " - "
    const segments = inputStr.split(" - ");

    // Get the last three segments
    const lastThree = segments.slice(-3);

    // Join them back together
    return lastThree.join(" - ");
}

function sanitizeFilename(filename) {
    let invalidChars = /[<>:"/\\|?*]/g;  // Regular expression to match invalid Windows filename characters
    return filename.replace(invalidChars, '_');  // Replace invalid characters with underscores
}

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
    let names = jsonResponse.crumbs.map(crumb => sanitizeFilename(crumb.name));
    let filename = parseEssentials(names.join('_'));
    let subdirectory = export_folder + filename + '/'

    sharedState.currentFilename = filename;
    document.dispatchEvent(new Event('partsProcessingComplete'));

    let records = jsonResponse.data.records;
    let recordsJson = JSON.stringify(records);

    let blob = new Blob([recordsJson], {type: 'application/json'});
    let objectURL = URL.createObjectURL(blob);

    let downloading = browser.downloads.download({
      url: objectURL,
      filename: subdirectory + parseEssentials(filename) + '.json',
    });

    downloading.then(id => {
      // Store the objectURL against the download id
      urlMap.set(id, objectURL);
    }).catch(error => console.error("Unexpected error:", error));

    filter.close();
  }
}

function image_download_listener(details) {
    // If the filename is not yet available, delay the processing
    if (!sharedState.currentFilename) {
        document.addEventListener('partsProcessingComplete', () => {
            processImageData(details);
        });
    } else {
        processImageData(details);
    }
}

function processImageData(details) {
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

    let subdirectory = export_folder + sharedState.currentFilename + '/';
    let filename = sharedState.currentFilename;

    let downloading = browser.downloads.download({
      url: objectURL,
      filename: subdirectory + parseEssentials(filename) + '.png'
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
