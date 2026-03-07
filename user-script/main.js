// ==UserScript==
// @name         Verse Fox
// @description  Scrape novel from websites !
// @author       Retro Boy
// @run-at       document-idle
// @match        *://*/*
// ==/UserScript==

(async () => {
    const indicator = document.createElement("div");
    Object.assign(indicator.style, {
        position: "fixed",
        right: "20px",
        bottom: "20px",
        zIndex: "9999",
        border: "5px double white",
        borderRadius: "50px",
        width: "20px",
        height: "20px",
        backgroundColor: "magenta",
    });
    const response_current_url = (websocket, data) => {
        if (!("current_url" in data)) return (indicator.style.backgroundColor = "orange");
        if (data.current_url != window.location.href) return (window.location.href = data.current_url);
        if (window.title == "Just a moment...") return (indicator.style.backgroundColor = "lime");
        websocket.send(JSON.stringify({ type: "submit_chapter_data", data: { html: document.documentElement.outerHTML } }));
        websocket.send(JSON.stringify({ type: "request_current_url", data: {} }));
    };
    const websocket = new WebSocket("ws://127.0.0.1:6969");
    websocket.onopen = () => {
        websocket.send(
            JSON.stringify({
                type: "request_current_url",
                data: {},
            }),
        );
        document.body.appendChild(indicator);
    };
    websocket.onclose = () => document.body.removeChild(indicator);
    websocket.onerror = () => (indicator.style.backgroundColor = "red");
    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const handler_mapping = {
            response_current_url: response_current_url,
        };
        if (!("type" in data && "data" in data)) return (indicator.style.backgroundColor = "red");
        if (!(data.type in handler_mapping)) return (indicator.style.backgroundColor = "brown");
        handler_mapping[data.type](websocket, data.data);
    };
})();
