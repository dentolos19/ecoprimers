INSERT INTO events (
  title,
  description,
  location,
  date,
  image_url,
  id,
  updated_at,
  created_at
) VALUES
  ('Cleaning Day', 'Join us for a community cleaning day to help keep our neighborhood clean and green. All necessary cleaning supplies will be provided.', 'Yishun', '2025-03-01', '/static/img/cleaning-day.jpg', 'seed-event-cleaning-day', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('Newspaper Roll', 'Participate in our newspaper roll event where we collect and recycle old newspapers. Help us promote recycling and reduce waste.', 'Ang Mo Kio', '2025-03-01', '/static/img/newspaper-roll.jpg', 'seed-event-newspaper-roll', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

INSERT INTO products (
  name,
  description,
  points,
  stock,
  image_url,
  id,
  updated_at,
  created_at
) VALUES
  ('Iron on Badge', 'Show your support for sustainability with this iron-on badge. Perfect for bags, jackets, or hats!', 100, 50, '/static/img/iron-on-badge.png', 'seed-product-iron-badge', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('Notebook', 'Stay organized with this eco-friendly notebook made from recycled materials.', 1500, 50, '/static/img/notebook.png', 'seed-product-notebook', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('Reusable Cup', 'Made from durable materials, this reusable cup helps reduce single-use plastics and is perfect for your daily coffee needs!', 200, 50, '/static/img/reusable-cup.png', 'seed-product-reusable-cup', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('Reusable Utensil', 'Eco-friendly and reusable, this utensil set helps you reduce waste during meals.', 1000, 50, '/static/img/reusable-utensil.png', 'seed-product-reusable-utensil', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('Tote Bag', 'Made from durable, reusable materials, this tote bag helps reduce plastic waste.', 2000, 50, '/static/img/tote-bag.png', 'seed-product-tote-bag', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('ZipLog Bag', 'Reusable and durable, this ZipLog bag is ideal for storing snacks or supplies!', 500, 50, '/static/img/ziplog-bag.png', 'seed-product-ziplog-bag', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

INSERT INTO tasks (
  name,
  description,
  points,
  criteria,
  image_url,
  id,
  updated_at,
  created_at
) VALUES
  ('EcoWalkSnap', 'Step out for the planet! Take a walk, pick up litter, snap a photo, and upload it for AI verification. Keep your surroundings clean and beautiful!', 100, 'A green space with no litter and very clean, or litter picked up and disposed of properly.', '/static/img/first.png', 'seed-task-eco-walk-snap', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('Lights Out', 'Turn off unused lights, snap a pic, and let AI confirm your energy-saving efforts. With your help we can save our environment.', 100, 'A room with lights off, or a room with lights off and a person in the room.', '/static/img/lights.png', 'seed-task-lights-out', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('RecycleVision', 'Collect recyclables, snap a picture as you drop them in the bin, and let AI verify your eco-friendly actions. Save reusable material and save the world!', 100, 'Recyclables in a recycling bin, or recyclables being dropped into a recycling bin.', '/static/img/vision.png', 'seed-task-recycle-vision', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('Thirsty Roots', 'Water a plant or tree, snap a picture, and let AI verify your care for nature. Help save your environment with your conscious effort.', 100, 'A plant or tree being watered, or a plant or tree being watered with a watering can.', '/static/img/thirstyroots.png', 'seed-task-thirsty-roots', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;
