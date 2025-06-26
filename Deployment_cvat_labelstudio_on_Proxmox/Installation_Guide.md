# Развертывание CVAT и Label Studio на Proxmox

Данное руководство описывает процесс установки и настройки инструментов для аннотирования данных CVAT и Label Studio в среде виртуализации Proxmox.

## Установка и настройка CVAT

### Предварительные требования

Перед началом работы убедитесь, что система соответствует следующим требованиям:
- Операционная система: Ubuntu/Debian
- Свободное дисковое пространство: минимум 10% от общего объема
- Установленные компоненты: `docker`, `docker compose`, `make`

> **Примечание для Windows:** Для выполнения команд Makefile используйте Git Bash или WSL.

### Шаг 1: Установка Docker и Docker Compose

Выполните следующие команды для установки необходимых компонентов:

```bash
# Обновление пакетов системы
sudo apt-get update

# Установка зависимостей
sudo apt-get --no-install-recommends install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common

# Добавление GPG ключа Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Добавление репозитория Docker
sudo add-apt-repository \
  "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) \
  stable"

# Обновление списка пакетов и установка Docker
sudo apt-get update
sudo apt-get --no-install-recommends install -y \
  docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Шаг 2: Настройка прав пользователя

Для работы с Docker без использования sudo выполните:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```

**Важно:** После выполнения команд необходимо перелогиниться в системе.

### Шаг 3: Получение исходного кода

Клонируйте официальный репозиторий CVAT:

```bash
git clone https://github.com/cvat-ai/cvat
cd cvat
```

### Шаг 4: Настройка сетевых параметров

Установите переменную окружения с внешним IP-адресом сервера:

```bash
export CVAT_HOST=YOUR_EXTERNAL_IP_ADDRESS
```

### Шаг 5: Исправление конфигурации портов

Перед запуском контейнеров выполните следующие команды:

```bash
# Остановка существующих контейнеров
docker compose down

# Запуск OPA сервиса для авторизации
docker run -d --rm --name cvat_opa_debug -p 8181:8181 openpolicyagent/opa:0.34.2-rootless \
  run --server --set=decision_logs.console=true \
  --set=services.cvat.url=http://host.docker.internal:7000/ \
  --set=bundles.cvat.service=cvat --set=bundles.cvat.resource=/api/auth/rules
```

### Шаг 6: Запуск сервиса

Запустите все контейнеры CVAT:

```bash
docker compose up -d
```

### Настройка пользовательского порта

Если требуется изменить стандартный порт 8080, отредактируйте файл конфигурации:

```bash
nano runners/CVAT_runner/cvat/docker-compose.yml
```

Найдите секцию traefik и измените внешний порт:

```yaml
traefik:
  image: traefik:v3.3
  container_name: traefik
  restart: always
  ports:
    - "YOUR_CUSTOM_PORT:8080"  # Замените YOUR_CUSTOM_PORT на нужный порт
    - "8090:8090"
```

### Создание администратора

После запуска сервисов создайте учетную запись суперпользователя:

```bash
# Убедитесь, что все сервисы запущены
docker compose ps

# Создание суперпользователя
docker compose exec cvat_server python3 manage.py createsuperuser
```

---

## Установка и настройка Label Studio

### Подготовка рабочей среды

Создайте рабочую директорию для Label Studio:

```bash
mkdir label_studio && cd label_studio
```

### Настройка хранилища данных

Создайте директорию для данных и настройте права доступа:

```bash
mkdir data
sudo chown -R 1001:1001 data
```

### Создание конфигурационного файла

Создайте файл docker-compose.yml:

```bash
nano docker-compose.yml
```

Добавьте следующее содержимое:

```yaml
version: '3.8'

services:
  label-studio:
    image: heartexlabs/label-studio:latest
    container_name: label-studio
    ports:
      - "8081:8080"  # При необходимости измените внешний порт
    volumes:
      - ./data:/label-studio/data
    restart: unless-stopped
    user: "1001:1001"
    environment:
      - LABEL_STUDIO_ML_BACKEND_V2=true
```

### Запуск Label Studio

Запустите контейнер Label Studio:

```bash
docker compose up -d
```

### Мониторинг работы сервиса

Для просмотра логов используйте команду:

```bash
docker compose logs -f
```

---

## Дополнительные рекомендации

### Системные требования
- **Дисковое пространство:** Обязательно оставляйте минимум 10% свободного места
- **Память:** Рекомендуется не менее 4GB RAM для стабильной работы
- **Процессор:** Минимум 2 ядра для комфортной работы

### Безопасность
- Регулярно обновляйте образы контейнеров
- Используйте сложные пароли для административных учетных записей
- Рассмотрите возможность настройки SSL-сертификатов для защищенного соединения

### Резервное копирование
Регулярно создавайте резервные копии данных:

```bash
# Для CVAT
docker compose exec postgres pg_dump -U root cvat > cvat_backup.sql

# Для Label Studio
tar -czf label_studio_backup.tar.gz ./data
```

### Обновление сервисов

Для обновления до последних версий:

```bash
# Остановка сервисов
docker compose down

# Обновление образов
docker compose pull

# Перезапуск с новыми образами
docker compose up -d
```

---

## Решение типичных проблем

### Проблема с правами доступа
Если возникают ошибки доступа к файлам:

```bash
sudo chown -R $USER:$USER ./data
```

### Проблема с портами
Если порт уже занят, найдите свободный порт:

```bash
netstat -tulpn | grep :8080
```

### Очистка системы
Для освобождения места удалите неиспользуемые контейнеры:

```bash
docker system prune -a
```

---
