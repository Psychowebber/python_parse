# python_parse
Adds functionality to parse nginx logs.
This script is designed to pull NGINX logs out of the domains logs directory, parse them and provide you with the desired informaiton within the designated timeframe.

## SETUP
Once the repo is cloned, create a `credentials.py` file with the following inside:

```
apikey="[ABUSE IP DB API KEY HERE]"
```

Note that the API key NEEDS to be contained in a string for Python to use it. If not, it will throw an error.

## USAGE:
- Using Python3, run `python3 parse.py`.
- The script will prompt you for the domain name (example: `foobar.com`). The script will automatically use this value to find the website docroot and relevant access log files.
- The script will prompt you for a value. This is how far back into the logs you want to go parse.. For example, if you want it to parse the last 4 hours and 12 minutes of activity, you would enter `4.12` (NOTE THE DECIMAL INSTEAD OF COLON). The script will then enter "4hrs 12min".

## FLAG USAGE

You can also set flags instead of interactive input.

ADD ADDITONAL FLAG INFORMATION HERE

--domain      Allows you to auto include the domain in the request.
--time        Allows you to auto include the timeframe in the request.

Example:
python3 parse.py --domain="foobar.com" --time="1.15"
This will result in parsing foobar.com for the last 1hr 15minutes
