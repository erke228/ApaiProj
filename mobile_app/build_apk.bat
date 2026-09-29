@echo off
echo =======================================================
echo          Запуск сборки Ultimate SuperApp (APK)
echo =======================================================
echo.
echo Шаг 1: Принятие лицензий Android (если нужно, нажимайте 'y' и Enter)
call "C:\Users\dengi\Desktop\flutter\bin\flutter.bat" doctor --android-licenses

echo.
echo Шаг 2: Загрузка зависимостей
call "C:\Users\dengi\Desktop\flutter\bin\flutter.bat" pub get

echo.
echo Шаг 3: Сборка APK (может занять 5-10 минут)
call "C:\Users\dengi\Desktop\flutter\bin\flutter.bat" build apk

echo.
echo =======================================================
echo Сборка завершена! Если нет ошибок, ваш APK находится по пути:
echo C:\Users\dengi\Desktop\Defender\mobile_app\build\app\outputs\flutter-apk\app-release.apk
echo =======================================================
pause
