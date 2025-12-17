from __future__ import annotations

import pytest

from farfan_pipeline.dashboard_atroz_.api_v1_store import AtrozStore


@pytest.mark.asyncio
async def test_store_bootstraps_170_municipalities_and_16_regions() -> None:
    store = AtrozStore()

    regions = await store.list_regions()
    assert len(regions) == 16

    total_municipalities = 0
    for region in regions:
        municipalities = await store.list_region_municipalities(region.id)
        total_municipalities += len(municipalities)

    assert total_municipalities == 170

