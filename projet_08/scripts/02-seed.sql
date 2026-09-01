-- ============================================================
-- SUPPORT CLIENT - SEED DATA
-- PostgreSQL
-- ============================================================

BEGIN;

-- ============================================================
-- 1. CUSTOMERS
-- ============================================================

INSERT INTO customers
    (first_name, last_name, email, phone, address, city,
     postal_code, country, status)
VALUES
    ('Jean', 'Tremblay', 'jean.tremblay@example.com',
     '+1-514-555-0101', '1250 Rue Sainte-Catherine Ouest',
     'Montreal', 'H3G 1P1', 'Canada', 'active'),

    ('Sophie', 'Martin', 'sophie.martin@example.com',
     '+1-514-555-0102', '4500 Rue Saint-Denis',
     'Montreal', 'H2J 2L1', 'Canada', 'active'),

    ('Marc', 'Dubois', 'marc.dubois@example.com',
     '+1-418-555-0103', '850 Grande Allée',
     'Quebec City', 'G1R 2K5', 'Canada', 'active'),

    ('Julie', 'Roy', 'julie.roy@example.com',
     '+1-514-555-0104', '7200 Boulevard Décarie',
     'Montreal', 'H4P 2N1', 'Canada', 'active'),

    ('Thomas', 'Gagnon', 'thomas.gagnon@example.com',
     '+1-438-555-0105', '300 Rue Sherbrooke Est',
     'Montreal', 'H2X 1E6', 'Canada', 'active'),

    ('Nathalie', 'Bouchard', 'nathalie.bouchard@example.com',
     '+1-514-555-0106', '210 Rue Wellington',
     'Montreal', 'H3C 1V8', 'Canada', 'active'),

    ('Alexandre', 'Fortin', 'alexandre.fortin@example.com',
     '+1-514-555-0107', '1800 Avenue du Mont-Royal',
     'Montreal', 'H2H 1J6', 'Canada', 'active'),

    ('Camille', 'Lavoie', 'camille.lavoie@example.com',
     '+1-418-555-0108', '90 Rue Saint-Jean',
     'Quebec City', 'G1R 1N5', 'Canada', 'active'),

    ('David', 'Bergeron', 'david.bergeron@example.com',
     '+1-514-555-0109', '5600 Rue Masson',
     'Montreal', 'H2H 1A4', 'Canada', 'active'),

    ('Isabelle', 'Côté', 'isabelle.cote@example.com',
     '+1-514-555-0110', '125 Rue Ontario Est',
     'Montreal', 'H2X 1H4', 'Canada', 'active'),

    ('Olivier', 'Lefebvre', 'olivier.lefebvre@example.com',
     '+1-514-555-0111', '700 Rue de la Gauchetière',
     'Montreal', 'H3B 2M4', 'Canada', 'active'),

    ('Sarah', 'Pelletier', 'sarah.pelletier@example.com',
     '+1-514-555-0112', '950 Avenue du Parc',
     'Montreal', 'H2X 2H2', 'Canada', 'active'),

    ('Antoine', 'Morin', 'antoine.morin@example.com',
     '+1-450-555-0113', '120 Rue Principale',
     'Longueuil', 'J4H 1H2', 'Canada', 'active'),

    ('Marie', 'Girard', 'marie.girard@example.com',
     '+1-514-555-0114', '4000 Boulevard Saint-Laurent',
     'Montreal', 'H2W 1Y8', 'Canada', 'active'),

    ('Patrick', 'Simard', 'patrick.simard@example.com',
     '+1-514-555-0115', '800 Rue Notre-Dame Ouest',
     'Montreal', 'H3C 1J7', 'Canada', 'blocked');


-- ============================================================
-- 2. PRODUCTS
-- ============================================================

INSERT INTO products
    (product_name, description, unit_price, currency, status)
