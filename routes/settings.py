from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.models import User, Department, AssetCategory
from database.database import db

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
def settings():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    departments = Department.query.all()
    categories = AssetCategory.query.all()
    users = User.query.all()
    
    return render_template('settings.html',
        user=user,
        departments=departments,
        categories=categories,
        users=users
    )

@settings_bp.route('/department/add', methods=['POST'])
def add_department():
    if 'user_id' not in session:
        return redirect('/login')
    
    name = request.form.get('name', '').strip()
    if name:
        dept = Department(name=name)
        db.session.add(dept)
        db.session.commit()
        flash(f'Department "{name}" added!', 'success')
    
    return redirect(url_for('settings.settings'))

@settings_bp.route('/department/delete/<int:dept_id>', methods=['POST'])
def delete_department(dept_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    dept = Department.query.get_or_404(dept_id)
    db.session.delete(dept)
    db.session.commit()
    return jsonify({'success': True})

@settings_bp.route('/category/add', methods=['POST'])
def add_category():
    if 'user_id' not in session:
        return redirect('/login')
    
    name = request.form.get('name', '').strip()
    if name:
        cat = AssetCategory(name=name)
        db.session.add(cat)
        db.session.commit()
        flash(f'Category "{name}" added!', 'success')
    
    return redirect(url_for('settings.settings'))

@settings_bp.route('/category/delete/<int:cat_id>', methods=['POST'])
def delete_category(cat_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    cat = AssetCategory.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'success': True})