from __future__ import annotations

from pydantic import BaseModel, ConfigDict, SecretStr, model_validator


class SecuritySettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    fernet_key: SecretStr | None = None
    allow_plaintext: bool = False

    @model_validator(mode="after")
    def _check_cipher(self) -> SecuritySettings:
        has_key = self.fernet_key is not None and bool(self.fernet_key.get_secret_value())
        if not has_key and not self.allow_plaintext:
            raise ValueError(
                "SECURITY__FERNET_KEY is required or SECURITY__ALLOW_PLAINTEXT must be true."
            )
        return self
