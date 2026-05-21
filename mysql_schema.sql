-- MySQL schema for encuestas-railway
-- Ejecuta este archivo en tu servidor MySQL para crear la base de datos y las tablas.

CREATE DATABASE IF NOT EXISTS `encuestas`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `encuestas`;

CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(80) NOT NULL,
  `email` VARCHAR(120) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `es_admin` TINYINT(1) NOT NULL DEFAULT 0,
  `fecha_registro` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_usuarios_username` (`username`),
  UNIQUE KEY `uq_usuarios_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `encuestas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `titulo` VARCHAR(200) NOT NULL,
  `descripcion` TEXT,
  `activa` TINYINT(1) NOT NULL DEFAULT 1,
  `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creador_id` INT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_encuestas_creador_id` (`creador_id`),
  CONSTRAINT `fk_encuestas_creador` FOREIGN KEY (`creador_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `preguntas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `encuesta_id` INT NOT NULL,
  `texto` VARCHAR(500) NOT NULL,
  `tipo` VARCHAR(20) NOT NULL DEFAULT 'texto',
  `opciones` TEXT,
  `orden` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_preguntas_encuesta_id` (`encuesta_id`),
  CONSTRAINT `fk_preguntas_encuesta` FOREIGN KEY (`encuesta_id`) REFERENCES `encuestas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `respuestas_encuesta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `encuesta_id` INT NOT NULL,
  `usuario_id` INT NULL,
  `fecha_completada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ip_address` VARCHAR(45),
  PRIMARY KEY (`id`),
  KEY `idx_respuestas_encuesta_encuesta_id` (`encuesta_id`),
  KEY `idx_respuestas_encuesta_usuario_id` (`usuario_id`),
  CONSTRAINT `fk_respuestas_encuesta_encuesta` FOREIGN KEY (`encuesta_id`) REFERENCES `encuestas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_respuestas_encuesta_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `respuestas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `pregunta_id` INT NOT NULL,
  `respuesta_encuesta_id` INT NOT NULL,
  `valor` TEXT NOT NULL,
  `fecha` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_respuestas_pregunta_id` (`pregunta_id`),
  KEY `idx_respuestas_respuesta_encuesta_id` (`respuesta_encuesta_id`),
  CONSTRAINT `fk_respuestas_pregunta` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_respuestas_respuesta_encuesta` FOREIGN KEY (`respuesta_encuesta_id`) REFERENCES `respuestas_encuesta` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