VALUES
    ('Laptop Pro 14',
     'Ordinateur portable professionnel 14 pouces',
     149999, 'CAD', 'active'),

    ('Laptop Air 13',
     'Ordinateur portable léger 13 pouces',
     119999, 'CAD', 'active'),

    ('Wireless Mouse',
     'Souris sans fil ergonomique',
     3999, 'CAD', 'active'),

    ('Mechanical Keyboard',
     'Clavier mécanique rétroéclairé',
     8999, 'CAD', 'active'),

    ('USB-C Hub',
     'Hub USB-C 7 ports',
     5999, 'CAD', 'active'),

    ('27 Inch Monitor',
     'Écran professionnel 27 pouces',
     32999, 'CAD', 'active'),

    ('24 Inch Monitor',
     'Écran Full HD 24 pouces',
     21999, 'CAD', 'active'),

    ('Noise Cancelling Headphones',
     'Casque audio à réduction de bruit',
     24999, 'CAD', 'active'),

    ('Webcam HD',
     'Webcam Full HD pour visioconférence',
     7999, 'CAD', 'active'),

    ('Laptop Stand',
     'Support ergonomique pour ordinateur',
     4999, 'CAD', 'active'),

    ('USB-C Cable',
     'Câble USB-C haute vitesse',
     1999, 'CAD', 'active'),

    ('External SSD 1TB',
     'SSD externe 1 To',
     10999, 'CAD', 'active'),

    ('External SSD 2TB',
     'SSD externe 2 To',
     17999, 'CAD', 'active'),

    ('Wireless Charger',
     'Chargeur sans fil',
     3499, 'CAD', 'active'),

    ('Bluetooth Speaker',
     'Enceinte Bluetooth portable',
     6999, 'CAD', 'active'),

    ('Smartphone X',
     'Smartphone 6.5 pouces',
     89999, 'CAD', 'active'),

    ('Tablet 11',
     'Tablette 11 pouces',
     49999, 'CAD', 'active'),

    ('Power Bank',
     'Batterie externe 20 000 mAh',
     4499, 'CAD', 'active'),

    ('Office Chair',
     'Chaise ergonomique de bureau',
     28999, 'CAD', 'active'),

    ('Desk Lamp',
     'Lampe LED de bureau',
     2999, 'CAD', 'active');


-- ============================================================
-- 3. ORDERS
-- ============================================================

INSERT INTO orders
    (customer_id, order_number, status, total_amount, currency,
     shipping_address, ordered_at)
VALUES
    (1, 'ORD-2026-0001', 'delivered', 153998, 'CAD',
     '1250 Rue Sainte-Catherine Ouest, Montreal, H3G 1P1',
     '2026-07-01 10:15:00'),

    (1, 'ORD-2026-0002', 'shipped', 32999, 'CAD',
     '1250 Rue Sainte-Catherine Ouest, Montreal, H3G 1P1',
     '2026-08-05 14:20:00'),

    -- total_amount corrigé à 9996 pour correspondre à la somme des order_items
    -- (3999 + 3 x 1999 = 9996) ; c'était 9998 dans la version précédente.
    (2, 'ORD-2026-0003', 'delivered', 9996, 'CAD',
     '4500 Rue Saint-Denis, Montreal, H2J 2L1',
     '2026-07-05 09:30:00'),

    (2, 'ORD-2026-0004', 'processing', 119999, 'CAD',
     '4500 Rue Saint-Denis, Montreal, H2J 2L1',
     '2026-08-15 11:45:00'),

    (3, 'ORD-2026-0005', 'cancelled', 5999, 'CAD',
     '850 Grande Allée, Quebec City, G1R 2K5',
     '2026-08-01 16:10:00'),

    (3, 'ORD-2026-0006', 'delivered', 24999, 'CAD',
     '850 Grande Allée, Quebec City, G1R 2K5',
     '2026-07-12 13:00:00'),

    (4, 'ORD-2026-0007', 'shipped', 10999, 'CAD',
     '7200 Boulevard Décarie, Montreal, H4P 2N1',
     '2026-08-10 08:20:00'),

    (5, 'ORD-2026-0008', 'pending', 7999, 'CAD',
     '300 Rue Sherbrooke Est, Montreal, H2X 1E6',
     '2026-08-17 12:00:00'),

    (6, 'ORD-2026-0009', 'delivered', 32999, 'CAD',
     '210 Rue Wellington, Montreal, H3C 1V8',
     '2026-07-20 15:40:00'),

    (7, 'ORD-2026-0010', 'confirmed', 89999, 'CAD',
     '1800 Avenue du Mont-Royal, Montreal, H2H 1J6',
     '2026-08-16 10:05:00'),

    (8, 'ORD-2026-0011', 'delivered', 49999, 'CAD',
     '90 Rue Saint-Jean, Quebec City, G1R 1N5',
     '2026-07-22 11:30:00'),

    (9, 'ORD-2026-0012', 'shipped', 17999, 'CAD',
     '5600 Rue Masson, Montreal, H2H 1A4',
     '2026-08-11 17:25:00'),

    (10, 'ORD-2026-0013', 'cancelled', 28999, 'CAD',
     '125 Rue Ontario Est, Montreal, H2X 1H4',
     '2026-08-03 09:00:00'),

    -- total_amount corrigé à 10497 (4999 + 3499 + 1999 = 10497) ; c'était 10498.
    (11, 'ORD-2026-0014', 'delivered', 10497, 'CAD',
     '700 Rue de la Gauchetière, Montreal, H3B 2M4',
     '2026-07-28 14:45:00'),

    -- total_amount corrigé à 153998 (149999 + 3999 = 153998) ; c'était 154998.
    -- Le double paiement ci-dessous (TXN-2026-000015-A/B), lui, reste volontaire :
    -- c'est le cas de test "double débit" que le support doit détecter.
    (12, 'ORD-2026-0015', 'processing', 153998, 'CAD',
     '950 Avenue du Parc, Montreal, H2X 2H2',
     '2026-08-16 16:20:00'),

    (13, 'ORD-2026-0016', 'delivered', 7498, 'CAD',
     '120 Rue Principale, Longueuil, J4H 1H2',
     '2026-07-30 10:30:00'),

    (14, 'ORD-2026-0017', 'shipped', 24999, 'CAD',
     '4000 Boulevard Saint-Laurent, Montreal, H2W 1Y8',
     '2026-08-12 13:10:00'),

    (15, 'ORD-2026-0018', 'pending', 4499, 'CAD',
     '800 Rue Notre-Dame Ouest, Montreal, H3C 1J7',
     '2026-08-17 09:15:00');


