import datetime

class DeletionLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Logic BEFORE the view
        path = request.path.lower()
        
        # Check for both underscore (your URL) and dash (just in case)
        if request.method == "POST" and ("delete_file" in path or "delete-file" in path):
            user = request.user if request.user.is_authenticated else "Anonymous"
            ip = self.get_client_ip(request)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n⚠️ [AUDIT LOG]")
            print(f"Timestamp: {timestamp}")
            print(f"User     : {user}")
            print(f"IP       : {ip}")
            print(f"Path     : {request.path}")
            print(f"------------------------------\n")

        # 2. THE BRIDGE: This MUST run for every single request
        response = self.get_response(request)

        # 3. Logic AFTER the view
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip