# Open-Meteo Air Quality (Home Assistant)

Custom integration для Home Assistant, получающая показатели качества воздуха из Open-Meteo Air Quality API.

## Что уже есть

- Настройка через UI (`config_flow`) по широте/долготе
- `DataUpdateCoordinator` с периодическим обновлением
- Сенсоры по полному набору ключевых полей Open-Meteo Air Quality (AQI, pollutants, pollen, UV)
- Изменение `scan_interval` через Options

## Установка через HACS

1. HACS → **Integrations** → меню (⋮) → **Custom repositories**
2. Добавить репозиторий `https://github.com/avchaykin/ha-open-meteo-air-quality`
3. Category: **Integration**
4. Установить **Open-Meteo Air Quality**
5. Home Assistant → **Settings → Devices & Services → Add Integration**
6. Найти **Open-Meteo Air Quality**, указать широту/долготу

> После добавления интеграция настраивается полностью через UI, без `configuration.yaml`.

## Roadmap

- Привязка нескольких устройств к зонам Home Assistant
- Документация и примеры дашборда
- Подготовка первого релиза `v0.1.0`