-- ============================================================
-- 4. ORDER ITEMS
-- ============================================================

INSERT INTO order_items
    (order_id, product_id, quantity, unit_price)
VALUES
    (1, 1, 1, 149999),
    (1, 3, 1, 3999),

    (2, 6, 1, 32999),

    (3, 3, 1, 3999),
    (3, 11, 3, 1999),

    (4, 2, 1, 119999),

    (5, 5, 1, 5999),

    (6, 8, 1, 24999),

    (7, 12, 1, 10999),

    (8, 9, 1, 7999),

    (9, 6, 1, 32999),

    (10, 16, 1, 89999),

    (11, 17, 1, 49999),

    (12, 13, 1, 17999),

    (13, 19, 1, 28999),

    (14, 10, 1, 4999),
    (14, 14, 1, 3499),
    (14, 11, 1, 1999),

    (15, 1, 1, 149999),
    (15, 3, 1, 3999),

    (16, 15, 1, 6999),
    (16, 11, 1, 499),

    (17, 8, 1, 24999),

    (18, 18, 1, 4499);


-- ============================================================
-- 5. PAYMENTS
-- ============================================================

INSERT INTO payments
    (order_id, amount, currency, status, payment_method,
     transaction_reference, paid_at)
VALUES

    -- Commande 1 : paiement normal
    (1, 153998, 'CAD', 'paid', 'credit_card',
     'TXN-2026-000001', '2026-07-01 10:16:00'),

    -- Commande 2
    (2, 32999, 'CAD', 'paid', 'credit_card',
     'TXN-2026-000002', '2026-08-05 14:21:00'),

    -- Commande 3
    (3, 9998, 'CAD', 'paid', 'paypal',
     'TXN-2026-000003', '2026-07-05 09:31:00'),

    -- Commande 4
    (4, 119999, 'CAD', 'paid', 'credit_card',
     'TXN-2026-000004', '2026-08-15 11:46:00'),

    -- Commande 5 annulée et remboursée
    (5, 5999, 'CAD', 'refunded', 'credit_card',
     'TXN-2026-000005', '2026-08-01 16:11:00'),

    -- Commande 6
    (6, 24999, 'CAD', 'paid', 'paypal',
     'TXN-2026-000006', '2026-07-12 13:01:00'),

    -- Commande 7
    (7, 10999, 'CAD', 'paid', 'credit_card',
     'TXN-2026-000007', '2026-08-10 08:21:00'),

    -- Commande 8 : paiement en attente
    (8, 7999, 'CAD', 'pending', 'credit_card',
     'TXN-2026-000008', NULL),

    -- Commande 9
    (9, 32999, 'CAD', 'paid', 'debit_card',
     'TXN-2026-000009', '2026-07-20 15:41:00'),

    -- Commande 10
    (10, 89999, 'CAD', 'paid', 'credit_card',
     'TXN-2026-000010', '2026-08-16 10:06:00'),

    -- Commande 11
    (11, 49999, 'CAD', 'paid', 'paypal',
     'TXN-2026-000011', '2026-07-22 11:31:00'),

    -- Commande 12
    (12, 17999, 'CAD', 'paid', 'credit_card',
     'TXN-2026-000012', '2026-08-11 17:26:00'),

    -- Commande 13 annulée
    (13, 28999, 'CAD', 'refunded', 'credit_card',
     'TXN-2026-000013', '2026-08-03 09:01:00'),

    -- Commande 14
    (14, 10498, 'CAD', 'paid', 'debit_card',
     'TXN-2026-000014', '2026-07-28 14:46:00'),

    -- Commande 15 : cas intéressant pour le support (double débit du même montant,
    -- 153998 = total_amount de la commande, aligné avec la correction ci-dessus)
    (15, 153998, 'CAD', 'paid', 'credit_card',
     'TXN-2026-000015-A', '2026-08-16 16:21:00'),

    (15, 153998, 'CAD', 'paid', 'credit_card',
     'TXN-2026-000015-B', '2026-08-16 16:22:00'),

    -- Commande 16
    (16, 7498, 'CAD', 'paid', 'paypal',
     'TXN-2026-000016', '2026-07-30 10:31:00'),

    -- Commande 17
    (17, 24999, 'CAD', 'paid', 'credit_card',
     'TXN-2026-000017', '2026-08-12 13:11:00'),

    -- Commande 18 : paiement en attente
    (18, 4499, 'CAD', 'pending', 'credit_card',
     'TXN-2026-000018', NULL);


