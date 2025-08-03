# utils/push_client.py
import requests

class PushClient:
    def __init__(self, title, body, token_list, data=None, service="fcm"):
        self.title = title
        self.body = body
        self.tokens = token_list if isinstance(token_list, list) else [token_list]
        self.data = data or {}
        self.service = service.lower()

    def send(self):
        if self.service == "fcm":
            return self._send_fcm()
        # future: elif self.service == "onesignal":
        #     return self._send_onesignal()
        else:
            raise ValueError(f"Unsupported push service: {self.service}")

    def _send_fcm(self):
        # Replace with your FCM server key
        FCM_SERVER_KEY = "YOUR_FCM_SERVER_KEY"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"key={FCM_SERVER_KEY}"
        }

        for token in self.tokens:
            payload = {
                "to": token,
                "notification": {
                    "title": self.title,
                    "body": self.body
                },
                "data": self.data
            }
            try:
                response = requests.post("https://fcm.googleapis.com/fcm/send", json=payload, headers=headers)
                response.raise_for_status()
            except Exception as e:
                print(f"Push to {token} failed: {e}")
                return False
        return True
