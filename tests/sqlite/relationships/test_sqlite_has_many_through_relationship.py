import unittest

from src.masoniteorm.collection import Collection
from src.masoniteorm.models import Model
from src.masoniteorm.relationships import has_many_through
from tests.integrations.config.database import DATABASES
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform


class Enrolment(Model):
    __table__ = "enrolment"
    __connection__ = "dev"
    __fillable__ = ["active_student_id", "in_course_id"]


class Student(Model):
    __table__ = "student"
    __connection__ = "dev"
    __fillable__ = ["student_id", "name"]


class Course(Model):
    __table__ = "course"
    __connection__ = "dev"
    __fillable__ = ["course_id", "name"]

    @has_many_through(
        None,
        "in_course_id",
        "active_student_id",
        "course_id",
        "student_id"
    )
    def students(self):
        return [Student, Enrolment]


class TestHasManyThroughRelationship(unittest.TestCase):
    def setUp(self):
        self.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        with self.schema.create_table_if_not_exists("student") as table:
            table.integer("student_id").primary()
            table.string("name")

        with self.schema.create_table_if_not_exists("course") as table:
            table.integer("course_id").primary()
            table.string("name")

        with self.schema.create_table_if_not_exists("enrolment") as table:
            table.integer("enrolment_id").primary()
            table.integer("active_student_id")
            table.integer("in_course_id")

        if not Course.count():
            Course.builder.new().bulk_create(
                [
                    {"course_id": 10, "name": "Math 101"},
                    {"course_id": 20, "name": "History 101"},
                    {"course_id": 30, "name": "Math 302"},
                    {"course_id": 40, "name": "Biology 302"},
                ]
            )

        if not Student.count():
            Student.builder.new().bulk_create(
                [
                    {"student_id": 100, "name": "Bob"},
                    {"student_id": 200, "name": "Alice"},
                    {"student_id": 300, "name": "Steve"},
                    {"student_id": 400, "name": "Megan"},
                ]
            )

        if not Enrolment.count():
            Enrolment.builder.new().bulk_create(
                [
                    {"active_student_id": 100, "in_course_id": 30},
                    {"active_student_id": 200, "in_course_id": 10},
                    {"active_student_id": 100, "in_course_id": 10},
                    {"active_student_id": 400, "in_course_id": 20},
                ]
            )

    def test_has_many_through_can_eager_load(self):
        courses = Course.where("name", "Math 101").with_("students").get()
        students = courses.first().students

        self.assertIsInstance(students, Collection)
        self.assertEqual(students.count(), 2)

        student1 = students.shift()
        self.assertIsInstance(student1, Student)
        self.assertEqual(student1.name, "Alice")

        student2 = students.shift()
        self.assertIsInstance(student2, Student)
        self.assertEqual(student2.name, "Bob")

        # check .first() and .get() produce the same result
        single = (
            Course.where("name", "History 101")
            .with_("students")
            .first()
        )
        self.assertIsInstance(single.students, Collection)

        single_get = (
            Course.where("name", "History 101").with_("students").get()
        )

        print(single.students)
        print(single_get.first().students)
        self.assertEqual(single.students.count(), 1)
        self.assertEqual(single_get.first().students.count(), 1)

        single_name = single.students.first().name
        single_get_name = single_get.first().students.first().name
        self.assertEqual(single_name, single_get_name)

    def test_has_many_through_eager_load_can_be_empty(self):
        courses = (
            Course.where("name", "Biology 302")
            .with_("students")
            .get()
        )
        self.assertIsNone(courses.first().students)

    def test_has_many_through_can_get_related(self):
        course = Course.where("name", "Math 101").first()
        self.assertIsInstance(course.students, Collection)
        self.assertIsInstance(course.students.first(), Student)
        self.assertEqual(course.students.count(), 2)

    def test_has_many_through_has_query(self):
        courses = Course.where_has(
            "students", lambda query: query.where("name", "Bob")
        )
        self.assertEqual(courses.count(), 2)
