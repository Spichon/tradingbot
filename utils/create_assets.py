from tradingbot.cotation import cotation_kraken
public_kraken = cotation_kraken()
assets = public_kraken.get_available_assets()
for asset in assets:
    if (assets[asset]['quote']) == 'ZEUR':
        if (assets[asset]['altname']).endswith('.d') is False:
            print(assets[asset]['altname'])
            print(assets[asset]['base'])
            print(assets[asset]['quote'])