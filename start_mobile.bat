@echo off
chcp 65001 >nul
echo ==============================================
echo   考研804知识库 - 一体化启动 (手机端可用)
echo ==============================================
echo.
echo [1/2] 构建前端...
cd /d "%~dp0frontend"
call npm run build
if %ERRORLEVEL% neq 0 (
    echo 前端构建失败，请检查错误信息
    pause
    exit /b 1
)
echo.
echo [2/2] 启动后端服务...
cd /d "%~dp0backend"
echo.
echo ==============================================
echo   启动成功！
echo   电脑访问: http://localhost:8000
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr /v "192.168.146" ^| findstr /v "192.168.60"') do set LAN_IP=%%a
set LAN_IP=%LAN_IP: =%
if not "%LAN_IP%"=="" (
    echo   手机访问: http://%LAN_IP%:8000
)
echo.
echo   手机添加到主屏幕: Safari 分享按钮 → 添加到主屏幕
echo ==============================================
echo.
python run_prod.py
pause
