# Prometheus & Grafana Monitoring Stack

Мониторинг системы, базы данных и внешних API с помощью Prometheus и Grafana.

## Компоненты

- **Prometheus**: Сбор и хранение метрик
- **Grafana**: Визуализация метрик
- **Node Exporter**: Системные метрики
- **PostgreSQL Exporter**: Метрики базы данных
- **Custom Exporter**: Метрики из внешних API

## Запуск

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Остановка
docker-compose down