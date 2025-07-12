# app.py - Main Flask Application
from flask_mail import Mail, Message
import random
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stackit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'debtanuroy82@gmail.com'  # replace
app.config['MAIL_PASSWORD'] = 'uijy gfzf qycj nuon'     # use app password

mail = Mail(app)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('Question', backref='author', lazy=True)
    answers = db.relationship('Answer', backref='author', lazy=True)
    votes = db.relationship('Vote', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=True)
    
    answers = db.relationship('Answer', backref='question', lazy=True, 
                            foreign_keys='Answer.question_id')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vote_score = db.Column(db.Integer, default=0)
    
    votes = db.relationship('Vote', backref='answer', lazy=True)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    filter_type = request.args.get('filter', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    base_query = Question.query

    if filter_type == 'unanswered':
        questions = base_query.all()
        unanswered = [q for q in questions if len(q.answers) == 0]
        total = len(unanswered)
        paginated_questions = unanswered[(page - 1) * per_page: page * per_page]
    elif filter_type == 'popular':
        questions = base_query.all()
        sorted_questions = sorted(questions, key=lambda q: sum(a.vote_score for a in q.answers), reverse=True)
        total = len(sorted_questions)
        paginated_questions = sorted_questions[(page - 1) * per_page: page * per_page]
    else:  # newest
        pagination = base_query.order_by(Question.created_at.desc()).paginate(page=page, per_page=per_page)
        paginated_questions = pagination.items
        total = pagination.total

    return render_template(
        'index.html',
        questions=paginated_questions,
        filter_type=filter_type,
        page=page,
        per_page=per_page,
        total=total
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check duplicates
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        session['reg_otp'] = otp
        session['reg_data'] = {
            'username': username,
            'email': email,
            'password': password
        }

        # Send email
        msg = Message('Your OTP for StackIt Registration', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f'Your OTP is {otp}. It is valid for 5 minutes.'
        mail.send(msg)

        flash('OTP sent to your email.')
        return redirect(url_for('verify_otp'))

    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp == session.get('reg_otp'):
            data = session.get('reg_data')
            if not data:
                flash('Session expired. Please register again.')
                return redirect(url_for('register'))

            user = User(
                username=data['username'],
                email=data['email'],
                password_hash=generate_password_hash(data['password'])
            )
            db.session.add(user)
            db.session.commit()

            # Clear session data
            session.pop('reg_otp', None)
            session.pop('reg_data', None)

            flash('Registration successful!')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')

    return render_template('verify_otp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/ask', methods=['GET', 'POST'])
@login_required
def ask_question():
    """Ask a new question"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        
        question = Question(
            title=title,
            description=description,
            tags=tags,
            user_id=current_user.id
        )
        db.session.add(question)
        db.session.commit()
        
        flash('Question posted successfully!')
        return redirect(url_for('view_question', question_id=question.id))
    
    return render_template('ask_question.html')

@app.route('/question/<int:question_id>')
def view_question(question_id):
    """View a specific question and its answers"""
    question = Question.query.get_or_404(question_id)
    answers = Answer.query.filter_by(question_id=question_id).order_by(Answer.vote_score.desc()).all()
    return render_template('question_detail.html', question=question, answers=answers)

@app.route('/answer/<int:question_id>', methods=['POST'])
@login_required
def post_answer(question_id):
    """Post an answer to a question"""
    content = request.form['content']

    answer = Answer(
        content=content,
        question_id=question_id,
        user_id=current_user.id
    )
    db.session.add(answer)

    # Fetch question
    question = Question.query.get(question_id)

    # Notify question owner
    if question.user_id != current_user.id:
        db.session.add(Notification(
            user_id=question.user_id,
            message=f'{current_user.username} answered your question: {question.title[:50]}...'
        ))

    # Notify mentioned users
    import re
    mentions = re.findall(r'@(\w+)', content)
    for username in mentions:
        mentioned_user = User.query.filter_by(username=username).first()
        if mentioned_user and mentioned_user.id != current_user.id:
            db.session.add(Notification(
                user_id=mentioned_user.id,
                message=f'{current_user.username} mentioned you in an answer.'
            ))

    db.session.commit()

    flash('Answer posted successfully!')
    return redirect(url_for('view_question', question_id=question_id))


@app.route('/vote/<int:answer_id>/<vote_type>', methods=['POST'])
@login_required
def vote_answer(answer_id, vote_type):
    """Vote on an answer"""
    if vote_type not in ['upvote', 'downvote']:
        return jsonify({'error': 'Invalid vote type'}), 400
    
    existing_vote = Vote.query.filter_by(user_id=current_user.id, answer_id=answer_id).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            db.session.delete(existing_vote)
        else:
            existing_vote.vote_type = vote_type
    else:
        vote = Vote(
            user_id=current_user.id,
            answer_id=answer_id,
            vote_type=vote_type
        )
        db.session.add(vote)
    
    # Update answer vote score
    answer = Answer.query.get(answer_id)
    upvotes = Vote.query.filter_by(answer_id=answer_id, vote_type='upvote').count()
    downvotes = Vote.query.filter_by(answer_id=answer_id, vote_type='downvote').count()
    answer.vote_score = upvotes - downvotes
    
    db.session.commit()
    
    return jsonify({'vote_score': answer.vote_score})

@app.route('/accept/<int:answer_id>', methods=['POST'])
@login_required
def accept_answer(answer_id):
    """Accept an answer as the solution"""
    answer = Answer.query.get_or_404(answer_id)
    question = answer.question
    
    if question.user_id != current_user.id:
        return jsonify({'error': 'Only question author can accept answers'}), 403
    
    question.accepted_answer_id = answer_id
    db.session.commit()
    
    # Create notification for answer author
    if answer.user_id != current_user.id:
        notification = Notification(
            user_id=answer.user_id,
            message=f'Your answer to "{question.title[:50]}..." was accepted!'
        )
        db.session.add(notification)
        db.session.commit()
    
    return jsonify({'success': True})

@app.route('/search')
def search():
    """Search questions by tags or title"""
    query = request.args.get('q', '')
    if query:
        questions = Question.query.filter(
            (Question.title.contains(query)) | 
            (Question.tags.contains(query))
        ).all()
    else:
        questions = []
    
    return render_template('search_results.html', questions=questions, query=query)

@app.route('/notifications')
@login_required
def notifications():
    """View user notifications"""
    notifications = Notification.query.filter_by(user_id=current_user.id)\
                                    .order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/api/notification_count')
@login_required
def notification_count():
    """Get unread notification count"""
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not current_user.is_admin:
        flash('Admin access required')
        return redirect(url_for('index'))
    
    questions = Question.query.order_by(Question.created_at.desc()).all()
    users = User.query.all()
    
    return render_template('admin_dashboard.html', questions=questions, users=users)

@app.route('/admin/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    """Delete a question (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    question = Question.query.get_or_404(question_id)
    
    # Delete related answers and votes
    for answer in question.answers:
        Vote.query.filter_by(answer_id=answer.id).delete()
        db.session.delete(answer)
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/api/notifications')
@login_required
def api_notifications():
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).all()
    recent = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()

    # Mark all as read (optional: disable if you want per-click control)
    for note in unread:
        note.is_read = True
    db.session.commit()

    return jsonify({
        "unread_count": len(unread),
        "notifications": [
            {"message": n.message, "created_at": n.created_at.strftime('%Y-%m-%d %H:%M')}
            for n in recent
        ]
    })

# Template filters
@app.template_filter('truncate')
def truncate_filter(text, length=100):
    """Truncate text to specified length"""
    if len(text) <= length:
        return text
    return text[:length] + '...'

@app.template_filter('tag_list')
def tag_list_filter(tags):
    """Convert comma-separated tags to list"""
    return [tag.strip() for tag in tags.split(',') if tag.strip()]

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@stackit.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")
    
    app.run(debug=True)