-- ============================================================
-- 6. SHIPMENTS
-- ============================================================

INSERT INTO shipments
    (order_id, carrier, tracking_number, status,
     estimated_delivery, shipped_at, delivered_at)
VALUES

    (1, 'Canada Post', 'CP202607010001',
     'delivered', '2026-07-06',
     '2026-07-02 08:00:00',
     '2026-07-05 14:30:00'),

    (2, 'Purolator', 'PU202608050002',
     'in_transit', '2026-08-20',
     '2026-08-06 09:00:00',
     NULL),

    (3, 'Canada Post', 'CP202607050003',
     'delivered', '2026-07-10',
     '2026-07-06 08:00:00',
     '2026-07-09 16:00:00'),

    (6, 'UPS', 'UPS202607120006',
     'delivered', '2026-07-17',
     '2026-07-13 10:00:00',
     '2026-07-16 13:20:00'),

    (7, 'FedEx', 'FDX202608100007',
     'in_transit', '2026-08-18',
     '2026-08-11 08:30:00',
     NULL),

    (9, 'Purolator', 'PU202607200009',
     'delivered', '2026-07-25',
     '2026-07-21 09:00:00',
     '2026-07-24 15:45:00'),

    (11, 'Canada Post', 'CP202607220011',
     'delivered', '2026-07-28',
     '2026-07-23 07:30:00',
     '2026-07-27 11:10:00'),

    (12, 'UPS', 'UPS202608110012',
     'delayed', '2026-08-19',
     '2026-08-12 09:15:00',
     NULL),

    (14, 'Canada Post', 'CP202607280014',
     'delivered', '2026-08-02',
     '2026-07-29 08:00:00',
     '2026-08-01 14:00:00'),

    (16, 'Purolator', 'PU202607300016',
     'delivered', '2026-08-04',
     '2026-07-31 10:00:00',
     '2026-08-03 12:30:00'),

    (17, 'FedEx', 'FDX202608120017',
     'in_transit', '2026-08-19',
     '2026-08-13 08:45:00',
     NULL);


-- ============================================================
-- 7. RETURNS
-- ============================================================

INSERT INTO returns
    (order_id, reason, status, requested_at,
     approved_at, received_at, refunded_at)
VALUES

    -- Retour normal
    (1,
     'Le client souhaite retourner le produit.',
     'refunded',
     '2026-07-10 10:00:00',
     '2026-07-11 09:00:00',
     '2026-07-15 14:00:00',
     '2026-07-17 10:00:00'),

    -- Retour en cours
    (6,
     'Le produit ne correspond pas aux attentes du client.',
     'approved',
     '2026-08-01 11:30:00',
     '2026-08-02 09:15:00',
     NULL,
     NULL),

    -- Retour refusé
    (9,
     'Produit retourné après expiration du délai autorisé.',
     'rejected',
     '2026-08-15 16:00:00',
     NULL,
     NULL,
     NULL),

    -- Retour demandé
    (11,
     'Produit reçu endommagé.',
     'requested',
     '2026-08-10 13:20:00',
     NULL,
     NULL,
     NULL),

    -- Commande annulée
    (13,
     'Annulation de la commande avant expédition.',
     'refunded',
     '2026-08-03 10:00:00',
     '2026-08-03 10:15:00',
     '2026-08-03 10:20:00',
     '2026-08-04 09:30:00');


