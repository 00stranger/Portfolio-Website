from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/uni_management'
app.app_context().push()
db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer)  # make foreign key
    subject_code = db.Column(db.String(20))  # make foreign key
    title = db.Column(db.String(20))
    description = db.Column(db.String(100))
    due_date = db.Column(db.DateTime())

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, user, subject_code, title, description, due_date):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.user = user
        self.subject_code = subject_code

    def __repr__(self):
        return f"{self.id}"


db.create_all()


class TodoSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Todo
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    user = fields.Number(required=True)
    subject_code = fields.String(required=True)
    title = fields.String(required=True)
    description = fields.String(required=True)
    due_date = fields.DateTime(required=True)


@app.route('/assignments/')
def home():
    return render_template('calendar_events.html')


@app.route('/calendar-events')
def calendar_events():
    get_todos = Todo.query.all()
    todo_schema = TodoSchema(many=True)
    todos = todo_schema.dump(get_todos)
    responses = []
    for todo in todos:
        response = {}
        date_time = todo["due_date"]
        date_time = datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S')
        # get timestamp
        timestamp = date_time.timestamp()*1000
        response["id"] = int(todo["id"])
        response["title"] = todo["title"]
        response["start"] = int(timestamp)
        response["end"] = int(timestamp)
        response["class"] = "event-important"
        response["description"] = todo["description"]
        response["url"] = f"/event_detail/{int(todo['id'])}/"
        responses.append(response)
    resp = jsonify({'success': 1, 'result': responses})
    resp.status_code = 200
    return resp


@app.route('/event_detail/<id>/')
def event_detail(id):
    assignment = Todo.query.get(id)
    return render_template("event_detail.html", assignment=assignment)


if __name__ == "__main__":
    app.run(debug=True)
