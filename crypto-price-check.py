import datetime
import json
import locale
import sys
import urllib.request

def extract_price(prices, time_offset, time_step=10):
    try:
        return float(prices[int(time_offset / time_step)]['price'])
    except IndexError:
        return None

utility_options = {
    'currency': 'USD',
    'apiVersion': '2017-05-19',
}

locale.setlocale(locale.LC_MONETARY, 'en_US.utf8')

api_endpoint_url = 'https://api.coinbase.com/v2/prices/BTC-{currency}/historic'.format(
    currency = utility_options['currency'],
)

api_request = req = urllib.request.Request(api_endpoint_url, None, {
    'CB-VERSION': utility_options['apiVersion'],
})

try:
    with urllib.request.urlopen(api_request) as response:
        api_response = response.read()
except urllib.error.HTTPError as e:
    if (e.code == 400):
        api_response = e.read()
    else:
        print('Failed to contact the Coinbase API: {}'.format(e.code))

        sys.stderr.write(
            json.dumps(json.loads(e.read()), sort_keys=True, indent=4)
        )
        sys.exit(1)

api_response = json.loads(api_response)

api_error = next(
    iter(
        api_response.get('errors', [None])
    )
)

if (api_error is not None):
    print('Client error: {}'.format(api_error['message']))
    sys.exit(1)

prices = {
    'current': extract_price(api_response['data']['prices'], time_offset=0),
    'past': extract_price(api_response['data']['prices'], time_offset=3600),
}

price_difference = ((prices['current'] - prices['past']) / prices['past']) * 100

print('The current price of Bitcoin is {price}. The price change is {diff:+.02f}%. <{chartUrl}|View chart>'.format(
    price = locale.currency(prices['current'], grouping=True),
    diff = price_difference,
    chartUrl = 'https://www.coinbase.com/charts',
))
