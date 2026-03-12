from flask import Flask, jsonify, request, abort
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)

# In-memory storage
students = [
    {"id": 1, "name": "Alice", "grade": 10, "section": "Zechariah"},
    {"id": 2, "name": "Bob", "grade": 11, "section": "Daniel"}
]

# Marshmallow schema for validation
class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    grade = fields.Int(required=True)
    section = fields.Str(required=True)

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({"error": e.messages}), 400

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the enhanced Flask API!"})

# Get all students with optional filtering and pagination
@app.route('/students', methods=['GET'])
def get_students():
    grade = request.args.get('grade')
    section = request.args.get('section')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    results = students
    if grade:
        results = [s for s in results if str(s['grade']) == str(grade)]
    if section:
        results = [s for s in results if s['section'].lower() == section.lower()]

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated = results[start:end]

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": len(results),
        "students": students_schema.dump(paginated)
    })

# Get single student
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = next((s for s in students if s['id'] == student_id), None)
    if student:
        return jsonify(student_schema.dump(student))
    return jsonify({"error": "Student not found"}), 404

# Add new student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    try:
        student_data = student_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # Check for duplicate name
    if any(s['name'].lower() == student_data['name'].lower() for s in students):
        return jsonify({"error": "Student with this name already exists"}), 400

    new_id = max([s["id"] for s in students], default=0) + 1
    student_data["id"] = new_id
    students.append(student_data)
    return jsonify(student_schema.dump(student_data)), 201

# Update student
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = next((s for s in students if s['id'] == student_id), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()
    for key in ["name", "grade", "section"]:
        if key in data:
            student[key] = data[key]
    return jsonify(student_schema.dump(student))

# Delete student
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    global students
    if not any(s["id"] == student_id for s in students):
        return jsonify({"error": "Student not found"}), 404

    students = [s for s in students if s["id"] != student_id]
    return jsonify({"message": "Student deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
