@echo off

SET dest="C:\hlserver\tf2\tf\addons\source-python\plugins\deepsurf"

rmdir /s /q %dest%
robocopy /s /e ".\addons\source-python\plugins\deepsurf" %dest%