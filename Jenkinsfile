pipeline {
  agent any

  environment {
    APP_DIR = "/opt/apps/ssau-schedule-bot"
  }

  stages {
    stage('Checkout (для статуса)') {
      steps {
        checkout scm
      }
    }

    stage('Deploy (docker compose)') {
      steps {
        sh """
          set -euo pipefail
          cd "${APP_DIR}"
          git fetch --all
          git reset --hard origin/main

          # сборка и запуск
          docker compose -f docker-compose.yaml up -d --build

          # показать статус
          docker compose -f docker-compose.yaml ps
        """
      }
    }
  }
}