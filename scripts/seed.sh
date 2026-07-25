#!/bin/bash
# =============================================================================
# Nexus AI — Database Seed Script
# =============================================================================

set -e

echo "Seeding default roles and permissions..."

# Use psql to seed the database
docker compose -f infrastructure/docker-compose.yml exec -T postgres psql -U nexusai -d nexusai <<SQL
-- Insert default roles
INSERT INTO roles (name, description) VALUES
    ('admin', 'Full system access'),
    ('editor', 'Can create and edit content'),
    ('viewer', 'Read-only access')
ON CONFLICT (name) DO NOTHING;

-- Insert default permissions
INSERT INTO permissions (name, resource, action) VALUES
    ('knowledge_base:read', 'knowledge_base', 'read'),
    ('knowledge_base:write', 'knowledge_base', 'write'),
    ('knowledge_base:delete', 'knowledge_base', 'delete'),
    ('agent:read', 'agent', 'read'),
    ('agent:write', 'agent', 'write'),
    ('agent:execute', 'agent', 'execute'),
    ('user:read', 'user', 'read'),
    ('user:manage', 'user', 'manage'),
    ('system:admin', 'system', 'admin')
ON CONFLICT (name) DO NOTHING;

-- Assign all permissions to admin role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'admin'
ON CONFLICT DO NOTHING;

-- Assign read permissions to viewer role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'viewer' AND p.action = 'read'
ON CONFLICT DO NOTHING;

SELECT 'Seed completed successfully!' AS result;
SQL

echo "Database seeded successfully."
