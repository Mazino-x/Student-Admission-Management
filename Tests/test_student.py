def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_create_student_success(client):
    payload = {
        "name": "Kunal",
        "email": "kunal@example.com",
        "phone": "9876543210",
        "course": "B.tech",
        "year": 4,
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Kunal"
    assert data["email"] == "kunal@example.com"
    assert data["phone"] == "9876543210"
    assert data["course"] == "B.tech"
    assert data["year"] == 4


def test_create_student_duplicate_email(client):
    payload = {
        "name": "Kunal",
        "email": "kunal@example.com",
        "phone": "9876543210",
        "course": "B.tech",
        "year": 4,
    }
    client.post("/students", json=payload)

    # Attempt to create another student with same email
    payload_dup = {
        "name": "Student Two",
        "email": "kunal@example.com",
        "phone": "9123456780",
        "course": "B.tech",
        "year": 4,
    }
    response = client.post("/students", json=payload_dup)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_create_student_invalid_phone(client):
    payload = {
        "name": "Test Student",
        "email": "test@example.com",
        "phone": "12345",  # Less than 10 digits
        "course": "B.tech",
        "year": 4,
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_create_student_invalid_year(client):
    payload = {
        "name": "Test Student",
        "email": "test2@example.com",
        "phone": "9876543210",
        "course": "B.tech",
        "year": 5,  # Out of range 1-4
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_list_students_and_filter(client):
    s1 = {
        "name": "Aroic",
        "email": "aroic@example.com",
        "phone": "1111111111",
        "course": "Computer Science",
        "year": 1,
    }
    s2 = {
        "name": "Xenon",
        "email": "xenon@example.com",
        "phone": "2222222222",
        "course": "Mechanical Engineering",
        "year": 2,
    }
    client.post("/students", json=s1)
    client.post("/students", json=s2)

    # List all
    response = client.get("/students")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Filter by year
    response_year = client.get("/students?year=1")
    assert response_year.status_code == 200
    assert len(response_year.json()) == 1
    assert response_year.json()[0]["name"] == "Aroic"

    # Filter by course/department
    response_dept = client.get("/students?course=mechanical engineering")
    assert response_dept.status_code == 200
    assert len(response_dept.json()) == 1
    assert response_dept.json()[0]["name"] == "Xenon"


def test_student_statistics(client):
    s1 = {
        "name": "Aroic",
        "email": "aroic@example.com",
        "phone": "1111111111",
        "course": "Computer Science",
        "year": 1,
    }
    s2 = {
        "name": "Xenon",
        "email": "xenon@example.com",
        "phone": "2222222222",
        "course": "Computer Science",
        "year": 3,
    }
    client.post("/students", json=s1)
    client.post("/students", json=s2)

    response = client.get("/students/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_students"] == 2
    assert stats["by_year"]["1"] == 1
    assert stats["by_year"]["3"] == 1
    assert stats["year_distribution"]["1"] == 1
    assert stats["by_department"]["Computer Science"] == 2


def test_get_student_by_id(client):
    payload = {
        "name": "Neon",
        "email": "neon@example.com",
        "phone": "3333333333",
        "course": "Civil",
        "year": 4,
    }
    created = client.post("/students", json=payload).json()
    student_id = created["id"]

    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Neon"

    # Non-existent ID
    response_404 = client.get("/students/9999")
    assert response_404.status_code == 404
    assert response_404.json()["detail"] == "Student not found"


def test_update_student(client):
    payload = {
        "name": "Siddharth",
        "email": "siddharth@example.com",
        "phone": "9876543210",
        "course": "BCA",
        "year": 3,
    }
    created = client.post("/students", json=payload).json()
    student_id = created["id"]

    update_payload = {
        "name": "Siddharth Srivastava",
        "email": "siddharth@example.com",
        "phone": "9876543210",
        "course": "BCA",
        "year": 4,
    }
    response = client.put(f"/students/{student_id}", json=update_payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Siddharth Srivastava"
    assert updated["year"] == 4
    assert updated["email"] == "siddharth@example.com"


def test_delete_student(client):
    payload = {
        "name": "Neon",
        "email": "neon@example.com",
        "phone": "9516559986",
        "course": "Math",
        "year": 1,
    }
    created = client.post("/students", json=payload).json()
    student_id = created["id"]

    response = client.delete(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Student deleted successfully"

    # Verify deleted
    get_res = client.get(f"/students/{student_id}")
    assert get_res.status_code == 404