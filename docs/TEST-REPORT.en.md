# Location Assistant 0.3 · Test report

[中文报告](TEST-REPORT.md) · [English user guide](../README.en.md)

Tested on Windows 11 x64 with Python 3.14.7 and Tk 9.0. The phone backend remains pinned to pymobiledevice3 11.63.1.

## Display and interaction

The previous map always used 112 pixels of height while its width followed the window. A wider window stretched the continents sideways. Version 0.3 draws the world in a 2:1 equirectangular viewport. The marker and mouse use the same degrees-per-pixel scale. Extra space stays outside the map. Dragging a point updates the marker without redrawing the land geometry on every mouse event.

| Check | Observed result |
| --- | --- |
| Windows executable | Opened the desktop window and launched the external Python runtime. Windows reported Per-Monitor V2 awareness and 144 DPI (150% scaling). |
| Map interaction | A press, drag and release on the Tk canvas selected a point in the southern and western hemispheres. The coordinate fields matched the expected values within half a map pixel, the preset switched to Custom, and the device-action dispatcher was never called. |
| Language switch | The same custom coordinates and page remained selected after switching to English and back. The English IP lookup prompt retained its confirmation step. The preference file recorded the selected language. |
| Automated checks | All 15 passed, including the existing process, recovery, input, privacy and iOS version tests. |
 
The English and Chinese screenshots show the actual application with the Paris preset. This release was checked at the reported display scale. Moving a running window between physical monitors with different scales has not been tested.

## Device testing

The earlier 0.2 session used an iPhone 14 Pro on iOS 26.7.1. The computer identified one USB phone, read the model and system version, and completed a read-only developer-service request over a userspace tunnel. No new on-device location change was performed for the 0.3 interface tests.

Earlier command-line records contain a Tokyo set command, a Los Angeles set command and a clear command. They establish what was invoked. They do not contain an independently observed Maps position after each command. Older iOS command routes were checked with CLI help and automated tests; those versions still need hardware testing.

For a full phone test, record the starting region, select a distant city, and note when the phone first reports it. Keep USB connected for five minutes and request another fix. Then clear the simulation and record how long the phone takes to return to its original region. The model, iOS version and timings are sufficient; private addresses and device IDs are unnecessary.
