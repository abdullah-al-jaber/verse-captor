// ==UserScript==
// @name         Verse Fox
// @namespace    http://tampermonkey.net/
// @version      2026-03-06
// @description  Scrape novel from websites !
// @author       Retro Boy
// @match        *://*/*
// ==/UserScript==

(async () => {
    let indicator = document.createElement("div");
    indicator.style.position = "fixed";
    indicator.style.bottom = "20px";
    indicator.style.right = "20px";
    indicator.style.borderRadius = "50px";
    indicator.style.zIndex = "9999";
    indicator.style.width = "20px";
    indicator.style.height = "20px";
    indicator.style.backgroundColor = "magenta";
    indicator.style.border = "5px double white";
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
        if (data.type == "response_current_url") {
            const current_url = data.data.current_url;
            if (current_url) indicator.style.backgroundColor = "magenta";
            else indicator.style.backgroundColor = "orange";
            if (current_url != window.location.href) indicator.style.backgroundColor = "yellow";
            else indicator.style.backgroundColor = "magenta";
            if (current_url == window.location.href) {
                if (window.title == "Just a moment...") return (indicator.style.backgroundColor = "pink");
                websocket.send(
                    JSON.stringify({
                        type: "submit_chapter_data",
                        data: { html: document.documentElement.outerHTML },
                    }),
                );
                websocket.send(
                    JSON.stringify({
                        type: "request_current_url",
                        data: {},
                    }),
                );
            } else {
                window.location.href = current_url;
            }
        }
    };
})();
