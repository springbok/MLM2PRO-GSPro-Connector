# MLM2PRO-GSPro-Connector
GSPro connector for the MLM2Pro Launch Monitor

Special thanks to rowengb for his work in producing the first connector, this connector uses some of his work. 

If you want to use his connector you can find it [here](https://github.com/rowengb/GSPro-MLM2PRO-OCR-Connector)

Please consider making a to him if you use his or my connector, you can donate [here](ko-fi.com/rowengb)

A Python app that interfaces the Rapsodo MLM2PRO golf launch monitor with the GSPro golf simulation software using OpenCV and TesserOCR.

Required:

1. Screen Mirroring App
  - iOS/iPhone - AirPlay app from Windows Store - https://www.microsoft.com/store/productId/9P6QSQ5PH9KR
  - Android - EasyCast app from Windows Store - https://www.microsoft.com/store/productId/9P8BH9SMXQMC (also requires Android app installation)

2. Rapsodo MLM2PRO App
  - iPhone/iPad - https://apps.apple.com/us/app/rapsodo-mlm2pro/id1659665092
  - Android - https://play.google.com/store/apps/details?id=com.rapsodo.MLM&hl=en_US&gl=US

3. Golf Balls
- Callaway® RPT™ Chrome Soft X® Golf Balls (3 Included in MLM2PRO box), these are necessary to accurately calculate Spin Axis and Spin Rate - https://rapsodo.com/products/callaway-rpt-chrome-soft-x-golf-balls

Steps:

1. Download the ZIP from v2.0, unzip it, and open the Settings.json file (https://github.com/rowengb/GSPro-MLM2PRO-OCR/releases/tag/v2.0).
2. By default, the WINDOW_NAME is set to "AirPlay" (for iOS), if you are using Android, change it to "EasyCast". Depending on if you're using an iPhone/iPad, also update the TARGET_HEIGHT and TARGET_WIDTH accordingly. Once done, save the file (Ctrl+S) and close it.
3. Open the Rapsodo MLM2PRO app, connect your Launch Monitor, and go to Simulation > Rapsodo Range.
4. If using a phone, click on the little arrow next to "Ball Speed" on the right to show all the metrics.
5. Mirror your phone/iPad screen to the AirPlay/EasyCast windows app (Depending on your OS).
6. Adjust the AirPlay/EasyCast window size so that the Rapsodo MLM2Pro App fills it out with little to no black borders/bars (Doesn't have to be perfect, the connector app will still work with black borders/bars but may not be as accurate) - (Example: https://ibb.co/DMHx12S).
7. Minimize the AirPlay/EasyCast application window (Important!).
8. Open GSPRO and GSPRO Connect Open API window (Go to Range or Local Match to test).
10. Run the MLM2PROConnectorV2.exe app file as ADMINISTRATOR (located in the previously downloaded/unzipped ZIP file) and wait for the "Press enter after you've hit your first shot" line to show.
11. Take your first shot, wait for the numbers to populate on the Rapsodo Range in the MLM2PRO app and then press the Enter key.
12. Set the ROIs for each shot metric one by one by creating rectangles around the desired value (See tutorial/example here - https://www.youtube.com/watch?v=zLptVv8umaU)
13. Done!

NOTE: Make sure to have GSPro, GSPro Connect and the AirPlay receiver app open and running before opening the MLM2PROConnectorV2.exe app otherwise it will just close instantly after pressing enter to confirm your first shot.

 
