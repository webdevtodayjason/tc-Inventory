"""fix_cpu_speed_format

Revision ID: fix_cpu_speed_format
Revises: 14cc056cb513
Create Date: 2025-02-06 15:48:16.784123

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import os

# revision identifiers, used by Alembic.
revision = 'fix_cpu_speed_format'
down_revision = '14cc056cb513'
branch_labels = None
depends_on = None

def upgrade():
    # Create a temporary table for CPUs
    op.execute("""
        CREATE TABLE cpu_temp (
            id int4 NOT NULL DEFAULT nextval('cpu_id_seq'::regclass),
            manufacturer varchar(64) NOT NULL,
            model varchar(128) NOT NULL,
            speed varchar(32),
            cores int4,
            created_at timestamp DEFAULT CURRENT_TIMESTAMP,
            benchmark int4,
            PRIMARY KEY (id)
        )
    """)
    
    # Copy data from cpu to cpu_temp with standardized speed format
    op.execute("""
        INSERT INTO cpu_temp (id, manufacturer, model, speed, cores, created_at, benchmark)
        SELECT 
            id,
            manufacturer,
            model,
            CASE 
                WHEN speed::text ILIKE '%GHz' THEN 
                    CASE 
                        WHEN speed::text LIKE '% GHz' THEN speed
                        ELSE REPLACE(speed::text, 'GHz', ' GHz')
                    END
                WHEN speed::text ILIKE '%MHz' THEN 
                    ROUND((REGEXP_REPLACE(speed::text, '[^0-9.]', '', 'g')::numeric) / 1000, 2)::text || ' GHz'
                ELSE speed::text || ' GHz'
            END as speed,
            cores,
            created_at,
            benchmark
        FROM cpu
    """)
    
    # Drop the foreign key constraint
    op.execute('ALTER TABLE computer_systems DROP CONSTRAINT computer_systems_cpu_id_fkey')
    
    # Drop the original cpu table
    op.execute('DROP TABLE cpu')
    
    # Rename temp table to cpu
    op.execute('ALTER TABLE cpu_temp RENAME TO cpu')
    
    # Recreate the foreign key constraint
    op.execute("""
        ALTER TABLE computer_systems 
        ADD CONSTRAINT computer_systems_cpu_id_fkey 
        FOREIGN KEY (cpu_id) REFERENCES cpu(id)
    """)

def downgrade():
    # Since this is a data fix, we don't want to provide a downgrade path
    # as it would be difficult to revert the speed format changes accurately
    pass 