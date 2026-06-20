import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.strategy import Strategy
from app.repositories.strategy_repository import StrategyRepository
from app.schemas import StrategyCreate, StrategyResponse, StrategyUpdate
from app.utils.serializers import strategy_to_response

router = APIRouter(prefix="/strategies", tags=["Strategies"])


@router.get("", response_model=list[StrategyResponse])
def list_strategies(db: Session = Depends(get_db)):
    repo = StrategyRepository(db)
    return [strategy_to_response(s) for s in repo.list_strategies()]


@router.post("", response_model=StrategyResponse, status_code=201)
def create_strategy(payload: StrategyCreate, db: Session = Depends(get_db)):
    repo = StrategyRepository(db)
    strategy = Strategy(
        name=payload.name,
        description=payload.description,
        screening_rules=json.dumps([r.model_dump() for r in payload.screening_rules]),
        ranking_rules=json.dumps([r.model_dump() for r in payload.ranking_rules]),
    )
    return strategy_to_response(repo.create(strategy))


@router.get("/{strategy_id}", response_model=StrategyResponse)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    repo = StrategyRepository(db)
    strategy = repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy_to_response(strategy)


@router.put("/{strategy_id}", response_model=StrategyResponse)
def update_strategy(
    strategy_id: int, payload: StrategyUpdate, db: Session = Depends(get_db)
):
    repo = StrategyRepository(db)
    strategy = repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if payload.name is not None:
        strategy.name = payload.name
    if payload.description is not None:
        strategy.description = payload.description
    if payload.screening_rules is not None:
        strategy.screening_rules = json.dumps([r.model_dump() for r in payload.screening_rules])
    if payload.ranking_rules is not None:
        strategy.ranking_rules = json.dumps([r.model_dump() for r in payload.ranking_rules])

    return strategy_to_response(repo.update(strategy))


@router.delete("/{strategy_id}", status_code=204)
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    repo = StrategyRepository(db)
    strategy = repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    repo.delete(strategy)
