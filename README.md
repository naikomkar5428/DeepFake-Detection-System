# DeepFake Detection Web Application

A Flask-based web application for detecting deepfake videos using deep learning models.

## Features

- User authentication (signup/login)
- Video upload and deepfake detection
- Real-time confidence scoring
- Admin panel for dataset management
- Responsive web interface

## Prerequisites

- Python 3.10
- Docker (optional, for containerized deployment)
- Git

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd DeepFake_Detection
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export SECRET_KEY="your-secure-secret-key"
export FLASK_ENV="development"
```

5. Run the application:
```bash
python server.py
```

The application will be available at `http://localhost:3000`

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Or build and run manually:
```bash
docker build -t deepfake-detection .
docker run -p 10000:10000 -e SECRET_KEY="your-secure-secret-key" deepfake-detection
```

## Environment Variables

- `SECRET_KEY`: Flask secret key for session management
- `FLASK_ENV`: Set to "development" for debug mode, "production" for production
- `PORT`: Port number (default: 3000 for development, 10000 for Docker)

## Project Structure

```
DeepFake_Detection/
├── server.py              # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── Procfile              # Heroku deployment configuration
├── runtime.txt           # Python runtime version
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── model/                # Trained ML models
├── Uploaded_Files/       # User uploaded videos
├── Admin/                # Admin panel files
└── instance/             # Database files
```

## Deployment

### Heroku

1. Create a Heroku app:
```bash
heroku create your-app-name
```

2. Set environment variables:
```bash
heroku config:set SECRET_KEY="your-secure-secret-key"
```

3. Deploy:
```bash
git push heroku main
```

### Other Platforms

The application can be deployed to any platform that supports Python applications:

- **Railway**: Connect your GitHub repository
- **Render**: Use the provided Dockerfile
- **AWS/GCP/Azure**: Use the Dockerfile or deploy directly

## Security Considerations

1. Change the default SECRET_KEY in production
2. Use HTTPS in production
3. Implement proper user authentication and authorization
4. Validate and sanitize all user inputs
5. Set up proper logging and monitoring

## Troubleshooting

### Common Issues

1. **dlib installation fails**: Install system dependencies first:
   ```bash
   sudo apt-get install cmake g++ make libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev libboost-all-dev
   ```

2. **CUDA issues**: The application works with CPU-only PyTorch. For GPU support, install CUDA-enabled PyTorch.

3. **Memory issues**: Large video files may require more memory. Consider increasing Docker memory limits or using a larger instance.

### Logs

Check application logs:
```bash
# Docker
docker-compose logs

# Local
tail -f server_output.log
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request 