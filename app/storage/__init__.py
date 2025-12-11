# (1.) Storage package
# (2.) Contains storage backend implementations

from app.storage.backend import InMemoryStorage, StorageBackend

__all__ = ["StorageBackend", "InMemoryStorage"]
