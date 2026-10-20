-- ==============================================================================
-- LYCAON SOFTWARE - ESQUEMA DE BASE DE DATOS RELACIONAL (MySQL / XAMPP / Render)
-- Codificación: UTF8MB4 (Soporte completo para tildes y caracteres internacionales)
-- Integridad Referencial: LLAVES FORÁNEAS (FOREIGN KEYS) HABILITADAS
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS `lycaon_db` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `lycaon_db`;

-- 1. TABLA DE USUARIOS (ENTIDAD FUERTE)
CREATE TABLE IF NOT EXISTS `users` (
    `id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(191) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('administrador', 'cliente', 'operador') NOT NULL DEFAULT 'cliente',
    `verified` BOOLEAN NOT NULL DEFAULT TRUE,
    `avatar` VARCHAR(255) DEFAULT '',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. TABLA DE INVENTARIO / PRODUCTOS (ENTIDAD FUERTE)
CREATE TABLE IF NOT EXISTS `inventory` (
    `id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `name` VARCHAR(200) NOT NULL,
    `category` VARCHAR(100) NOT NULL,
    `stock` INT NOT NULL DEFAULT 0,
    `price` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `status` VARCHAR(50) NOT NULL DEFAULT 'active',
    `image_url` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_inventory_category` (`category`),
    INDEX `idx_inventory_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. TABLA DE PEDIDOS / ÓRDENES (ENTIDAD RELACIONAL CON LLAVES FORÁNEAS)
CREATE TABLE IF NOT EXISTS `orders` (
    `id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `user_id` VARCHAR(50) DEFAULT NULL,
    `user_email` VARCHAR(191) NOT NULL,
    `product_id` VARCHAR(50) DEFAULT NULL,
    `product_name` VARCHAR(200) DEFAULT NULL,
    `cantidad` INT NOT NULL DEFAULT 1,
    `subtotal` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `discount_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `total` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `status` VARCHAR(50) NOT NULL DEFAULT 'delivered',
    `invoice_id` VARCHAR(50) DEFAULT NULL,
    `items_json` JSON DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_orders_user_email` (`user_email`),
    INDEX `idx_orders_status` (`status`),
    INDEX `idx_orders_user_id` (`user_id`),
    INDEX `idx_orders_product_id` (`product_id`),
    CONSTRAINT `fk_orders_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    CONSTRAINT `fk_orders_product` FOREIGN KEY (`product_id`) 
        REFERENCES `inventory` (`id`) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. TABLA DE DETALLES DE PEDIDO (ORDER ITEMS - NORMALIZACIÓN RELACIONAL 1:N)
CREATE TABLE IF NOT EXISTS `order_items` (
    `id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `order_id` VARCHAR(50) NOT NULL,
    `product_id` VARCHAR(50) DEFAULT NULL,
    `product_name` VARCHAR(200) NOT NULL,
    `category` VARCHAR(100) DEFAULT 'General',
    `price` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `cantidad` INT NOT NULL DEFAULT 1,
    `subtotal` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    INDEX `idx_order_items_order` (`order_id`),
    INDEX `idx_order_items_product` (`product_id`),
    CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) 
        REFERENCES `orders` (`id`) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT `fk_order_items_product` FOREIGN KEY (`product_id`) 
        REFERENCES `inventory` (`id`) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. TABLA DE LOGS DE ACTIVIDAD (AUDITORÍA)
CREATE TABLE IF NOT EXISTS `activity_log` (
    `id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `user_email` VARCHAR(191) NOT NULL,
    `action` VARCHAR(100) NOT NULL,
    `entity_type` VARCHAR(50) NOT NULL,
    `entity_id` VARCHAR(50) NOT NULL,
    `ip_address` VARCHAR(45) NOT NULL DEFAULT '127.0.0.1',
    `details` TEXT DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_activity_user` (`user_email`),
    INDEX `idx_activity_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. TABLA DE TAREAS OPERATIVAS (CON LLAVE FORÁNEA A USUARIOS)
CREATE TABLE IF NOT EXISTS `tasks` (
    `id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `assigned_to` VARCHAR(191) DEFAULT NULL,
    `status` VARCHAR(50) NOT NULL DEFAULT 'pending',
    `priority` VARCHAR(50) NOT NULL DEFAULT 'medium',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_tasks_assigned` (`assigned_to`),
    CONSTRAINT `fk_tasks_user` FOREIGN KEY (`assigned_to`) 
        REFERENCES `users` (`email`) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. TABLA DE SUGERENCIAS / PQRS (CON LLAVE FORÁNEA A USUARIOS)
CREATE TABLE IF NOT EXISTS `suggestions` (
    `id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `user_email` VARCHAR(191) NOT NULL,
    `subject` VARCHAR(255) NOT NULL,
    `message` TEXT NOT NULL,
    `status` VARCHAR(50) NOT NULL DEFAULT 'unread',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_suggestions_user` (`user_email`),
    CONSTRAINT `fk_suggestions_user` FOREIGN KEY (`user_email`) 
        REFERENCES `users` (`email`) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
