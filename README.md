# python_parse
Adds functionality to parse nginx logs.
This script is designed to pull NGINX logs out of the domains logs directory, parse them and provide you with the desired informaiton within the designated timeframe.

USE:
Using Pyhton3, `python3 parse.py`
It will prompt for the domain name
`bob.com`
The script will automatically input this value into both the docroot and the name of the access log.
It will ask for a value. This is the amount of time you want it to use relavant to the server. For example, if you want it to parse the last 4 hours and 12 minutes,
you would enter "4.12". The script will then enter "4hrs 12min".

You can also use flags.

--domain      Allows you to auto include the domain in the request.
--time        Allows you to auto include the timeframe in the request.

Example:
python3 parse.py --domain="example.com" --time="1.15"
This will result in parsing example.com for the last 1hr 15minutes
