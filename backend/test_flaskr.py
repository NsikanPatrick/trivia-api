import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.DB_HOST = os.getenv('HOST')
        self.DB_USER = os.getenv('DATABASE_USER')
        self.DB_PASSWORD = os.getenv('DATABASE_PASS')
        self.DB_NAME = os.getenv('DATABASE_NAME')
        self.database_path = "postgres://{}:{}@{}/{}".format(
            self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question":"Who are you",
             "answer":"A programmer", 
             "category":"3", 
             "difficulty":"1"
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    # This section executes tests for all the question related queries.....................
    def test_get_paginated_list_of_questions(self):
        response = self.client().get('/questions')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(res_data['success'], True)
        self.assertTrue(res_data['questions'])
        self.assertTrue(res_data['total_questions'])
        # self.assertFalse(res_data['current_category'])
        # self.assertTrue(res_data['total_categories'])

    def test_request_questions_beyond_available_pages(self):
        response = self.client().get('/questions?page=1500')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Bad request, resource not available.")

    def test_delete_question(self):
        response = self.client().delete('/questions/5')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_none_existent_question(self):
        response = self.client().delete('/questions/1500')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable request')

    def test_create_question(self):
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search_questions(self):
        search_term = {
            "search": "Who"
            }
        response = self.client().post('/questions/search', json=search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_invalid_search_request(self):
        search_term = {
            'searchTerm': 'testing testing testing',
        }
        response = self.client().post('/search', json=search_term)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


    # This section executes tests for all the category related queries.....................

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_question_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_get_question_beyond_available_categories(self):
        response = self.client().get('/categories/200/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    
    # This section executes tests for the quiz related queries.....................

    def test_load_quiz_question(self):
        new_quiz = {
            'previous_questions': [],
            'quiz_category': {
            'type': 'Art',
            'id': 2
            }
        }

        response = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_invalid_quiz(self):
        new_quiz = {
            'previous_questions': [4],
            'quiz_category': {
                'type': 'CTY',
                'id': 'WYU'
            }
        }
        response = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()