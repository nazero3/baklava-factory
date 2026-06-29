"""add indexes, audit fields, and sale price

Revision ID: 5c3d9e1a7f8b
Revises: 3a7c1f9b2e10
Create Date: 2026-06-19 21:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "5c3d9e1a7f8b"
down_revision: Union[str, None] = "3a7c1f9b2e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- new columns ---
    # Note: ForeignKey constraints are omitted from ALTER ADD COLUMN statements
    # because SQLite does not support adding constraints via ALTER TABLE.
    # The FK relationship is enforced at the ORM / application layer.
    op.add_column("receivings", sa.Column("created_by_user_id", sa.Integer(), nullable=True))
    op.add_column("production_batches", sa.Column("created_by_user_id", sa.Integer(), nullable=True))
    op.add_column("transfers", sa.Column("created_by_user_id", sa.Integer(), nullable=True))
    op.add_column("store_movements", sa.Column("unit_price", sa.Float(), nullable=False, server_default="0"))
    op.add_column("store_movements", sa.Column("created_by_user_id", sa.Integer(), nullable=True))

    # --- indexes ---
    op.create_index("ix_receivings_supplier_id", "receivings", ["supplier_id"])
    op.create_index("ix_receivings_product_id", "receivings", ["product_id"])
    op.create_index("ix_receivings_created_at", "receivings", ["created_at"])
    op.create_index(
        "ix_production_batches_finished_product_id",
        "production_batches",
        ["finished_product_id"],
    )
    op.create_index("ix_production_batches_created_at", "production_batches", ["created_at"])
    op.create_index("ix_transfers_product_id", "transfers", ["product_id"])
    op.create_index("ix_transfers_to_store_id", "transfers", ["to_store_id"])
    op.create_index("ix_transfers_status", "transfers", ["status"])
    op.create_index("ix_store_movements_store_id", "store_movements", ["store_id"])
    op.create_index("ix_store_movements_product_id", "store_movements", ["product_id"])
    op.create_index("ix_store_movements_movement_type", "store_movements", ["movement_type"])
    op.create_index("ix_inventory_adjustments_product_id", "inventory_adjustments", ["product_id"])
    op.create_index("ix_inventory_adjustments_status", "inventory_adjustments", ["status"])
    op.create_index("ix_transfer_exceptions_transfer_id", "transfer_exceptions", ["transfer_id"])
    op.create_index("ix_transfer_exceptions_status", "transfer_exceptions", ["status"])
    op.create_index("ix_recipe_items_recipe_id", "recipe_items", ["recipe_id"])
    op.create_index("ix_inventory_product_id", "inventory", ["product_id"])
    op.create_index("ix_recipes_finished_product_id", "recipes", ["finished_product_id"])
    op.create_index(
        "ix_recipe_items_ingredient_product_id", "recipe_items", ["ingredient_product_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_recipe_items_ingredient_product_id", "recipe_items")
    op.drop_index("ix_recipes_finished_product_id", "recipes")
    op.drop_index("ix_inventory_product_id", "inventory")
    op.drop_index("ix_recipe_items_recipe_id", "recipe_items")
    op.drop_index("ix_transfer_exceptions_status", "transfer_exceptions")
    op.drop_index("ix_transfer_exceptions_transfer_id", "transfer_exceptions")
    op.drop_index("ix_inventory_adjustments_status", "inventory_adjustments")
    op.drop_index("ix_inventory_adjustments_product_id", "inventory_adjustments")
    op.drop_index("ix_store_movements_movement_type", "store_movements")
    op.drop_index("ix_store_movements_product_id", "store_movements")
    op.drop_index("ix_store_movements_store_id", "store_movements")
    op.drop_index("ix_transfers_status", "transfers")
    op.drop_index("ix_transfers_to_store_id", "transfers")
    op.drop_index("ix_transfers_product_id", "transfers")
    op.drop_index("ix_production_batches_created_at", "production_batches")
    op.drop_index("ix_production_batches_finished_product_id", "production_batches")
    op.drop_index("ix_receivings_created_at", "receivings")
    op.drop_index("ix_receivings_product_id", "receivings")
    op.drop_index("ix_receivings_supplier_id", "receivings")

    op.drop_column("store_movements", "created_by_user_id")
    op.drop_column("store_movements", "unit_price")
    op.drop_column("transfers", "created_by_user_id")
    op.drop_column("production_batches", "created_by_user_id")
    op.drop_column("receivings", "created_by_user_id")
