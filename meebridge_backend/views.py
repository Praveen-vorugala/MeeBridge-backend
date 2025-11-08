from django.http import JsonResponse, HttpResponse
import json


def api_root(request):
    """Root API endpoint with API information"""
    if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
        # Return HTML for browser requests
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MeeBridge API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #667eea; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 4px; }
                .method { color: #4caf50; font-weight: bold; }
                code { background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🚀 MeeBridge API</h1>
            <p><strong>Version:</strong> 1.0.0</p>
            <p>Backend API server is running successfully!</p>
            
            <h2>Available Endpoints:</h2>
            <div class="endpoint">
                <span class="method">GET</span> <code>/</code> - API Information (this page)
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/admin/</code> - Django Admin Panel
            </div>
            <div class="endpoint">
                <span class="method">POST</span> <code>/api/users/login/</code> - User Login
            </div>
            <div class="endpoint">
                <span class="method">POST</span> <code>/api/users/register/</code> - User Registration
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/users/me/</code> - Get Current User
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/meeting-pages/</code> - List Meeting Pages
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/public/meeting-pages/{slug}/</code> - Get Public Meeting Page
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/bookings/</code> - List Bookings
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/availabilities/</code> - List Availabilities
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/analytics/</code> - Get Analytics
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/customers/</code> - Manage Customers
            </div>
            
            <h2>Default Login Credentials:</h2>
            <p><strong>Email:</strong> admin@meebridge.com<br>
            <strong>Password:</strong> admin123</p>
            
            <h2>Next Steps:</h2>
            <p>1. Start the Angular frontend: <code>cd meebridge-frontend && npm start</code></p>
            <p>2. Access the frontend at: <code>http://localhost:4200</code></p>
            <p>3. Login with the credentials above</p>
        </body>
        </html>
        """
        return HttpResponse(html)
    else:
        # Return JSON for API requests
        return JsonResponse({
            'message': 'MeeBridge API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'admin': '/admin/',
                'api': {
                    'auth': '/api/users/login/',
                    'users': '/api/users/',
                    'meeting_pages': '/api/meeting-pages/',
                    'bookings': '/api/bookings/',
                    'availabilities': '/api/availabilities/',
                    'analytics': '/api/analytics/',
                    'customers': '/api/customers/',
                }
            }
        })

