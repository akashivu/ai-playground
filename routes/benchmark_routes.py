from fastapi import APIRouter

from core.dependencies import (benchmark_service,)

router = APIRouter()


@router.post("/benchmark")
async def run_benchmark():

    report = await (benchmark_service.run_benchmark())

    return report