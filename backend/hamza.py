import requests

webhook_url = "https://default6d3563170d044abcb6b68c9773885b.b0.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/1f93e464a8cc4ebdb6f52d13568fa4b1/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=gaaOj6dyZFsZ4QwHVQfkox9bPN8OEDqTxkSJE03WPK4"
payload = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "summary": "Workflow Notification",
    "themeColor": "0076D7",
    "title": "Pipeline Notification",
    "text": "Hello from Python!",
}

response = requests.post(webhook_url, json=payload, timeout=10)

print(response.status_code)
print(response.text)
