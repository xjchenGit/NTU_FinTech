class Strategy:
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, "")

    def __getattr__(self, key):
        if key in self.options:
            return int(self.options.get(key, ""))

    def __init__(self):
        # strategy property
        self.subscribedBooks = {
            "Binance": {"pairs": ["BTC-USDT"]},
        }
        self.period = 15 * 60
        self.options = {}

        # user defined class attribute
        self.eth_trace = np.empty((0, 5))
        self.grid_variable = {}
        self.kk_variable = {"warehouse": 0}

    def kk(self, current_status, max_value):
        kernel = talib.SMA(
            (self.eth_trace[:, 1] + self.eth_trace[:, 2] + self.eth_trace[:, 3]) / 3,
            int(self.options["MA"]),
        )[1:]
        true_range = np.max(
            [
                self.eth_trace[1:, 2] - self.eth_trace[1:, 3],
                np.abs(self.eth_trace[1:, 2] - self.eth_trace[:-1, 1]),
                np.abs(self.eth_trace[1:, 3] - self.eth_trace[:-1, 1]),
            ],
            axis=0,
        )
        upper_bound = kernel + float(self.options["multi"]) * true_range

        curr_kernel = kernel[-1]
        last_kernel = kernel[-2]
        if curr_kernel > last_kernel and (
            upper_bound[-2] > self.eth_trace[-2, 1]
            and self.eth_trace[-1, 1] > upper_bound[-1]
        ):
            amount = max_value / np.around(current_status["close"], 2)
            self.kk_variable["warehouse"] += amount
            return amount
        if self.eth_trace[-2, 1] > last_kernel and curr_kernel > self.eth_trace[-1, 1]:
            remain = self.kk_variable["warehouse"]
            self.kk_variable["warehouse"] = 0
            return -remain

    def eth(self, information):
        exchange = list(information["candles"])[0]
        pair = list(information["candles"][exchange])[0]
        current_status = information["candles"][exchange][pair][0]
        asset_USDT = information["assets"][exchange]["USDT"]

        # add latest price into trace
        self.eth_trace = np.append(
            self.eth_trace,
            [
                [
                    current_status["open"],
                    current_status["close"],
                    current_status["high"],
                    current_status["low"],
                    current_status["volume"],
                ]
            ],
            axis=0,
        )

        if self.eth_trace.shape[0] < 24:
            return []

        kk_amount = self.kk(current_status, asset_USDT)
        orders = []
        for amount in [kk_amount]:
            if not amount:
                continue

            if amount > 0:
                orders.append(
                    {
                        "exchange": exchange,
                        "amount": amount,
                        "price": -1,
                        "type": "MARKET",
                        "pair": pair,
                    }
                )
            if amount < 0:
                orders.append(
                    {
                        "exchange": exchange,
                        "amount": amount,
                        "price": current_status["close"] * 1.01,
                        "type": "LIMIT",
                        "pair": pair,
                    }
                )
        return orders

    # called every self.period
    def trade(self, information):
        orders = []
        orders += self.eth(information)
        return orders
