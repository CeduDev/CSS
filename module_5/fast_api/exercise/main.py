from fastapi import FastAPI
from mongoengine import (
    connect,
    disconnect,
    Document,
    StringField,
    ReferenceField,
    ListField,
    IntField,
)
import json
from pydantic import BaseModel

app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    connect("fast-api-database", host="mongo", port=27017)


@app.on_event("shutdown")
def shutdown_db_client():
    disconnect("fast-api-database")


# Helper functions to convert MongeEngine documents to json
def course_to_json(course):
    course = json.loads(course.to_json())
    course["students"] = list(map(lambda dbref: str(dbref["$oid"]), course["students"]))
    course["id"] = str(course["_id"]["$oid"])
    course.pop("_id")
    return course


def student_to_json(student):
    student = json.loads(student.to_json())
    student["id"] = str(student["_id"]["$oid"])
    student.pop("_id")
    return student


# Schema
class Student(Document):
    name = StringField(required=True)
    student_number = IntField()


class Course(Document):
    name = StringField(required=True)
    description = StringField()
    tags = ListField(StringField())
    students = ListField(ReferenceField("Student", reverse_delete_rule=4))


# Input Validators
class CourseData(BaseModel):
    name: str
    description: str | None
    tags: list[str] | None
    students: list[str] | None


class StudentData(BaseModel):
    name: str
    student_number: int | None


# Student routes
# Complete the Student routes similarly as per the instructions provided in A+
@app.post("/students", status_code=201)
async def create_student(student: StudentData):
    new_student = Student(**student.dict()).save()
    result = student_to_json(new_student)
    return {"message": "Student successfully created", "id": result["id"]}


@app.get("/students/{student_id}", status_code=200)
async def read_student(student_id: str):
    return student_to_json(Student.objects.get(id=student_id))


@app.put("/students/{student_id}", status_code=200)
async def update_student(student_id: str, student: StudentData):
    Student.objects.get(id=student_id).update(**student.dict())
    return {"message": "Student successfully updated"}


@app.delete("/students/{student_id}", status_code=200)
async def delete_student(student_id: str):
    Student.objects.get(id=student_id).delete()
    return {"message": "Student successfully deleted"}


# Course routes
@app.post("/courses", status_code=201)
async def create_course(course: CourseData):
    new_course = Course(**course.dict()).save()
    result = course_to_json(new_course)
    return {"message": "Course successfully created", "id": result["id"]}


@app.get("/courses", status_code=200)
async def read_courses(tag: str | None = None, studentName: str | None = None):
    query = Course.objects()
    if tag is not None:
        query = query.filter(tags=tag)
    if studentName is not None:
        student = Student.objects(name=studentName).first()
        query = query.filter(students=student)
    result = []
    for i in query:
        result.append(course_to_json(i))
    return result


@app.get("/courses/{course_id}", status_code=200)
async def read_course(course_id: str):
    return course_to_json(Course.objects.get(id=course_id))


@app.put("/courses/{course_id}", status_code=200)
async def update_course(course_id: str, course: CourseData):
    Course.objects.get(id=course_id).update(**course.dict())
    return {"message": "Course successfully updated"}


@app.delete("/courses/{course_id}", status_code=200)
async def delete_course(course_id: str):
    Course.objects.get(id=course_id).delete()
    return {"message": "Course successfully deleted"}
