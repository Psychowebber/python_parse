import credentials # NEED TO INSERT API KEY AS STRING IN CREDENTIALS.PY (apikey="KEY HERE")
import subprocess

def ipCheck(ip): 
    # Call Abuse IP DB API with script
    apikey = credentials.apikey
    ipAddressString = '--data-urlencode "ipAddress={ip}"'.format(ip=ip)
    keyString = '-H "Key: {apikey}"'.format(apikey=apikey)
    # Contruct curl command for hitting API endpoint
    command =  ['curl',
                '-sG',
                'https://api.abuseipdb.com/api/v2/check',
                '--data-urlencode',
                'ipAddress={ip}'.format(ip=ip),
                '-d',
                'maxAgeInDays=90',
                '-d',
                'verbose',
                '-H',
                'Key:{apikey}'.format(apikey=apikey),
                '-H',
                '"Accept: application/json"']
    results = subprocess.run(command, capture_output=True, text=True)
    return results.stdout