# Open-Meteo Air Quality (Home Assistant)

Custom integration для Home Assistant, получающая показатели качества воздуха из Open-Meteo Air Quality API.

## Возможности

- Настройка через UI без `configuration.yaml`
- Два режима добавления локации:
  - через зону Home Assistant
  - вручную по координатам
- Поддержка нескольких устройств (multi-entry) для разных зон/локаций
- `DataUpdateCoordinator` с обновлением по расписанию
- Настройка `scan_interval` через Options (без перезапуска)
- Сенсоры для ключевых полей Open-Meteo Air Quality:
  - European AQI / US AQI (+ breakdown)
  - PM10 / PM2.5
  - NO2 / SO2 / O3 / CO / ammonia / dust
  - UV index / UV clear sky
  - pollen (alder, birch, grass, mugwort, olive, ragweed)
- MDI-иконки для интеграции и сенсоров (в т.ч. `mdi:flower-pollen` для pollen)

## Установка через HACS

1. HACS → **Integrations** → меню (⋮) → **Custom repositories**
2. Добавить репозиторий: `https://github.com/avchaykin/ha-open-meteo-air-quality`
3. Category: **Integration**
4. Установить **Open-Meteo Air Quality**
5. Home Assistant → **Settings → Devices & Services → Add Integration**
6. Найти **Open-Meteo Air Quality** и выбрать источник локации:
   - Home Assistant zone, или
   - manual coordinates

> После добавления интеграция настраивается полностью через UI.

## Конфигурация

В Options доступен параметр:
- `scan_interval` — интервал обновления в минутах (5–180)

## Статус

- Текущий релиз: `v0.1.0`
- Репозиторий: https://github.com/avchaykin/ha-open-meteo-air-quality

## Дальше

- Улучшить user-facing документацию (примеры карточек Lovelace)
- Добавить автотесты (минимум smoke + config flow)
