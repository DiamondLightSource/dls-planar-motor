class HTMLMonitorPage:
    def get_page_content(self) -> str:
        content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Xbot Motor Stream Monitor</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            Helvetica, Arial, sans-serif; margin: 40px; background-color: #f4f6f9;
            color: #333; }
            .card { background: white; padding: 24px; border-radius: 12px; box-shadow:
            0 4px 6px rgba(0,0,0,0.05); max-width: 500px; margin: 0 auto; }
            h2 { margin-top: 0; color: #1e293b; border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px; }
            .status-container { display: flex; justify-content: space-between;
            align-items: center; margin: 20px 0; padding: 15px; background: #f8fafc;
            border-radius: 8px; border: 1px solid #e2e8f0; }
            .status-label { font-weight: 600; font-size: 1.1rem; }
            .status-value { font-family: monospace; font-size: 1.2rem; color: #0284c7;
            font-weight: bold; }
            .badge { display: inline-block; padding: 4px 10px; border-radius: 20px;
            font-size: 0.85rem; font-weight: bold; }
            .connected { background-color: #dcfce7; color: #166534; }
            .disconnected { background-color: #fee2e2; color: #991b1b; }
            .log-box { background: #1e293b; color: #38bdf8; padding: 12px;
            border-radius:6px; font-family: monospace; font-size: 0.85rem;
            max-height: 150px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🤖 Xbot1 Live Stream</h2>
            <p>Connection State:
            <span id="conn-badge" class="badge disconnected">Disconnected</span></p>

            <div class="status-container">
                <span class="status-label">Xbot1 Done Flag:</span>
                <span id="xbot-status" class="status-value">--</span>
            </div>

            <p style="margin-bottom: 5px; font-size: 0.9rem;
            color: #64748b;">Live Event Stream:</p>
            <div id="log" class="log-box">Awaiting connection...</div>
        </div>

        <script>
            // Automatically adapts if you use localhost or an external IP network
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${wsProtocol}//${window.location.host}/xbot1/status/stream`;

            const ws = new WebSocket(wsUrl);
            const badge = document.getElementById('conn-badge');
            const statusDisplay = document.getElementById('xbot-status');
            const logBox = document.getElementById('log');

            function logMessage(text) {
                const timestamp = new Date().toLocaleTimeString();
                logBox.innerHTML = `[${timestamp}] ${text}<br>` + logBox.innerHTML;
            }

            ws.onopen = () => {
                badge.innerText = "Connected";
                badge.className = "badge connected";
                logMessage("Connected to FastAPI WebSocket server.");
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.xbot1_done !== undefined) {
                        statusDisplay.innerText = data.xbot1_done;
                        logMessage(`Updated Done flag: ${data.xbot1_done}`);
                    }
                } catch (err) {
                    logMessage(`Data error: ${event.data}`);
                }
            };

            ws.onclose = () => {
                badge.innerText = "Disconnected";
                badge.className = "badge disconnected";
                logMessage("WebSocket stream disconnected.");
            };

            ws.onerror = (error) => {
                logMessage("Streaming connection error occurred.");
            };
        </script>
    </body>
    </html>
    """
        return content
