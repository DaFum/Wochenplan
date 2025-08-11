"""Update Task model with enums and due_date

Revision ID: update_task_model_enums
Revises: 23538eb60ee0
Create Date: 2025-08-11 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_task_model_enums'
down_revision = '23538eb60ee0'
branch_labels = None
depends_on = None


def upgrade():
    """Update Task model with new structure."""
    # Create new table with the updated structure
    op.create_table('task_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='taskpriority'), nullable=False),
        sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'COMPLETED', name='taskstatus'), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Migrate data from old table to new table
    # We'll create a mapping of old string IDs to new integer IDs
    connection = op.get_bind()
    
    # Get existing data
    result = connection.execute(sa.text("SELECT id, title, description, priority, status, start_time, end_time, [order] FROM task ORDER BY [order]"))
    rows = result.fetchall()
    
    # Insert data into new table
    for i, row in enumerate(rows, 1):
        # Get column values by name instead of position
        row_dict = dict(row._mapping)
    
        # Map string priority to enum
        priority_map = {
            'LOW': 'LOW',
            'MEDIUM': 'MEDIUM', 
            'HIGH': 'HIGH'
        }
        priority = priority_map.get(row_dict.get('priority', 'MEDIUM'), 'MEDIUM')
    
        # Map string status to enum  
        status_map = {
            'OPEN': 'OPEN',
            'IN_PROGRESS': 'IN_PROGRESS',
            'COMPLETED': 'COMPLETED'
        }
        status = status_map.get(row_dict.get('status', 'OPEN'), 'OPEN')
        
        # Use start_time as due_date if available
        due_date = row[5]  # start_time from old schema
        
        connection.execute(sa.text(
            "INSERT INTO task_new (id, title, description, priority, status, due_date, [order]) "
            "VALUES (:id, :title, :description, :priority, :status, :due_date, :order)"
        ), {
            'id': i,
            'title': row[1],
            'description': row[2],
            'priority': priority,
            'status': status,
            'due_date': due_date,
            'order': row[7] if len(row) > 7 else i  # Use existing order or assign sequential
        })
    
    # Drop old table and rename new table
    op.drop_table('task')
    op.rename_table('task_new', 'task')


def downgrade():
    """Revert Task model to previous structure."""
    # Create old table structure
    op.create_table('task_old',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Migrate data back (this will lose the integer IDs)
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT id, title, description, priority, status, due_date, [order] FROM task ORDER BY [order]"))
    rows = result.fetchall()
    
    import uuid
    for row in rows:
        connection.execute(sa.text(
            "INSERT INTO task_old (id, title, description, priority, status, start_time, end_time, [order]) "
            "VALUES (:id, :title, :description, :priority, :status, :start_time, :end_time, :order)"
        ), {
            'id': str(uuid.uuid4()),
            'title': row[1],
            'description': row[2],
            'priority': row[3].value if hasattr(row[3], 'value') else str(row[3]),
            'status': row[4].value if hasattr(row[4], 'value') else str(row[4]),
            'start_time': row[5],  # due_date becomes start_time
            'end_time': None,
            'order': row[6]
        })
    
    # Drop new table and rename old table
    op.drop_table('task')
    op.rename_table('task_old', 'task')
    
    # Drop the enum types
    op.execute('DROP TYPE IF EXISTS taskpriority')
    op.execute('DROP TYPE IF EXISTS taskstatus')