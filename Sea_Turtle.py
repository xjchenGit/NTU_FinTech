# Class name must be Strategy
class Strategy():
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, '')

    def __init__(self):
        # strategy property needed
        self.subscribedBooks = {
            'BINANCE': {
                'pairs': ['BTC-USDT'],
            },
        }

        # seconds for broker to call trade()
        # do not set the frequency below 60 sec.
        # 10 * 60 for 10 mins
        self.period = 10 * 60
        self.options = {}
        
        # user defined class attribute
        self.last_type = 'sell'
        self.high_price_trace = np.array([])
        self.low_price_trace = np.array([])
        self.close_price_trace = np.array([])
        self.MAX_high_price = np.array([])
        self.MIN_low_price = np.array([])
        self.yesterday_price = 0
        self.high_long = 20
        self.low_long = 10
        self.Acceleration = 0
        self.up = 1
        self.down = 2
        self.ATR = 0
    
    def get_prediction(self):
        self.yesterday_price = self.close_price_trace
        yesP = float(str(self.yesterday_price[len(self.yesterday_price)-1]))
        if np.isnan(yesP) or np.isnan(self.MAX_high_price) or np.isnan(self.MIN_low_price):
            return None
        if  self.MAX_high_price > yesP :
            return self.up
        elif  (self.MIN_low_price + 20) < yesP  :
            return self.down

    # called every self.period
    def trade(self, information):
        # for single pair strategy, user can choose which exchange/pair to use when launch, get current exchange/pair from information
        exchange = list(information['candles'])[0]
        pair = list(information['candles'][exchange])[0]
        high_price = information['candles'][exchange][pair][0]['high']
        # Log('high_price: ' + self.high_price_trace)
        low_price = information['candles'][exchange][pair][0]['low']
        close_price = information['candles'][exchange][pair][0]['close']

        self.high_price_trace = np.append(self.high_price_trace, [float(high_price)]) 
        #Log('high_price_trace: ' + str(self.high_price_trace))
        self.low_price_trace = np.append(self.low_price_trace, [float(low_price)])
        #Log('low_price_trace: ' + str(self.low_price_trace))
        self.close_price_trace = np.append(self.close_price_trace, [float(close_price)])
        # Log('close_price_trace: ' + str(self.close_price_trace))
        self.high_price_trace = self.high_price_trace[ -self.high_long: ]
        #Log('high_price_trace: ' + str(self.high_price_trace))
        self.low_price_trace = self.low_price_trace[ -self.low_long: ]
        #Log('low_price_trace: ' + str(self.low_price_trace))

        self.close_price_trace = self.close_price_trace[ -self.low_long: ]

        self.MAX_high_price = np.max(self.high_price_trace)
        #Log('MAX_high_price: ' + str(self.MAX_high_price))
        self.MIN_low_price = np.min(self.low_price_trace)
        #Log('MIN_low_price: ' + str(self.MIN_low_price))
        cur_state = self.get_prediction()
        #Log( 'info: ' + str(cur_state) )

        if cur_state == self.up:
            if self.last_type == 'buy':
                self.Acceleration += 1
            else:
                self.Acceleration = 0
            self.last_type = 'buy'

            return [
                {
                    'exchange': exchange,
                    'amount':  2^(self.Acceleration),
                    'price':  -1, # -1
                    'type': 'MARKET',
                    'pair': pair,
                },
            ]
        elif cur_state == self.down :
            # if self.last_type == 'sell':
            #     self.decline += 1
            # elif self.last_type != 'sell':
            #     self.decline = 0
            self.last_type = 'sell'
            return [
                {
                    'exchange': exchange,
                    'amount':  -1,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                },
            ]
        return []
