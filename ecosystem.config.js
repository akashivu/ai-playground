module.exports = {
  apps: [{
    name: 'ai-platform',
    script: '/home/ubuntu/ai-playground/venv/bin/uvicorn',
    args: 'app:app --host 127.0.0.1 --port 8000 --workers 2',
    cwd: '/home/ubuntu/ai-playground',
    interpreter: 'none',
    env: {
      PATH: '/home/ubuntu/ai-playground/venv/bin:/usr/bin:/bin',
    },
    error_file: '/home/ubuntu/ai-playground/logs/pm2-error.log',
    out_file: '/home/ubuntu/ai-playground/logs/pm2-out.log',
    time: true,
  }]
};
