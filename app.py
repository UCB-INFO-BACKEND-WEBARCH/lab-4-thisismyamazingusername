"""
Week 4
Complete TODO 1-5 in order.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TodoModel(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "category_id": self.category_id
        }

next_id = 4


class CategoryModel(db.Model):
    __tablename__ = "categories"
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False)
    todos = db.relationship('TodoModel', backref='category', lazy=True)

    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            "todo_count": len(self.todos),
        }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/api/todos', methods=['GET'])
def get_todos():
    query = TodoModel.query
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    priority = request.args.get('priority')
    if priority:
        query = query.filter_by(priority=priority)

    category_id = request.args.get('category_id')
    if category_id:
        query = query.filter_by(category_id=int(category_id))

    return jsonify([todo.to_dict() for todo in query])


@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = TodoModel.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())


@app.route('/api/todos', methods=['POST'])
def create_todo():
    global next_id
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400

    todo = TodoModel(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        category_id=data.get('category_id')
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201



@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = TodoModel.query.get_or_404(todo_id)
    if not todo:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    for field in ['title', 'description', 'status', 'priority', 'category_id']:
        if field in data:
            setattr(todo, field, data[field])

    db.session.commit()
    return jsonify(todo.to_dict())


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = TodoModel.query.get_or_404(todo_id)
    if not todo:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Todo deleted"})


@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify([c.to_dict() for c in CategoryModel.query.all()])

@app.route('/api/categories/<int:cat_id>', methods=['GET'])
def get_category(cat_id):
    cat = db.get_or_404(CategoryModel, cat_id)
    return jsonify(cat.to_dict())

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    cat = CategoryModel(name=data['name'])
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
