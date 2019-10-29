# PiCam

###Project Directory
* static - Directory of all static server files, such as images and databases
 * imgs - Directory that contains all saved webcam pictures
 * piCam.db - Database that stores all image information
 * webBackground.jpg - Website background image
* templates - All website pages, such as the index/home page
 * PiCam4b.html - Only web page, uses AJAX to update all aspects of the site
 * old - Older versions of piCam4b.html 
* piCam4.py - Flask web framework, handles all web page requests. 
 * Imported libraries:
    *  Pygame Python
    *  Sqlite3
    *  RPIO.PWM
