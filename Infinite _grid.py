class Strategy():
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, '')

    def __init__(self):
        self.subscribedBooks = {
            'Binance': {
                'pairs': ['MIOTA-USDT'],
            },
        }
        self.period = 10 * 60
        self.options = {}
    
    def trade(self, information): 
        exchange = list(information['candles'])[0]
        pair = list(information['candles'][exchange])[0] 
        if information['candles'][exchange][pair][0]['close'] < 0.29:
            return [
                {
                'exchange': exchange,
                'amount': -1 * self['assets'][exchange]['MIOTA'],
                'price': -1,
                'type': 'MARKET',
                'pair': pair,
                }
            ]
        return [
            {
                'exchange': exchange,
                'amount': (8000 - information['candles'][exchange][pair][0]['close'] * self['assets'][exchange]['MIOTA'])/information['candles'][exchange][pair][0]['close'],
                'price': -1,
                'type': 'MARKET',
                'pair': pair,
            }
        ]
