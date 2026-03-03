# Railway Deployment Guide for DeepFake Detection

This guide will help you deploy your DeepFake Detection Flask application to Railway.

## 🚀 Why Railway?

**Railway advantages for ML applications:**
- ✅ Higher resource limits (up to 8GB RAM, 4 vCPUs)
- ✅ Longer execution times (no strict timeout limits)
- ✅ Better support for large files and models
- ✅ Native Python support
- ✅ Automatic HTTPS and custom domains
- ✅ Built-in database support
- ✅ Easy environment variable management

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)
3. **Railway CLI** (optional): Install with `npm i -g @railway/cli`

## Deployment Steps

### 1. Prepare Your Project

Ensure you have the following files in your project root:

```
DeepFake_Detection/
├── server.py                 # Main Flask application
├── models.py                 # Database models
├── requirements.txt          # Python dependencies
├── railway.json             # Railway configuration
├── nixpacks.toml            # Build configuration
├── download_models.py       # Model download script
├── templates/               # HTML templates
├── static/                  # Static files
├── model/                   # ML models (will be downloaded)
├── .gitignore              # Git ignore file
└── README.md               # Project documentation
```

### 2. Deploy via Railway Dashboard

#### Option A: GitHub Integration (Recommended)

1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Connect to Railway**:
   - Go to [railway.app/dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect it's a Python project

3. **Configure Environment Variables**:
   - Go to your project settings
   - Add environment variables:
     ```
     SECRET_KEY=your-secure-secret-key-here
     FLASK_ENV=production
     ```

4. **Deploy**: Railway will automatically build and deploy your application

#### Option B: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 3. Set Environment Variables

In your Railway dashboard:

1. Go to your project
2. Click on "Variables" tab
3. Add the following variables:

```
SECRET_KEY=your-secure-random-secret-key
FLASK_ENV=production
```

### 4. Configure Domain (Optional)

1. Go to your project settings
2. Click "Generate Domain" or add a custom domain
3. Your app will be available at the provided URL

## Configuration Files

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn server:app --bind 0.0.0.0:$PORT --timeout 600 --workers 1 --preload",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["cmake", "gcc", "gcc-unwrapped", "make", "pkg-config", "libopenblas", "lapack", "libx11", "gtk3", "boost", "curl", "wget"]

[phases.install]
cmds = [
    "pip install --upgrade pip", 
    "pip install -r requirements.txt",
    "pip install gdown tqdm requests",
    "mkdir -p model"
]

[phases.build]
cmds = [
    "echo 'Starting model download process...'",
    "python download_models.py",
    "echo 'Build process completed successfully!'"
]

[start]
cmd = "gunicorn server:app --bind 0.0.0.0:$PORT --timeout 600 --workers 1"
```

### requirements.txt
```
flask==2.3.3
flask-login==0.6.3
flask-sqlalchemy==3.0.5
torch==1.13.1
torchvision==0.14.1
face-recognition==1.3.0
numpy==1.24.3
opencv-python==4.8.1.78
matplotlib==3.7.2
scikit-image==0.21.0
cmake==3.27.2
dlib==19.24.2
gunicorn==21.2.0
werkzeug==2.3.7
tqdm==4.66.1
requests==2.31.0
gdown==4.7.1
```

## Model Download Configuration

The application automatically downloads models from Google Drive during deployment:

1. **Model Files**: Stored in Google Drive with public access
2. **Download Script**: `download_models.py` handles the download process
3. **Automatic Download**: Models are downloaded during Railway build process

### Current Model Configuration:
- **File ID**: `1Klw2YvgxCMoODEwlY0mpaApJ4Q_mVL6c`
- **Filename**: `model_84_acc_10_frames_final_data.pt`
- **Size**: ~216MB

## Database Setup

### Option 1: SQLite (Default)
- No additional setup required
- Data persists in the container

### Option 2: PostgreSQL (Recommended for Production)
1. Add PostgreSQL service in Railway
2. Set `DATABASE_URL` environment variable
3. Update your application to use PostgreSQL

## Monitoring and Logs

### View Logs
1. Go to your Railway project
2. Click on "Deployments" tab
3. Click on any deployment to view logs

### Monitor Performance
1. Go to "Metrics" tab
2. Monitor CPU, memory, and network usage
3. Set up alerts for resource usage

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check if all dependencies are in requirements.txt
   - Ensure nixpacks.toml has correct system dependencies
   - Check build logs for specific errors

2. **Model Loading Issues**
   - Ensure Google Drive file is publicly accessible
   - Check model download logs in build process
   - Verify model file paths in code

3. **Memory Issues**
   - Upgrade to a higher tier plan
   - Optimize model loading
   - Reduce batch sizes

4. **Timeout Issues**
   - Increase gunicorn timeout in railway.json
   - Optimize video processing
   - Use smaller video files

### Debugging Commands

```bash
# Check Railway CLI status
railway status

# View logs
railway logs

# Connect to running container
railway shell

# Restart service
railway service restart
```

## Performance Optimization

### For Railway Deployment

1. **Model Optimization**:
   - Use model quantization
   - Implement model caching
   - Consider using smaller models

2. **Video Processing**:
   - Implement progress indicators
   - Use async processing for large videos
   - Add client-side video compression

3. **Resource Management**:
   - Monitor memory usage
   - Implement proper cleanup
   - Use connection pooling for database

## Scaling

### Railway Plans
- **Starter**: $5/month - 512MB RAM, 0.5 vCPU
- **Developer**: $20/month - 2GB RAM, 1 vCPU
- **Pro**: $50/month - 4GB RAM, 2 vCPU
- **Business**: Custom pricing

### When to Scale
- High memory usage (>80% consistently)
- Slow response times
- Multiple concurrent users
- Large video processing requirements

## Security Considerations

1. **Environment Variables**:
   - Never commit secrets to Git
   - Use Railway's secure environment variables
   - Rotate secrets regularly

2. **File Uploads**:
   - Validate file types and sizes
   - Implement virus scanning
   - Use secure file storage

3. **Database Security**:
   - Use strong passwords
   - Enable SSL connections
   - Regular backups

## Cost Optimization

### Railway Pricing (as of 2024)
- **Starter**: $5/month
- **Developer**: $20/month
- **Pro**: $50/month
- **Business**: Custom

### Cost Optimization Tips
1. **Monitor Usage**: Track resource consumption
2. **Right-size Resources**: Choose appropriate plan
3. **Optimize Code**: Reduce memory and CPU usage
4. **Use Caching**: Minimize redundant processing

## Success Metrics

After deployment, verify:
- ✅ Application loads successfully
- ✅ User registration/login works
- ✅ Video upload and processing works
- ✅ Model loads without errors
- ✅ Results are displayed correctly
- ✅ No timeout or memory errors in logs

## Maintenance

### Regular Tasks
1. **Update Dependencies**: Keep packages updated
2. **Monitor Logs**: Check for errors and performance issues
3. **Backup Data**: Regular database backups
4. **Security Updates**: Apply security patches

### Updates and Deployments
1. **Test Locally**: Always test changes locally first
2. **Staging Environment**: Use staging for testing
3. **Rollback Plan**: Keep previous deployments for rollback
4. **Monitoring**: Monitor after each deployment

## Support

If you encounter issues:
1. Check Railway documentation
2. Review deployment logs
3. Contact Railway support
4. Check community forums

## Next Steps

After successful deployment:
1. Set up custom domain
2. Configure monitoring and alerts
3. Implement performance optimizations
4. Set up CI/CD pipeline
5. Plan for scaling

## Migration from Other Platforms

### From Vercel
- Railway has higher limits and better ML support
- No function timeout restrictions
- Better handling of large files

### From Heroku
- Railway is more cost-effective
- Better Python support
- Easier deployment process

### From AWS/GCP
- Railway is simpler to use
- Faster deployment
- Built-in monitoring and logging 