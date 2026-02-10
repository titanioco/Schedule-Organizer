# Schedule Organizer / Organizador de Horarios

[English](#english) | [Español](#español)

---

## English

### Overview
Schedule Organizer is an intelligent assistant designed to help students organize their study schedules according to class availability by period/semester. The application features AI-powered content analysis and dual language support (Spanish/English).

### Features
- 📅 **Schedule Management**: Read and parse HTML files containing class schedules and groups
- 🤖 **AI-Powered Analysis**: Analyze class content using OpenAI to provide helpful insights including:
  - Course summaries
  - Key topics identification
  - Difficulty level assessment
  - Prerequisites suggestions
  - Study recommendations
- 🌍 **Dual Language Support**: Full interface available in Spanish and English
- 📊 **Class Information**: View detailed information about classes, groups, schedules, and availability
- 💻 **Modern Web Interface**: Built with Python, HTML, CSS, and TypeScript

### Technology Stack
- **Backend**: Python 3.x with Flask
- **Frontend**: TypeScript, HTML5, CSS3
- **AI Integration**: OpenAI API (GPT-3.5-turbo)
- **HTML Parsing**: BeautifulSoup4
- **API**: RESTful API with JSON responses

### Installation

#### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

#### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/titanioco/Schedule-Organizer.git
cd Schedule-Organizer
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Node.js dependencies and build TypeScript**
```bash
npm install
npm run build
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. **Run the application**
```bash
python app.py
```

6. **Access the application**
Open your browser and navigate to: `http://localhost:5000`

### Usage

#### Adding Schedule Files
1. Place your HTML schedule files in the `data/schedules/` directory
2. The HTML files should follow the structure shown in the sample file `semester_2024_1.html`
3. The parser will automatically detect and load all schedule files

#### Using the AI Analysis
1. Navigate to the "AI Analysis" tab
2. Enter the course content you want to analyze
3. Click "Analyze with AI"
4. View the comprehensive analysis including summary, topics, difficulty, and recommendations

#### Switching Languages
Click the language toggle button in the header to switch between Spanish and English

### API Endpoints

- `GET /api/schedules` - Get all available schedules
- `GET /api/schedule/<schedule_id>` - Get specific schedule by ID
- `POST /api/analyze-content` - Analyze class content with AI
- `POST /api/translate` - Translate text between Spanish and English
- `GET /api/health` - Health check endpoint

### Project Structure
```
Schedule-Organizer/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── package.json               # Node.js dependencies
├── tsconfig.json              # TypeScript configuration
├── src/
│   ├── models/                # Data models
│   ├── parsers/               # HTML schedule parsers
│   ├── services/              # AI analyzer and translation services
│   └── typescript/            # TypeScript source files
├── templates/                 # HTML templates
├── static/
│   ├── css/                   # CSS stylesheets
│   └── js/                    # Compiled JavaScript
└── data/
    └── schedules/             # HTML schedule files
```

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

### License
MIT License

---

## Español

### Descripción General
Organizador de Horarios es un asistente inteligente diseñado para ayudar a los estudiantes a organizar sus horarios de estudio según la disponibilidad de clases por período/semestre. La aplicación cuenta con análisis de contenido impulsado por IA y soporte dual de idiomas (Español/Inglés).

### Características
- 📅 **Gestión de Horarios**: Lee y analiza archivos HTML que contienen horarios de clases y grupos
- 🤖 **Análisis con IA**: Analiza el contenido de las clases usando OpenAI para proporcionar información útil incluyendo:
  - Resúmenes de cursos
  - Identificación de temas clave
  - Evaluación del nivel de dificultad
  - Sugerencias de prerrequisitos
  - Recomendaciones de estudio
- 🌍 **Soporte Dual de Idiomas**: Interfaz completa disponible en Español e Inglés
- 📊 **Información de Clases**: Visualiza información detallada sobre clases, grupos, horarios y disponibilidad
- 💻 **Interfaz Web Moderna**: Construida con Python, HTML, CSS y TypeScript

### Stack Tecnológico
- **Backend**: Python 3.x con Flask
- **Frontend**: TypeScript, HTML5, CSS3
- **Integración IA**: API de OpenAI (GPT-3.5-turbo)
- **Análisis HTML**: BeautifulSoup4
- **API**: API RESTful con respuestas JSON

### Instalación

#### Requisitos Previos
- Python 3.8 o superior
- Node.js 14 o superior
- npm o yarn

#### Pasos de Configuración

1. **Clonar el repositorio**
```bash
git clone https://github.com/titanioco/Schedule-Organizer.git
cd Schedule-Organizer
```

2. **Instalar dependencias de Python**
```bash
pip install -r requirements.txt
```

3. **Instalar dependencias de Node.js y compilar TypeScript**
```bash
npm install
npm run build
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Edita .env y agrega tu clave API de OpenAI
```

5. **Ejecutar la aplicación**
```bash
python app.py
```

6. **Acceder a la aplicación**
Abre tu navegador y navega a: `http://localhost:5000`

### Uso

#### Agregar Archivos de Horarios
1. Coloca tus archivos HTML de horarios en el directorio `data/schedules/`
2. Los archivos HTML deben seguir la estructura mostrada en el archivo de ejemplo `semester_2024_1.html`
3. El analizador detectará y cargará automáticamente todos los archivos de horarios

#### Usar el Análisis con IA
1. Navega a la pestaña "Análisis AI"
2. Ingresa el contenido del curso que deseas analizar
3. Haz clic en "Analizar con AI"
4. Visualiza el análisis completo incluyendo resumen, temas, dificultad y recomendaciones

#### Cambiar Idiomas
Haz clic en el botón de cambio de idioma en el encabezado para alternar entre Español e Inglés

### Endpoints de la API

- `GET /api/schedules` - Obtener todos los horarios disponibles
- `GET /api/schedule/<schedule_id>` - Obtener un horario específico por ID
- `POST /api/analyze-content` - Analizar contenido de clase con IA
- `POST /api/translate` - Traducir texto entre Español e Inglés
- `GET /api/health` - Endpoint de verificación de salud

### Estructura del Proyecto
```
Schedule-Organizer/
├── app.py                      # Aplicación Flask principal
├── requirements.txt            # Dependencias de Python
├── package.json               # Dependencias de Node.js
├── tsconfig.json              # Configuración de TypeScript
├── src/
│   ├── models/                # Modelos de datos
│   ├── parsers/               # Analizadores de horarios HTML
│   ├── services/              # Servicios de análisis IA y traducción
│   └── typescript/            # Archivos fuente TypeScript
├── templates/                 # Plantillas HTML
├── static/
│   ├── css/                   # Hojas de estilo CSS
│   └── js/                    # JavaScript compilado
└── data/
    └── schedules/             # Archivos HTML de horarios
```

### Contribuir
¡Las contribuciones son bienvenidas! Por favor, siéntete libre de enviar un Pull Request.

### Licencia
Licencia MIT
