import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    all_questions = [question.format() for question in selection]
    current_questions_page = all_questions[start:end]
    return current_questions_page

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    
    cors = CORS(app, resources={'/': {'origins': '*'}})


    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response


    """
    @TODO:
    Create an endpoint to handle GET requests for all available categories.
    """
    
    @app.route("/categories")
    def get_all_categories():
        # Fetching all categories from the database
        categories = Category.query.all()

        # Creating a dictionary to hold all fetched categories
        cat_dictionary = {}

        # Adding categories to dictionary
        for category in categories:
            cat_dictionary[category.id] = category.type

        # Abort the request if no categories were fetched
        if (len(cat_dictionary) == 0):
            abort(404)

        # Return the result of the categories api
        return jsonify({
            'success': True,
            'categories': cat_dictionary
        })



    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions')
    def get_questions():
        try:
            # get all questions from the database
            questions = Question.query.order_by(Question.id).all()
            # get the total num of questions
            total_questions = len(questions)
            # get current questions in a page (10q)
            current_questions = paginate_questions(request, questions)

            # get all categories
            all_categories = Category.query.all()
            cat_dictionary = {}

            # if the page number is not found
            if (len(current_questions) == 0):
                abort(404)

            # Storing categories in a dictionary
            for category in all_categories:
                cat_dictionary[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions,
                'categories': cat_dictionary
            })

        except:
            abort(400)


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:q_id>', methods=['DELETE'])
    def delete_question(q_id):
        try:
            # Get the particular question to delete
            question_to_delete = Question.query.get(q_id)

            # Abort request if the question is not found
            if question_to_delete is None:
                abort(404)

            question_to_delete.delete()
            # Update the current available questions in  the front end
            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,

                'deleted':q_id,
                'questions': current_questions,
                'total_questions': len(questions)
            })

        except Exception as e:
            print(e)
            abort(400)



    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=['POST'])
    def add_question():
        # Get client's data to post to the db
        n_question = request.json['question']
        n_answer = request.json['answer']
        n_category = request.json['category']
        n_difficulty = request.json['difficulty']

        try:
            # Posting new data to db
            new_question = Question(question=n_question, answer=n_answer,
                                category=n_category, difficulty=n_difficulty)
            new_question.insert()

            # Updating the frontend with new set of questions
            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'created': new_question.id,
                'questions': current_questions,
                'total_questions': len(questions)
            })

        except:
            abort(422)



    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    
    @app.route("/search", methods=['POST'])
    def search():
        search_term = request.json['searchTerm']
        questions = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()

        if questions:
            current_questions = paginate_questions(request, questions)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions)
            })
        else:
            abort(404)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    
    @app.route("/categories/<int:id>/questions")
    def questions_in_category(id):
        # retrive the category by given id
        category_to_fetch = Category.query.filter_by(id=id).one_or_none()

        if category_to_fetch:
            # retrive all questions in a category
            questions_in_category = Question.query.filter_by(category=str(id)).all()
            current_questions = paginate_questions(request, questions_in_category)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions_in_category),
                'current_category': category_to_fetch.type
            })
        # if category not founs
        else:
            abort(404)


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def quiz():
        # get the qestion category an the previous question
        quiz_category = request.json['quiz_category']
        previous_question = request.json['previous_questions']

        try:
            if (quiz_category['id'] == 0):
                all_questions = Question.query.all()
            else:
                all_questions = Question.query.filter_by(
                    category=quiz_category['id']).all()

            randomized_index = random.randint(0, len(all_questions)-1)
            next_question = all_questions[randomized_index]

            while next_question.id not in previous_question:
                next_question = all_questions[randomized_index]
                return jsonify({
                    'success': True,
                    'question': {
                        "id": next_question.id,
                        "question": next_question.question,
                        "answer": next_question.answer,
                        "category": next_question.category,
                        "difficulty": next_question.difficulty 
                    },
                    'previousQuestion': previous_question
                })

        except Exception as e:
            print(e)
            abort(400)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Invalid method!"
        }), 405

    @app.errorhandler(422)
    def unprocessable_resource(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable resource"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500


    return app 














