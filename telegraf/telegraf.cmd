@echo off

echo "Starting Telegraf..."
cd %programfiles%\InfluxData\telegraf

telegraf.exe --config telegraf.conf
pause