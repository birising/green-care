"""Initial PostGIS schema"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


issue_status = sa.Enum("open", "in_progress", "resolved", name="issue_status")


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "greens",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("polygon", Geometry(geometry_type="POLYGON", srid=4326), nullable=False),
        sa.Column("frequency_days", sa.Integer(), nullable=False),
        sa.Column("last_mowed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("frequency_days > 0", name="ck_greens_frequency_positive"),
    )

    op.create_table(
        "lamps",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("point", Geometry(geometry_type="POINT", srid=4326), nullable=False),
    )

    op.create_table(
        "bins",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("point", Geometry(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("last_fill_level", sa.Numeric(5, 2)),
        sa.Column("last_battery_level", sa.Numeric(5, 2)),
        sa.Column("last_temperature", sa.Numeric(5, 2)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "bin_telemetry",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "bin_id",
            sa.BigInteger(),
            sa.ForeignKey("bins.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("fill_level", sa.Numeric(5, 2)),
        sa.Column("battery_level", sa.Numeric(5, 2)),
        sa.Column("temperature", sa.Numeric(5, 2)),
        sa.Column("at_time", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "lamp_issues",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "lamp_id",
            sa.BigInteger(),
            sa.ForeignKey("lamps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", issue_status, nullable=False, server_default="open"),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("reported_by", sa.Text(), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("resolution_note", sa.Text()),
    )

    op.create_table(
        "bin_issues",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "bin_id",
            sa.BigInteger(),
            sa.ForeignKey("bins.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", issue_status, nullable=False, server_default="open"),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("reported_by", sa.Text(), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("resolution_note", sa.Text()),
    )

    op.create_index("idx_greens_geom", "greens", ["polygon"], postgresql_using="gist")
    op.create_index("idx_lamps_geom", "lamps", ["point"], postgresql_using="gist")
    op.create_index("idx_bins_geom", "bins", ["point"], postgresql_using="gist")
    op.create_index("idx_bin_telemetry_bin_time", "bin_telemetry", ["bin_id", sa.text("at_time DESC")])
    op.create_index("idx_lamp_issues_status", "lamp_issues", ["status"])
    op.create_index("idx_bin_issues_status", "bin_issues", ["status"])


def downgrade():
    op.drop_index("idx_bin_issues_status", table_name="bin_issues")
    op.drop_index("idx_lamp_issues_status", table_name="lamp_issues")
    op.drop_index("idx_bin_telemetry_bin_time", table_name="bin_telemetry")
    op.drop_index("idx_bins_geom", table_name="bins")
    op.drop_index("idx_lamps_geom", table_name="lamps")
    op.drop_index("idx_greens_geom", table_name="greens")

    op.drop_table("bin_issues")
    op.drop_table("lamp_issues")
    op.drop_table("bin_telemetry")
    op.drop_table("bins")
    op.drop_table("lamps")
    op.drop_table("greens")

    issue_status.drop(op.get_bind(), checkfirst=True)
    op.execute("DROP EXTENSION IF EXISTS postgis")
