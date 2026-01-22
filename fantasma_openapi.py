"""
OpenAPI/Swagger Documentation for FantasmaWiFi-Pro API
"""

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "FantasmaWiFi-Pro API",
        "description": "REST API for controlling FantasmaWiFi-Pro network sharing",
        "version": "7.5.0",
        "contact": {
            "name": "FantasmaWiFi-Pro",
            "url": "https://github.com/Blackmvmba88/FantasmaWiFi-Pro"
        },
        "license": {
            "name": "Sovereignty License",
            "url": "https://github.com/Blackmvmba88/FantasmaWiFi-Pro/blob/main/LICENSE_SOVEREIGNTY.md"
        }
    },
    "servers": [
        {
            "url": "http://localhost:8080",
            "description": "Local development server"
        }
    ],
    "security": [
        {
            "ApiKeyAuth": []
        }
    ],
    "paths": {
        "/api/interfaces": {
            "get": {
                "summary": "List network interfaces",
                "description": "Get all available network interfaces on the system",
                "tags": ["Interfaces"],
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of interfaces",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "interfaces": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/NetworkInterface"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                    "429": {"$ref": "#/components/responses/RateLimitError"}
                }
            }
        },
        "/api/status": {
            "get": {
                "summary": "Get sharing status",
                "description": "Get current network sharing status",
                "tags": ["Status"],
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "Current status",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Status"}
                            }
                        }
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"}
                }
            }
        },
        "/api/start": {
            "post": {
                "summary": "Start network sharing",
                "description": "Start sharing internet connection with specified configuration",
                "tags": ["Control"],
                "security": [{"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ShareConfig"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Sharing started successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                            }
                        }
                    },
                    "400": {"$ref": "#/components/responses/BadRequestError"},
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                    "429": {"$ref": "#/components/responses/RateLimitError"}
                }
            }
        },
        "/api/stop": {
            "post": {
                "summary": "Stop network sharing",
                "description": "Stop currently active network sharing",
                "tags": ["Control"],
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "Sharing stopped successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                            }
                        }
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"}
                }
            }
        },
        "/api/profiles": {
            "get": {
                "summary": "List configuration profiles",
                "description": "Get all saved configuration profiles",
                "tags": ["Profiles"],
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of profile names",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "profiles": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "summary": "Save configuration profile",
                "description": "Save a new configuration profile",
                "tags": ["Profiles"],
                "security": [{"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ProfileSave"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Profile saved",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                            }
                        }
                    },
                    "400": {"$ref": "#/components/responses/BadRequestError"}
                }
            }
        },
        "/api/profiles/{name}": {
            "get": {
                "summary": "Get configuration profile",
                "description": "Get a specific configuration profile by name",
                "tags": ["Profiles"],
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {
                        "name": "name",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Profile name"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Profile data",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "profile": {"$ref": "#/components/schemas/ShareConfig"}
                                    }
                                }
                            }
                        }
                    },
                    "404": {"$ref": "#/components/responses/NotFoundError"}
                }
            },
            "delete": {
                "summary": "Delete configuration profile",
                "description": "Delete a configuration profile by name",
                "tags": ["Profiles"],
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {
                        "name": "name",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Profile name"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Profile deleted",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                            }
                        }
                    },
                    "404": {"$ref": "#/components/responses/NotFoundError"}
                }
            }
        }
    },
    "components": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for authentication. Get your key from the web UI or server logs."
            }
        },
        "schemas": {
            "NetworkInterface": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "example": "en0",
                        "description": "Interface name"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["wifi", "ethernet", "usb", "bluetooth"],
                        "example": "wifi",
                        "description": "Interface type"
                    },
                    "status": {
                        "type": "string",
                        "example": "active",
                        "description": "Current status"
                    },
                    "ip": {
                        "type": "string",
                        "example": "192.168.1.100",
                        "description": "IP address"
                    },
                    "mac": {
                        "type": "string",
                        "example": "aa:bb:cc:dd:ee:ff",
                        "description": "MAC address"
                    }
                }
            },
            "Status": {
                "type": "object",
                "properties": {
                    "active": {
                        "type": "boolean",
                        "example": True,
                        "description": "Whether sharing is active"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["hotspot", "bridge", "none"],
                        "example": "hotspot",
                        "description": "Current operation mode"
                    },
                    "source_interface": {
                        "type": "string",
                        "example": "en0",
                        "description": "Source interface name"
                    },
                    "target_interface": {
                        "type": "string",
                        "example": "en1",
                        "description": "Target interface name"
                    },
                    "uptime": {
                        "type": "integer",
                        "example": 3600,
                        "description": "Uptime in seconds"
                    },
                    "platform": {
                        "type": "string",
                        "example": "macOS",
                        "description": "Operating platform"
                    }
                }
            },
            "ShareConfig": {
                "type": "object",
                "required": ["source", "target", "mode"],
                "properties": {
                    "source": {
                        "type": "string",
                        "example": "en0",
                        "description": "Source interface (consumes internet)"
                    },
                    "target": {
                        "type": "string",
                        "example": "en1",
                        "description": "Target interface (distributes internet)"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["hotspot", "bridge"],
                        "example": "hotspot",
                        "description": "Operation mode"
                    },
                    "ssid": {
                        "type": "string",
                        "example": "MyHotspot",
                        "description": "WiFi network name (required for hotspot mode)"
                    },
                    "password": {
                        "type": "string",
                        "example": "SecurePass123",
                        "description": "WiFi password (required for hotspot mode, min 8 chars)"
                    },
                    "channel": {
                        "type": "integer",
                        "example": 6,
                        "minimum": 1,
                        "maximum": 11,
                        "description": "WiFi channel (default: 6)"
                    },
                    "ip_range": {
                        "type": "string",
                        "example": "192.168.137.0/24",
                        "description": "IP range for DHCP (default: 192.168.137.0/24)"
                    }
                }
            },
            "ProfileSave": {
                "type": "object",
                "required": ["name", "config"],
                "properties": {
                    "name": {
                        "type": "string",
                        "example": "home_usb",
                        "description": "Profile name"
                    },
                    "config": {
                        "$ref": "#/components/schemas/ShareConfig"
                    }
                }
            },
            "SuccessResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "message": {
                        "type": "string",
                        "example": "Operation completed successfully"
                    }
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Error type"
                    },
                    "message": {
                        "type": "string",
                        "example": "Error description"
                    }
                }
            }
        },
        "responses": {
            "UnauthorizedError": {
                "description": "API key is missing or invalid",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            },
            "BadRequestError": {
                "description": "Invalid request parameters",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            },
            "NotFoundError": {
                "description": "Resource not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            },
            "RateLimitError": {
                "description": "Rate limit exceeded",
                "headers": {
                    "X-RateLimit-Limit": {
                        "schema": {"type": "integer"},
                        "description": "Request limit per minute"
                    },
                    "X-RateLimit-Remaining": {
                        "schema": {"type": "integer"},
                        "description": "Remaining requests"
                    },
                    "Retry-After": {
                        "schema": {"type": "integer"},
                        "description": "Seconds to wait before retrying"
                    }
                },
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            }
        }
    },
    "tags": [
        {
            "name": "Interfaces",
            "description": "Network interface discovery"
        },
        {
            "name": "Status",
            "description": "Sharing status monitoring"
        },
        {
            "name": "Control",
            "description": "Start and stop sharing"
        },
        {
            "name": "Profiles",
            "description": "Configuration profile management"
        }
    ]
}


def get_openapi_html():
    """Generate Swagger UI HTML"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>FantasmaWiFi-Pro API Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css"/>
    <style>
        body {
            margin: 0;
            padding: 0;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            window.ui = SwaggerUIBundle({
                url: "/api/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            });
        };
    </script>
</body>
</html>
    """
