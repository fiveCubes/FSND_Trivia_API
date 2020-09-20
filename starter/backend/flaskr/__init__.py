import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  CORS(app,resources={r'/*':{'origins':'*'}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods','GET,POST,PATCH,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories')
  def categories():
    categories = Category.query.all()
    formatted_categories = {category.id:category.type for category in categories}

    return jsonify({ 
      'success':True,
       'categories':formatted_categories

    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def questions():
    page = request.args.get('page',1,type=int)
    start = (page-1)*10
    end = start + 10
    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions][start:end]

    if(len(formatted_questions)==0):
      abort(404)

    categories = Category.query.all()
    formatted_categories = {category.id:category.type for category in categories}
    return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(formatted_questions),
          'categories': formatted_categories,
          'current_category': None
      })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:del_id>', methods=['DELETE'])
  def del_question(del_id):
    question = Question.query.filter_by(id=del_id).first()
    if (question==None):
      abort(404)

    question.delete()
    return jsonify({
      'success':True,
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
     data = request.get_json()
     if('searchTerm' in data):
       search_term = data['searchTerm']
       questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
       formatted_questions = [question.format() for question in questions]
       return jsonify({
         'success':True,
         'questions':formatted_questions})
      
     else:
      try:
        question = Question(question=data['question'], answer = data['answer'] ,category=data['category'], difficulty = data['difficulty'])
        question.insert()
        return jsonify({'success':True})
      except:
        abort(400)

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

  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def category_questions(id):
    questions = Question.query.filter_by(category=id).all()
    if(len(questions)==0  ):
      abort(404)
    formatted_question = [question.format() for question in questions]
    return jsonify({ 
      'success':True,
       'questions':formatted_question,
        'total_questions':len(formatted_question),
        'current_category':id

    })
 

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

  @app.route('/quizzes', methods=['POST'])
  def create_quizzes():
     data = request.get_json()
     previous_questions = data['previous_questions']
     quiz_category = data['quiz_category']['id']
     try:
      if(quiz_category ==0):
        questions=Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).filter_by(category=quiz_category).all()
      #  .filter_by(Question.id.notin_(previous_questions))
      formatted_questions = [question.format() for question in questions]
      return jsonify({
        'previous_questions':previous_questions,
        'question':formatted_questions[0]})
     except Exception as e:
        abort(500)
           
     
  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success":False,
       "error":404,
       "message":'Resource not found'

    }),404

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success":False,
       "error":500,
       "message":"internal server error"

    }),500

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success":False,
       "error":405,
       "message":"method not allowed"

    }),405


  @app.errorhandler(400)
  def method_not_allowed(error):
    return jsonify({
      "success":False,
       "error":400,
       "message":"Bad request"

    }),400

  
  return app

    