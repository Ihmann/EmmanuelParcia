from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# In-memory storage for students
students = [
    {"id": 1, "name": "Alice", "grade": 10, "section": "Zechariah"},
    {"id": 2, "name": "Bob", "grade": 11, "section": "Daniel"}
]

@app.route('/')
def home():
    return "Welcome to my enhanced Flask API!"

# Get all students or filter by grade/section
@app.route('/students', methods=['GET'])
def get_students():
    grade = request.args.get('grade')
    section = request.args.get('section')
    results = students

    if grade:
        results = [s for s in results if str(s['grade']) == grade]
    if section:
        results = [s for s in results if s['section'].lower() == section.lower()]

    return jsonify(results)

# Get a single student by ID
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = next((s for s in students if s['id'] == student_id), None)
    if student:
        return jsonify(student)
    else:
        return jsonify({"error": "Student not found"}), 404

# Add a new student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    if not data or not all(k in data for k in ("name", "grade", "section")):
        return jsonify({"error": "Missing fields"}), 400

    new_id = max([s["id"] for s in students], default=0) + 1
    new_student = {
        "id": new_id,
        "name": data["name"],
        "grade": data["grade"],
        "section": data["section"]
    }
    students.append(new_student)
    return jsonify(new_student), 201

# Update a student
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = next((s for s in students if s['id'] == student_id), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()
    student.update({k: data[k] for k in data if k in student})
    return jsonify(student)

# Delete a student
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    global students
    students = [s for s in students if s["id"] != student_id]
    return jsonify({"message": "Student deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
