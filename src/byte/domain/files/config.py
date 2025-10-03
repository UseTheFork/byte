from pydantic import BaseModel


class WatchConfig(BaseModel):
    enable: bool = True


class FilesConfig(BaseModel):
    watch: WatchConfig = WatchConfig()
