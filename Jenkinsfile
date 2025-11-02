pipeline {
  agent any

  environment {
    DOCKER_COMPOSE = 'docker compose'
    DB_HOST     = credentials('rds-host')
    DB_PORT     = '3306'
    DB_USER     = credentials('rds-user')
    DB_PASSWORD = credentials('rds-password')
    DB_NAME     = credentials('rds-dbname')
    SECRET_KEY  = credentials('app-secret')
  }

  options {
    timestamps()
    // ansiColor removed
  }

  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Prepare Docker') {
      steps {
        sh 'docker version'
        sh 'docker compose version || true'
        sh 'id -nG'
      }
    }

    stage('Build images') {
      steps { sh "docker compose build --pull" }
    }

    stage('Deploy (Compose up)') {
      steps {
        sh '''
cat > backend/.env <<EOF
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME}
SECRET_KEY=${SECRET_KEY}
EOF
'''
        sh "docker compose up -d --remove-orphans"
      }
    }
  }

  post {
    success { echo '✅ Deployment completed successfully!' }
    failure { echo '❌ Deployment failed.' }
    always  { sh 'docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"' }
  }
}
