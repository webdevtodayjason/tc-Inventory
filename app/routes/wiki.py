from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.inventory import WikiCategory, WikiPage
from app.forms import WikiCategoryForm, WikiPageForm
from app.routes.inventory import admin_required
from sqlalchemy import or_

bp = Blueprint('wiki', __name__)

@bp.route('/wiki')
@login_required
def wiki_home():
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    
    query = WikiPage.query
    
    if search:
        query = query.filter(
            or_(
                WikiPage.title.ilike(f'%{search}%'),
                WikiPage.content.ilike(f'%{search}%')
            )
        )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    pages = query.order_by(WikiPage.updated_at.desc()).all()
    categories = WikiCategory.query.order_by(WikiCategory.name).all()
    
    return render_template('wiki/home.html',
                         pages=pages,
                         categories=categories,
                         search=search,
                         selected_category=category_id)

@bp.route('/wiki/new', methods=['GET', 'POST'])
@login_required
def new_page():
    form = WikiPageForm()
    
    if form.validate_on_submit():
        page = WikiPage(
            title=form.title.data,
            content=form.content.data,
            category_id=form.category_id.data,
            author_id=current_user.id
        )
        db.session.add(page)
        db.session.commit()
        flash('Wiki page created successfully', 'success')
        return redirect(url_for('wiki.view_page', id=page.id))
    
    api_key = current_app.config.get('TINYMCE_API_KEY')
    current_app.logger.debug(f'TinyMCE API Key: {api_key}')
    
    if not api_key:
        flash('TinyMCE API key is not configured', 'error')
        current_app.logger.error('TinyMCE API key is missing')
    
    return render_template('wiki/edit.html', form=form, is_new=True, tinymce_api_key=api_key)

@bp.route('/wiki/category/<int:category_id>')
@login_required
def category_view(category_id):
    category = WikiCategory.query.get_or_404(category_id)
    pages = WikiPage.query.filter_by(category_id=category_id).order_by(WikiPage.updated_at.desc()).all()
    categories = WikiCategory.query.order_by(WikiCategory.name).all()
    return render_template('wiki/category.html',
                         category=category,
                         pages=pages,
                         categories=categories)

@bp.route('/wiki/<int:id>')
@login_required
def view_page(id):
    page = WikiPage.query.get_or_404(id)
    category = WikiCategory.query.get(page.category_id) if page.category_id else None
    return render_template('wiki/view.html',
                         page=page,
                         category=category)

@bp.route('/wiki/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_page(id):
    page = WikiPage.query.get_or_404(id)
    
    if not page.can_edit(current_user):
        flash('You do not have permission to edit this page', 'error')
        return redirect(url_for('wiki.view_page', id=page.id))
    
    form = WikiPageForm(obj=page)
    
    if form.validate_on_submit():
        page.title = form.title.data
        page.content = form.content.data
        page.category_id = form.category_id.data
        db.session.commit()
        flash('Wiki page updated successfully', 'success')
        return redirect(url_for('wiki.view_page', id=page.id))
    
    api_key = current_app.config.get('TINYMCE_API_KEY')
    if not api_key:
        flash('TinyMCE API key is not configured', 'error')
        current_app.logger.error('TinyMCE API key is missing')
    
    return render_template('wiki/edit.html', form=form, page=page, is_new=False, tinymce_api_key=api_key)

@bp.route('/wiki/<int:id>/delete', methods=['POST'])
@login_required
def delete_page(id):
    page = WikiPage.query.get_or_404(id)
    
    if not page.can_delete(current_user):
        flash('You do not have permission to delete this page', 'error')
        return redirect(url_for('wiki.view_page', id=page.id))
    
    db.session.delete(page)
    db.session.commit()
    flash('Wiki page deleted successfully', 'success')
    return redirect(url_for('wiki.wiki_home'))

# Wiki Category Management
@bp.route('/manage/wiki-categories')
@login_required
@admin_required
def manage_categories():
    categories = WikiCategory.query.order_by(WikiCategory.name).all()
    return render_template('wiki/manage/categories.html', categories=categories)

@bp.route('/manage/wiki-categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name')
    if not name:
        flash('Category name is required', 'error')
        return redirect(url_for('wiki.manage_categories'))
    
    if WikiCategory.query.filter_by(name=name).first():
        flash('Category already exists', 'error')
        return redirect(url_for('wiki.manage_categories'))
    
    category = WikiCategory(name=name)
    db.session.add(category)
    db.session.commit()
    flash('Category added successfully', 'success')
    return redirect(url_for('wiki.manage_categories'))

@bp.route('/manage/wiki-categories/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_category(id):
    category = WikiCategory.query.get_or_404(id)
    name = request.form.get('name')
    
    if not name:
        flash('Category name is required', 'error')
        return redirect(url_for('wiki.manage_categories'))
    
    existing = WikiCategory.query.filter_by(name=name).first()
    if existing and existing.id != id:
        flash('Category name already exists', 'error')
        return redirect(url_for('wiki.manage_categories'))
    
    category.name = name
    db.session.commit()
    flash('Category updated successfully', 'success')
    return redirect(url_for('wiki.manage_categories'))

@bp.route('/manage/wiki-categories/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    category = WikiCategory.query.get_or_404(id)
    
    if category.pages.count() > 0:
        flash('Cannot delete category that contains pages', 'error')
        return redirect(url_for('wiki.manage_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully', 'success')
    return redirect(url_for('wiki.manage_categories')) 