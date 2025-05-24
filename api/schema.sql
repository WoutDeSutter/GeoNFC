USE geonfc;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS tags;

-- Create tags table
CREATE TABLE tags (
    tag_id VARCHAR(50) PRIMARY KEY,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create logs table
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tag_id VARCHAR(50) NOT NULL,
    username VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);

-- Create indexes
CREATE INDEX idx_tag_id ON logs(tag_id);
CREATE INDEX idx_timestamp ON logs(timestamp);

-- Insert test data
INSERT INTO tags (tag_id, latitude, longitude) VALUES 
('TEST001', 50.8503, 4.3517),
('TEST002', 51.2195, 4.4025),
('TEST003', 50.8796, 4.7009),
('TEST004', 50.8503, 5.6909),
('TEST005', 50.4114, 4.4445); 