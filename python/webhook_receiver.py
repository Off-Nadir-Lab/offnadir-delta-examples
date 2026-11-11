"""Receive watch notifications on your own endpoint and verify each delivery.

1. Register the endpoint once (it must be https on port 443 and reachable from the internet —
   run this behind your reverse proxy or a tunnel):

       from offnadir_delta import Client
       with Client() as client:
           channel = client.notifications.channel.connect_webhook("https://example.com/delta-hook")
           print(channel.signing_secret)   # returned only once — store it

2. Turn on notifications for the watches you want delivered (the watch's notify_chat setting,
   in the app or with client.watches.update).

3. Run this receiver:  DELTA_WEBHOOK_SECRET=whsec_... python examples/webhook_receiver.py

Deliveries run with the hourly notifications. Each change has a ledger id, so a change sent
again by notifications.channel.replay() is recognised and skipped.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from offnadir_delta import WebhookSignatureError, verify_webhook

SECRET = os.environ["DELTA_WEBHOOK_SECRET"]
PORT = int(os.environ.get("PORT", "8080"))

# Ids of changes already handled. Keep these in your database in a real receiver.
seen: set[str] = set()


class DeltaWebhook(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        try:
            # The raw bytes, exactly as received — parsing and re-serialising would change them.
            event = verify_webhook(raw, self.headers.get("X-Delta-Signature"), SECRET)
        except WebhookSignatureError as exc:
            self.send_response(400)
            self.end_headers()
            print(f"rejected: {exc}")
            return

        if event.get("type") == "test":
            print("connected:", event.get("message"))
        else:
            watch = event["watch"]["name"]
            for change in event["changes"]:
                if change["id"] in seen:
                    continue  # already handled (for example, sent again by a replay)
                seen.add(change["id"])
                # `line` is always present; label / from / to are null when your plan does
                # not open them.
                print(f"[{watch}] {change['line']}")

        # Answer 2xx quickly. A 404 or 410 stops the channel; other errors are retried each hour.
        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    print(f"listening on :{PORT}")
    HTTPServer(("", PORT), DeltaWebhook).serve_forever()
