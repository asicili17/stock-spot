class FakeAlphaVantageClient:
    def __init__(self, payloads): self.payloads = payloads
    def _make_api_request(self, params): return self.payloads[params['function']]
