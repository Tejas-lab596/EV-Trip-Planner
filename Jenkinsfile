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
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Prepare Docker') {
      steps {
        sh 'docker version'
        sh 'docker compose version || true'
        sh 'id -nG'
      }
    }

    stage('Build images') {
      steps {
        sh "${DOCKER_COMPOSE} build --pull"
      }
    }

    stage('Deploy (Compose up)') {
      steps {
        // write runtime env that Compose will mount into the backend container
        sh '''
          mkdir -p backend
          cat > backend/.env <<EOF
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME}
SECRET_KEY=${SECRET_KEY}
EOF
        '''
        sh "${DOCKER_COMPOSE} up -d --remove-orphans"
      }
    }

    stage('Smoke check') {
      steps {
        // quick health probe inside the backend container
        sh 'docker exec ev-backend sh -lc "curl -fsS http://localhost:5000/health"'
      }
    }
  }

  post {
    success { echo '✅ Deployment completed successfully!' }
    failure { echo '❌ Deployment failed.' }
    always  { sh 'docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"' }
  }
}
