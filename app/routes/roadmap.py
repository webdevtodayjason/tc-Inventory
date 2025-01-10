from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.inventory import RoadmapItem, roadmap_votes
from app.utils.activity_logger import log_activity
from sqlalchemy import func, desc

bp = Blueprint('roadmap', __name__)

@bp.route('/roadmap')
@login_required
def roadmap():
    # Create a subquery to count votes
    vote_count = db.session.query(
        roadmap_votes.c.item_id,
        func.count(roadmap_votes.c.user_id).label('vote_count')
    ).group_by(roadmap_votes.c.item_id).subquery()

    # Query items with vote count
    items = db.session.query(RoadmapItem)\
        .outerjoin(vote_count, RoadmapItem.id == vote_count.c.item_id)\
        .order_by(
            RoadmapItem.status.asc(),
            desc(func.coalesce(vote_count.c.vote_count, 0)),
            RoadmapItem.created_at.desc()
        ).all()
    
    return render_template('roadmap.html', items=items)

@bp.route('/roadmap/submit', methods=['POST'])
@login_required
def submit_request():
    try:
        print("Received roadmap submit request")
        data = request.get_json()
        print("Request data:", data)
        
        if not data:
            print("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['title', 'description', 'category']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print("Missing fields:", missing_fields)
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Validate data
        if not data['title'].strip():
            return jsonify({'error': 'Title cannot be empty'}), 400
        if not data['description'].strip():
            return jsonify({'error': 'Description cannot be empty'}), 400
        if data['category'] not in ['Feature Request', 'Bug Report', 'Integration']:
            return jsonify({'error': 'Invalid category'}), 400
            
        item = RoadmapItem(
            title=data['title'].strip(),
            description=data['description'].strip(),
            category=data['category'],
            submitter_id=current_user.id
        )
        print("Created RoadmapItem:", item)
        
        try:
            db.session.add(item)
            db.session.commit()
            print("Item saved to database")
        except Exception as db_error:
            print("Database error:", str(db_error))
            db.session.rollback()
            return jsonify({'error': 'Database error: ' + str(db_error)}), 400
        
        try:
            log_activity('add', 'roadmap_item', item.id, {
                'title': item.title,
                'category': item.category
            })
            print("Activity logged")
        except Exception as log_error:
            print("Logging error:", str(log_error))
            # Don't return error here, as the item was already saved
        
        return jsonify(item.to_dict(current_user)), 201
    except Exception as e:
        print("Unexpected error:", str(e))
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/roadmap/vote/<int:item_id>', methods=['POST'])
@login_required
def vote(item_id):
    try:
        item = RoadmapItem.query.get_or_404(item_id)
        
        # Check if item is completed
        if item.status == 'done':
            return jsonify({'error': 'Cannot vote on completed items'}), 400
            
        # Check if user has already voted
        if item.has_user_voted(current_user):
            return jsonify({'error': 'You have already voted on this item'}), 400
            
        # Add the vote
        item.voters.append(current_user)
        db.session.commit()
        
        # Log the activity
        log_activity('vote', 'roadmap_item', item.id, {
            'title': item.title,
            'votes': item.votes
        })
        
        return jsonify({
            'votes': item.votes,
            'has_voted': True
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/admin/roadmap/update-status', methods=['POST'])
@login_required
def update_status():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        print("Received status update request")
        data = request.get_json()
        print("Request data:", data)
        
        if not data:
            print("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
            
        if 'item_id' not in data or 'status' not in data:
            print("Missing required fields")
            return jsonify({'error': 'Missing required fields: item_id and status'}), 400
            
        if data['status'] not in ['open', 'in_progress', 'done']:
            print("Invalid status:", data['status'])
            return jsonify({'error': 'Invalid status value'}), 400
            
        item = RoadmapItem.query.get_or_404(data['item_id'])
        old_status = item.status
        item.status = data['status']
        
        try:
            db.session.commit()
            print(f"Status updated: {old_status} -> {item.status}")
            
            log_activity('update', 'roadmap_item', item.id, {
                'title': item.title,
                'old_status': old_status,
                'new_status': item.status
            })
            print("Activity logged")
            
            return jsonify({
                'status': 'success',
                'item': item.to_dict(current_user)
            })
        except Exception as db_error:
            print("Database error:", str(db_error))
            db.session.rollback()
            return jsonify({'error': 'Database error: ' + str(db_error)}), 400
            
    except Exception as e:
        print("Unexpected error:", str(e))
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 400 