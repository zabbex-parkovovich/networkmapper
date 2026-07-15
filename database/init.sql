-- Создание базы данных (если нужно)
-- CREATE DATABASE network_map;

-- Таблица устройств
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    ip INET NOT NULL,
    model VARCHAR(100),
    location VARCHAR(200),
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица портов
CREATE TABLE IF NOT EXISTS ports (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    port_type VARCHAR(20) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'unknown',
    patch_panel VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(device_id, name)
);

-- Таблица связей
CREATE TABLE IF NOT EXISTS links (
    id SERIAL PRIMARY KEY,
    port_a_id INTEGER REFERENCES ports(id) ON DELETE CASCADE,
    port_b_id INTEGER REFERENCES ports(id) ON DELETE CASCADE,
    discovered_at TIMESTAMP DEFAULT NOW(),
    CHECK (port_a_id < port_b_id),
    UNIQUE(port_a_id, port_b_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_ports_device ON ports(device_id);
CREATE INDEX IF NOT EXISTS idx_links_port_a ON links(port_a_id);
CREATE INDEX IF NOT EXISTS idx_links_port_b ON links(port_b_id);

-- Тестовые данные
INSERT INTO devices (name, ip, model, location, role) VALUES
    ('H3C#1', '172.22.40.1', 'H3C S5170S', 'Серверная №1', 'distribution'),
    ('H3C#2', '172.22.40.2', 'H3C S5170S', 'Серверная №2', 'access'),
    ('H3C#3', '172.22.40.3', 'H3C S5170S', 'Серверная №3', 'access'),
    ('H3C#4', '172.22.40.4', 'H3C S5170S', 'Серверная №4', 'access')
ON CONFLICT (name) DO NOTHING;

-- Таблица конечных устройств, подключенных к портам
CREATE TABLE IF NOT EXISTS connected_hosts (
    id SERIAL PRIMARY KEY,
    port_id INTEGER REFERENCES ports(id) ON DELETE CASCADE,
    ip_address INET,                          -- Может быть NULL, если берём из mac-address
    mac_address MACADDR NOT NULL,
    vlan_id INTEGER DEFAULT 1,
    vendor VARCHAR(100),                      -- Опционально: производитель по OUI
    last_seen TIMESTAMP DEFAULT NOW(),        -- Когда последний раз видели в ARP/MAC
    UNIQUE(mac_address, vlan_id, port_id) -- Один MAC на одном порту в конкретном VLAN
);

CREATE INDEX IF NOT EXISTS idx_hosts_port ON connected_hosts(port_id);
CREATE INDEX IF NOT EXISTS idx_hosts_mac ON connected_hosts(mac_address);