-- ============================================================
-- 8. SUPPORT CONVERSATIONS
-- ============================================================

INSERT INTO support_conversations
    (customer_id, channel, status, created_at)
VALUES

    (1, 'chat', 'resolved', '2026-08-05 15:00:00'),

    (2, 'chat', 'open', '2026-08-17 09:30:00'),

    (3, 'email', 'resolved', '2026-08-02 14:00:00'),

    (4, 'chat', 'in_progress', '2026-08-17 10:15:00'),

    (5, 'chat', 'escalated', '2026-08-17 12:30:00'),

    (9, 'email', 'escalated', '2026-08-15 16:30:00'),

    (12, 'chat', 'open', '2026-08-17 17:00:00'),

    (15, 'chat', 'escalated', '2026-08-17 09:45:00');


-- ============================================================
-- 9. SUPPORT MESSAGES
-- ============================================================

INSERT INTO support_messages
    (conversation_id, sender_type, message,
     ai_generated, knowledge_article_id, confidence_score)
VALUES

    -- Conversation 1
    (1, 'customer',
     'Bonjour, où est ma commande ORD-2026-0002 ?',
     0, NULL, NULL),

    (1, 'ai',
     'Votre commande ORD-2026-0002 est actuellement en transit. La livraison est estimée au 20 août 2026.',
     1, 'KB-003', 0.96),

    (1, 'customer',
     'Merci.',
     0, NULL, NULL),


    -- Conversation 2
    (2, 'customer',
     'Je voudrais annuler ma commande.',
     0, NULL, NULL),

    (2, 'ai',
     'Je peux vous aider à vérifier si votre commande peut encore être annulée. Pouvez-vous me fournir votre numéro de commande ?',
     1, 'KB-001', 0.91),


    -- Conversation 3
    (3, 'customer',
     'Comment retourner mon produit ?',
     0, NULL, NULL),

    (3, 'ai',
     'Vous pouvez demander un retour depuis votre espace client en sélectionnant la commande concernée.',
     1, 'KB-013', 0.97),

    (3, 'customer',
     'Parfait, merci.',
     0, NULL, NULL),


    -- Conversation 4
    (4, 'customer',
     'J''ai payé mais ma commande n''est pas confirmée.',
     0, NULL, NULL),

    (4, 'ai',
     'Je vais vérifier les informations disponibles concernant votre paiement et votre commande.',
     1, 'KB-011', 0.88),


    -- Conversation 5 : escalade
    (5, 'customer',
     'J''ai été débité deux fois pour ma commande.',
     0, NULL, NULL),

    (5, 'ai',
     'Je constate une situation nécessitant une vérification de votre paiement. Je vais transmettre votre demande à un agent.',
     1, 'KB-012', 0.79),

    (5, 'agent',
     'Bonjour, je vais vérifier les deux transactions avec notre système de paiement.',
     0, NULL, NULL),


    -- Conversation 6 : colis indiqué livré
    (6, 'customer',
     'Le suivi indique que mon colis est livré mais je ne l''ai pas reçu.',
     0, NULL, NULL),

    (6, 'ai',
     'Je n''ai pas suffisamment d''informations pour résoudre cette situation automatiquement. Votre demande est transférée à un agent.',
     1, 'KB-008', 0.72),

    (6, 'agent',
     'Nous allons vérifier les informations de livraison auprès du transporteur.',
     0, NULL, NULL),


    -- Conversation 7
    (7, 'customer',
     'Quand vais-je recevoir mon remboursement ?',
     0, NULL, NULL),

    (7, 'ai',
     'Le délai de remboursement dépend du moyen de paiement utilisé. Je vais vérifier le statut de votre remboursement.',
     1, 'KB-016', 0.94),


    -- Conversation 8 : double paiement
    (8, 'customer',
     'Pourquoi ma carte a-t-elle été débitée deux fois ?',
     0, NULL, NULL),

    (8, 'ai',
     'Votre demande nécessite une vérification détaillée des transactions. Je vous mets en relation avec un agent.',
     1, 'KB-012', 0.81);

COMMIT;