from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..auth import require_roles
from ..database import get_db
from ..models import Product, ProductCategory, Recipe, RecipeItem, User, UserRole
from ..schemas import ProductCreate, ProductOut, RecipeCreate, RecipeOut

router = APIRouter(tags=["products"])


@router.get("/products", response_model=list[ProductOut])
def list_products(
    category: ProductCategory | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.factory_manager,
            UserRole.accountant,
            UserRole.warehouse,
            UserRole.production_supervisor,
        )
    ),
):
    query = select(Product).order_by(Product.id).offset(skip).limit(limit)
    if category is not None:
        query = query.where(Product.category == category)
    return db.scalars(query).all()


@router.post("/products", response_model=ProductOut)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.accountant)
    ),
):
    existing = db.scalar(select(Product).where(Product.code == payload.code))
    if existing:
        raise HTTPException(status_code=409, detail="Product code already exists")
    row = Product(**payload.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product code already exists") from exc
    db.refresh(row)
    return row


@router.post("/recipes")
def create_recipe(
    payload: RecipeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin, UserRole.factory_manager, UserRole.production_supervisor
        )
    ),
):
    finished = db.get(Product, payload.finished_product_id)
    if not finished:
        raise HTTPException(status_code=404, detail="Finished product not found")
    recipe = Recipe(finished_product_id=payload.finished_product_id)
    db.add(recipe)
    db.flush()
    for item in payload.items:
        if not db.get(Product, item.ingredient_product_id):
            raise HTTPException(
                status_code=404,
                detail=f"Ingredient {item.ingredient_product_id} not found",
            )
        db.add(
            RecipeItem(
                recipe_id=recipe.id,
                ingredient_product_id=item.ingredient_product_id,
                qty_per_kg_output=item.qty_per_kg_output,
            )
        )
    db.commit()
    return {"recipe_id": recipe.id, "item_count": len(payload.items)}


@router.get("/recipes", response_model=list[RecipeOut])
def list_recipes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin, UserRole.factory_manager, UserRole.production_supervisor
        )
    ),
):
    # Load recipes with items in one query (fixes N+1)
    recipes = db.scalars(
        select(Recipe)
        .order_by(Recipe.id)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Recipe.items))
    ).all()

    # Single query for product name/code lookup
    product_map = {
        row.id: {"code": row.code, "name": row.name}
        for row in db.execute(select(Product.id, Product.code, Product.name)).all()
    }

    out = []
    for recipe in recipes:
        finished = product_map.get(recipe.finished_product_id, {})
        out.append(
            {
                "id": recipe.id,
                "finished_product_id": recipe.finished_product_id,
                "finished_code": finished.get("code"),
                "finished_name": finished.get("name"),
                "items": [
                    {
                        "ingredient_product_id": it.ingredient_product_id,
                        "ingredient_name": product_map.get(it.ingredient_product_id, {}).get("name"),
                        "ingredient_code": product_map.get(it.ingredient_product_id, {}).get("code"),
                        "qty_per_kg_output": round(it.qty_per_kg_output, 4),
                    }
                    for it in recipe.items
                ],
            }
        )
    return out
