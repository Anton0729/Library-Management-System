"""Update models

Revision ID: b660074bea52
Revises: a325926514e0
Create Date: 2024-10-16 20:12:47.243348

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b660074bea52"
down_revision: Union[str, None] = "a325926514e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "books", ["title"])
    op.alter_column("genres", "name", existing_type=sa.VARCHAR(), nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("genres", "name", existing_type=sa.VARCHAR(), nullable=True)
    op.drop_constraint(None, "books", type_="unique")
    # ### end Alembic commands ###
