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

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    '''
  @TODO: Set up CORS. Allow '*' for origins.
  Delete the sample route after
  completing the TODOs
  '''

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response
    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def retrieve_categories():
        categories = Category.query.all()
        category_list = [category.format() for category in categories]
        cdict = {}
        for i, j in enumerate(category_list):
            cdict[i + 1] = j['type']
        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': cdict
        })

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination
  at the bottom of the screen for three pages.
  Clicking on the page numbers should
  update the questions.
  '''

    @app.route('/questions', methods=['GET', 'POST'])
    def questions():
        if(request.get_json()):
            body = request.get_json()
            if 'difficulty' in body:

                new_question = body.get('question', None)
                new_answer = body.get('answer', None)
                new_difficulty = body.get('difficulty', None)
                new_category = body.get('category', None)
                print(new_question, new_answer,
                      new_difficulty, new_category)
                if (new_question is None or new_answer is None):
                    abort(404)

                try:
                    question = Question(
                        question=new_question,
                        answer=new_answer,
                        difficulty=new_difficulty,
                        category=new_category)
                    question.insert()

                    return jsonify({
                        'success': True,
                        'created': question.id
                    })

                except BaseException:
                    abort(422)
            else:
                question = Question.query.order_by(
                    Question.id).filter(
                    Question.question.ilike(
                        '%{}%'.format(
                            body['searchTerm'])))
                current_questions = paginate_questions(request, question)
                categories = retrieve_categories()
                if len(current_questions) == 0:
                    abort(404)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all()),
                    'current_category': None,
                    'categories': categories.json['categories']


                })
        else:
            question = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, question)
            categories = retrieve_categories()
            if len(current_questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'current_category': None,
                'categories': categories.json['categories']


            })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        question = Question.query.filter(
            Question.category == category_id).order_by(
            Question.id).all()
        current_questions = paginate_questions(request, question)
        categories = retrieve_categories()
        if len(current_questions) == 0:
            abort(400)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(question),
            'current_category': category_id,
            'categories': categories.json['categories']


        })

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash
  icon next to a question,
  the question will be removed.
  This removal will persist in the
  database and when you refresh the page.
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except BaseException:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        selcat = body['quiz_category']['id']
        previous = body['previous_questions']
        if selcat == 0:
            question = Question.query.order_by(
                Question.id).filter(~Question.id.in_(previous)).all()
        else:
            selcat = int(selcat)
            question = Question.query.filter(
                Question.category == selcat).order_by(
                Question.id).filter(~Question.id.in_(previous)).all()
        try:
            r = random.randint(0, len(question))
            q = question[r].format()
            return jsonify({
                'success': True,
                'previous_questions': previous,
                'quiz_category': selcat,
                'question': q
            })
        except BaseException:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

    return app
