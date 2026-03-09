// ==UserScript==
// @name         Verse Fox
// @namespace    https://github.com/abdullah-al-jaber
// @version      2.0
// @description  Scrape novels from websites
// @author       Retro Boy
// @match        *://*/*
// @run-at       document-idle
// @grant        none
// ==/UserScript==

(async () => {
    "use strict";
    if (window.top !== window.self) return void 0;
    const STATUS_COLORS = {
        idle: "magenta",
        ws_error: "red",
        message_format_error: "brown",
        message_type_unknown: "orange",
        message_data_unknown: "yellow",
        cloudflare_challenge: "green",
    };
    const host = document.createElement("div");
    const shadow = host.attachShadow({ mode: "open" });
    host.id = "verse-fox-host";
    document.documentElement.appendChild(host);
    const indicator = document.createElement("div");
    Object.assign(indicator.style, {
        position: "fixed",
        right: "20px",
        bottom: "20px",
        zIndex: "9999",
        border: "5px double white",
        boxShadow: "0 0 0px 2px black",
        borderRadius: "50px",
        width: "20px",
        height: "20px",
        backgroundColor: STATUS_COLORS.idle,
    });
    indicator.hidden = true;
    shadow.appendChild(indicator);
    const response_current_url = (websocket, data) => {
        if (!("current_url" in data)) return (indicator.style.backgroundColor = STATUS_COLORS.message_data_unknown);
        if (document.title == "Just a moment...") return (indicator.style.backgroundColor = STATUS_COLORS.cloudflare_challenge);
        if (data.current_url != window.location.href) return (window.location.href = data.current_url);
        websocket.send(JSON.stringify({ type: "submit_html", data: { html: document.documentElement.outerHTML } }));
        websocket.send(JSON.stringify({ type: "request_current_url", data: {} }));
    };
    const websocket = new WebSocket("ws://127.0.0.1:6969");
    websocket.onopen = () => (indicator.hidden = false);
    websocket.onclose = () => (indicator.hidden = true);
    websocket.onerror = () => (indicator.style.backgroundColor = STATUS_COLORS.ws_error);
    websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        const handler_mapping = {
            response_current_url: response_current_url,
        };
        if (!("type" in message && "data" in message)) return (indicator.style.backgroundColor = STATUS_COLORS.message_format_error);
        if (!(message.type in handler_mapping)) return (indicator.style.backgroundColor = STATUS_COLORS.message_type_unknown);
        handler_mapping[message.type](websocket, message.data);
    };
    websocket.addEventListener("open", () => {
        websocket.send(JSON.stringify({ type: "request_current_url", data: {} }));
    });
})();
