pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  environment {
    APP_DIR = "/opt/apps/ssau-schedule-bot"
    APP_PARENT_DIR = "/opt/apps"
    REPO_URL = "https://github.com/golosoman/ssau-schedule-bot.git"
    DEPLOY_BRANCH = "main"
    COMPOSE_FILE = "docker-compose.yaml"
    BACKUP_DIR = "backups"
    BACKUP_KEEP = "20"
  }

  stages {
    stage('Checkout (для статуса)') {
      steps {
        checkout scm
      }
    }

    stage('Deploy (main only)') {
      when {
        branch 'main'
      }
      steps {
        sh '''#!/usr/bin/env bash
          set -euo pipefail

          echo "Sync repo on host path: ${APP_DIR}"
          docker run --rm \
            --entrypoint /bin/sh \
            -e APP_DIR="${APP_DIR}" \
            -e REPO_URL="${REPO_URL}" \
            -e DEPLOY_BRANCH="${DEPLOY_BRANCH}" \
            -v "${APP_PARENT_DIR}:${APP_PARENT_DIR}" \
            alpine/git:latest -euxc '
              if [ ! -d "${APP_DIR}/.git" ]; then
                git clone "${REPO_URL}" "${APP_DIR}"
              fi

              cd "${APP_DIR}"
              git fetch --all --prune
              git checkout "${DEPLOY_BRANCH}"
              git reset --hard "origin/${DEPLOY_BRANCH}"
            '

          JENKINS_IMAGE="$(docker inspect --format='{{.Config.Image}}' jenkins)"
          echo "Compose helper image: ${JENKINS_IMAGE}"

          docker run --rm \
            --user 0:0 \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${APP_DIR}:${APP_DIR}" \
            -w "${APP_DIR}" \
            -e COMPOSE_FILE="${COMPOSE_FILE}" \
            -e BACKUP_DIR="${BACKUP_DIR}" \
            -e BACKUP_KEEP="${BACKUP_KEEP}" \
            "${JENKINS_IMAGE}" sh -euxc '
              docker compose -f "${COMPOSE_FILE}" stop || true

              if [ -f "data/ssau_schedule_bot.db" ]; then
                ts="$(date -u +%Y%m%dT%H%M%SZ)"
                mkdir -p "${BACKUP_DIR}"
                tar -czf "${BACKUP_DIR}/data-${ts}.tar.gz" data
                echo "Backup created: ${BACKUP_DIR}/data-${ts}.tar.gz"

                ls -1t "${BACKUP_DIR}"/data-*.tar.gz 2>/dev/null \
                  | tail -n +$((BACKUP_KEEP + 1)) \
                  | xargs -r rm -f
              else
                echo "Database file data/ssau_schedule_bot.db not found, backup skipped"
              fi

              docker compose -f "${COMPOSE_FILE}" up -d --build
              docker compose -f "${COMPOSE_FILE}" ps
            '
        '''
      }
    }
  }
}
