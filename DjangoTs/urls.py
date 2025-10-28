# myproject/urls.py
from django.http import JsonResponse, HttpResponse
from django.urls import path, include
from django.contrib import admin

def api_home(request):
    """智能API首页"""
    # 如果是API请求，返回JSON
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            "service": "商品市场后端API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth/",
                "goods": "/api/goods/",
                "test": "/api/test/"
            }
        })

    # 否则返回简单的HTML页面
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>商品市场 - 后端服务</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛒 商品市场平台后端服务</h1>
            
            <div class="card">
                <h2>📊 管理后台</h2>
                <p><a href="/admin/">/admin/</a> - 数据管理界面</p>
            </div>
            
            <div class="card">
                <h2>🔌 API接口</h2>
                <p><a href="/api/">/api/</a> - REST API 端点</p>
            </div>
            
            <div class="card">
                <h2>🎨 前端应用</h2>
                <p><a href="http://localhost:5173" target="_blank">http://localhost:5173</a> - Vue.js前端界面</p>
            </div>
        </div>
    </body>
    </html>
    """)

urlpatterns = [
    path('', api_home),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]