"""
Schedule Organizer - Main Application
Organizes study schedules according to class availability by period
Supports Spanish and English languages
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

from src.parsers.schedule_parser import ScheduleParser
from src.services.ai_analyzer import AIAnalyzer
from src.services.translation_service import TranslationService

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Configure secret key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize services
schedule_parser = ScheduleParser()
ai_analyzer = AIAnalyzer(api_key=os.getenv('OPENAI_API_KEY'))
translation_service = TranslationService()

@app.route('/')
def index():
    """Main page - Schedule viewer"""
    return render_template('index.html')

@app.route('/api/schedules')
def get_schedules():
    """Get all available schedules"""
    try:
        schedules = schedule_parser.get_all_schedules()
        return jsonify({
            'success': True,
            'schedules': schedules
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedule/<schedule_id>')
def get_schedule(schedule_id):
    """Get specific schedule by ID"""
    try:
        schedule = schedule_parser.get_schedule_by_id(schedule_id)
        if schedule:
            return jsonify({
                'success': True,
                'schedule': schedule
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-content', methods=['POST'])
def analyze_content():
    """Analyze class content using AI"""
    try:
        data = request.json
        content = data.get('content', '')
        language = data.get('language', 'es')  # Default to Spanish
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'No content provided'
            }), 400
        
        analysis = ai_analyzer.analyze_class_content(content, language)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate text between Spanish and English"""
    try:
        data = request.json
        text = data.get('text', '')
        target_language = data.get('target_language', 'en')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        translated = translation_service.translate(text, target_language)
        
        return jsonify({
            'success': True,
            'translated': translated
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print(f"🚀 Starting Schedule Organizer on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
