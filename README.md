# MLM2PRO-GSPro-Connector
GSPro connector for the MLM2Pro Launch Monitor.

## Highlights:

1. User Friendly
   - Menu to access all application functions.
   - Allows you to easily manage & select from multiple devices
   
2. Performance:
   - True multithreading with keyboard, screenshot, shot processing, GSPRO communication all running in seperate threads.
   - Direct use of Windows API which improves performance and reduces reliance on third party libraries.
   - Use of the above allows the connector to efficiently check & process a shot giving almost instant reponse times.

3. Maintainability:
   - Uses Object-oriented programming techniques.
   - Code seperated into easily maintainable classes.

## Documentation

Getting Started guid and other documentation can be found [here](https://github.com/springbok/MLM2PRO-GSPro-Connector/wiki)

## Latest Release

The latest release can be downloaded from [here](https://github.com/springbok/MLM2PRO-GSPro-Connector/releases)

## Acknowledgment

### Original Connector
* Thank you to [rowenb](https://github.com/rowengb) for producing the first [connector](https://github.com/rowengb/GSPro-MLM2PRO-OCR-Connector), this connector uses the same technique of taking a screenshot of a mirror of the device running the Rapsodo app, it then extracts the shot metrics using OCR and transmits the result to GSPro.   
* [woner99](https://github.com/wonder99) for his testing, suggestions, & feedback.