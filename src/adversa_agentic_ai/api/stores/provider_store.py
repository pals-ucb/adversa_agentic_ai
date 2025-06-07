from ..schemas.providers import Provider

class ProviderStore:
    def __init__(self):
        self.db = {}

    def save(self, provider: Provider) -> Provider:
        self.db[provider.id] = provider
        return provider

    def get(self, provider_id: str) -> Provider | None:
        return self.db.get(provider_id)

    def update(self, provider_id: str, provider: Provider) -> Provider:
        self.db[provider_id] = provider
        return provider

    def delete(self, provider_id: str):
        self.db.pop(provider_id, None)

    def list_all(self) -> list[Provider]:
        return list(self.db.values())
