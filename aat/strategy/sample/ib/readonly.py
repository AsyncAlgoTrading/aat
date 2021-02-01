if __name__ == "__main__":
    from aat import TradingEngine, parseConfig

    cfg = parseConfig(
        [
            "--trading_type",
            "live",
            "--load_accounts",
            "--exchanges",
            "aat.exchange.public.ib:InteractiveBrokersExchange",
            "--strategies",
            "aat.strategy.sample.readonly:ReadOnlyStrategy",
        ]
    )
    print(cfg)
    t = TradingEngine(**cfg)
    t.start()
