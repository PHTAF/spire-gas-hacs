from __future__ import annotations

import asyncio
from typing import Any, Dict

import aiohttp

from .const import HTTP_TIMEOUT_SECONDS


class SpireApiError(Exception):
    """Base API error."""


class SpireAuthError(SpireApiError):
    """Authentication error."""


class SpireClient:
    BASE_URL = "https://myaccount.spireenergy.com"

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._lock = asyncio.Lock()
        self._logged_in = False
        self._timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT_SECONDS)

    async def login_only(self) -> None:
        url = f"{self.BASE_URL}/o/rest/mfa/v1.0/login"
        payload = {"userName": self._username, "password": self._password, "rememberMe": True}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            async with self._session.post(url, json=payload, headers=headers, timeout=self._timeout) as resp:
                if resp.status in (401, 403):
                    raise SpireAuthError("Invalid credentials")
                if resp.status >= 400:
                    text = await resp.text()
                    raise SpireApiError(f"Login failed ({resp.status}): {text[:200]}")
                self._logged_in = True
        except asyncio.TimeoutError as err:
            raise SpireApiError("Login timed out") from err

    async def _ensure_login(self) -> None:
        if self._logged_in:
            return
        async with self._lock:
            if not self._logged_in:
                await self.login_only()

    async def get_daily_usage_history(self, account_id: str, sa_id: str) -> Dict[str, Any]:
        await self._ensure_login()

        url = f"{self.BASE_URL}/o/rest/accounts/api/v1/usage-graphical-history/{account_id}/daily-usage-history"
        params = {"sald": sa_id}
        headers = {"Accept": "application/json"}

        async def _do_get() -> Dict[str, Any]:
            async with self._session.get(url, params=params, headers=headers, timeout=self._timeout) as resp:
                if resp.status in (401, 403):
                    raise SpireAuthError("Not authorized (session expired)")
                if resp.status >= 400:
                    text = await resp.text()
                    raise SpireApiError(f"Request failed ({resp.status}): {text[:200]}")
                try:
                    return await resp.json(content_type=None)
                except Exception:
                    text = await resp.text()
                    raise SpireApiError(f"Invalid JSON response: {text[:200]}")

        try:
            return await _do_get()
        except SpireAuthError:
            # Relogin once and retry
            self._logged_in = False
            await self._ensure_login()
            return await _do_get()
        except asyncio.TimeoutError as err:
            raise SpireApiError("Usage request timed out") from err
