let webSocket = null;
connect()

function connect() {
  webSocket = new WebSocket("ws://localhost:8000/ws");

  webSocket.onopen = (event) => {
    console.log('websocket open');
    // keepAlive();
  };

  webSocket.onmessage = (event) => {
    console.log(`websocket received message: ${event.data}`);
    const msg = JSON.parse(event.data);

    if (msg.action === "get_cookies") {
      const cookies = chrome.cookies.getAll({ url: msg.url }, (cookies) => {
        console.log("cookies", cookies);
        // Gửi cookie về server
        webSocket.send(JSON.stringify({ action: "cookie_data", cookies }));
      });
    };

    if (msg.action === "violation_result") {
      console.log("Violation report:", msg.data);
      // Hiển thị popup hoặc gửi đến content script
      console.log("Violation report:", msg.data);
    }
  };

  webSocket.onclose = (event) => {
    console.log('websocket connection closed');
    webSocket = null;
  };
}

function disconnect() {
  if (webSocket == null) {
    return;
  }
  webSocket.close();
}
