# Install

* Copy config.py.example to config.py and replace the variables
* Add this in you crontab :
    */2 * * * *  DISPLAY=:0.0 $HOME/.bin/unread/unread.py > /dev/null 2>&1

