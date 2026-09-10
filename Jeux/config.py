import pygame

# --- INITIALISATION DES POLICES GLOBALES (pour ui.py) ---
pygame.font.init()
font_small = pygame.font.SysFont("Consolas", 14)
font_med = pygame.font.SysFont("Consolas", 18)
font_large = pygame.font.SysFont("Consolas", 24)
font_title = pygame.font.SysFont("Consolas", 32)

# --- PALETTE DE COULEURS CYBERPUNK ---
CYAN = (0, 240, 255)
PINK = (255, 0, 110)
YELLOW = (255, 215, 0)
GREEN = (0, 255, 128)
RED = (255, 40, 40)
GOLD = (255, 200, 0)
TEXT_COLOR = (220, 235, 255)
MUTED_COLOR = (120, 140, 180)
CARD_BG = (14, 18, 30, 200)
CARD_BORDER = (40, 60, 100)
PANEL_BG = (10, 14, 24, 230)
PANEL_BORDER = (0, 240, 255)

# --- CITATIONS CYBERPUNK (affichées sur le dirigeable publicitaire) ---
CYBERPUNK_QUOTES = [
    "WAKE THE FUCK UP, SAMURAI — WE HAVE A CITY TO BURN.",
    "NIGHT CITY RAILWAY : THE CITY OF DREAMS... OR NIGHTMARES.",
    "ARASAKA TOWER : SECURITY, PROSPERITY & SUBROUTINES.",
    "NEVER FADE AWAY — KEEP PUSHING THROUGH THE ICE.",
    "GOLD-PLATED CHROME & BRAINDANCE DREAMS.",
    "CORPO-RATS RUN THIS ENTIRE SPRAWL.",
    "BECOME A LEGEND OF THE AFTERLIFE, NOT A ROOKIE.",
    "TOO MUCH CHROME WILL FRY YOUR SYNAPSE, CHOOMBA.",
    "MAELSTROM ACTIVITY DETECTED IN SECTOR 7.",
    "SANTO DOMINGO AIRSPACE : INDUSTRIAL ZONE SECURE.",
]

# --- RÉSOLUTIONS DISPONIBLES (jusqu'à la 4K) ---
RESOLUTIONS_LIST = [
    (1280, 720),
    (1600, 900),
    (1920, 1080),
    (2560, 1440),
    (3840, 2160),
]

# --- CONFIGURATION DES BOTS (PRODUCTION DE CRÉDITS) ---
BOTS_DATA = [
    {
        "id": "netrunner",
        "name": "Netrunner Novice",
        "desc": "Scanne les subnets de Watson pour extraire des eddies résiduels et des micro-transactions oubliées sans se faire repérer par les daemons locaux.",
        "lore": (
            "Un script kiddy de Kabuki qui rêve de s'acheter\n"
            "un passeport pour l'espace en piratant des\n"
            "distributeurs automatiques de nouilles."
        ),
        "cost": 15,
        "cps": 0.5,
        "color": CYAN,
        "icon": "terminal",
    },
    {
        "id": "ganger",
        "name": "Scavenger de Rue",
        "desc": "Dépouille les implants obsolètes et revends les composants sur le marché noir des bas-fonds à des ripperdocs peu scrupuleux.",
        "lore": (
            "Ils fouillent méthodiquement les ruelles sombres\n"
            "à la recherche de chrome encore chaud à revendre\n"
            "pour une bouchée de pain."
        ),
        "cost": 120,
        "cps": 4.0,
        "color": PINK,
        "icon": "skull",
    },
    {
        "id": "corpo_drone",
        "name": "Drone de Surveillance",
        "desc": "Patrouille le ciel des corporations pour collecter et revendre des données de trafic ultra-sensibles aux fixeurs rivaux.",
        "lore": (
            "Un œil constant dans le smog de Night City,\n"
            "programmé pour ignorer les crimes à moins qu'ils\n"
            "ne nuisent aux actions en bourse."
        ),
        "cost": 1100,
        "cps": 32.0,
        "color": YELLOW,
        "icon": "drone",
    },
    {
        "id": "maxtec",
        "name": "Unité Max-Tac",
        "desc": "Intervient pour neutraliser les cyberpsychos et récupère le matériel militaire de pointe sur les cadavres encore fumants.",
        "lore": (
            "La dernière chose que voient les criminels les plus\n"
            "instables de la ville avant de finir découpés\n"
            "en morceaux par le feu."
        ),
        "cost": 14000,
        "cps": 260.0,
        "color": RED,
        "icon": "shield",
    },
    {
        "id": "fixer",
        "name": "Fixer de Quartier",
        "desc": "Coordonne des contrats clandestins discrets à travers Heywood et génère un flux constant de commissions sur les risques encourus.",
        "lore": (
            "Assis au fond d'un bar enfumé, il tire les ficelles\n"
            "de l'ombre et monnaye chaque information\n"
            "confidentielle au plus offrant."
        ),
        "cost": 75000,
        "cps": 1200.0,
        "color": CYAN,
        "icon": "briefcase",
    },
    {
        "id": "trauma_team",
        "name": "Équipe Trauma Team International",
        "desc": "Facture des abonnements exorbitants et rançonne les zones d'intervention d'urgence prioritaire pour maximiser les profits.",
        "lore": (
            "Leur devise est implacable : votre vie ou vos\n"
            "économies, livrées en moins de trois minutes\n"
            "chrono par héliport blindé."
        ),
        "cost": 350000,
        "cps": 5500.0,
        "color": GREEN,
        "icon": "cross",
    },
    {
        "id": "rogue_ai",
        "name": "Chasseur de Données du Blackwall",
        "desc": "Extrait des fragments de technologies interdites de l'autre côté du mur de feu numérique au péril de votre intégrité mentale.",
        "lore": (
            "Une entité frôlant la folie algorithmique, capable\n"
            "de siphonner des comptes offshores dans des\n"
            "dimensions virtuelles oubliées."
        ),
        "cost": 1800000,
        "cps": 25000.0,
        "color": RED,
        "icon": "ghost",
    },
    {
        "id": "arasaka_agent",
        "name": "Infiltrateur Arasaka",
        "desc": "Détourne les flux de trésorerie internes de la multinationale directement vers vos serveurs fantômes sans éveiller les soupçons.",
        "lore": (
            "Formé dans les divisions d'élite du contre-espionnage,\n"
            "il opère dans l'obscurité absolue sans laisser\n"
            "la moindre trace biologique."
        ),
        "cost": 9500000,
        "cps": 120000.0,
        "color": GOLD,
        "icon": "eye",
    },
    {
        "id": "netwatch_exec",
        "name": "Directeur Netwatch",
        "desc": "Monopolise et taxe le trafic de données inter-réseaux sous couvert de régulation sécuritaire pour écraser toute concurrence.",
        "lore": (
            "Il contrôle les vannes du net mondial, s'octroyant\n"
            "une dime royale sur chaque gigaoctet transitant\n"
            "par les serveurs de la ville."
        ),
        "cost": 50000000,
        "cps": 650000.0,
        "color": CYAN,
        "icon": "lock",
    },
    {
        "id": "soulkiller_rig",
        "name": "Ferme de Serveurs Soulkiller",
        "desc": "Numérise la conscience de magnats de la pègre pour monnayer leurs secrets industriels les plus sombres éternellement.",
        "lore": (
            "Une machinerie macabre conçue à l'origine par Alt\n"
            "Cunningham, transformée ici en redoutable machine\n"
            "à imprimer des eddies."
        ),
        "cost": 250000000,
        "cps": 3200000.0,
        "color": PINK,
        "icon": "server",
    },
    {
        "id": "milan_orbital",
        "name": "Station Orbitale de Luxe",
        "desc": "Exploite le tourisme spatial des ultra-riches et les paris sur les marchés financiers extraterritoriaux pour siphonner les fortunes.",
        "lore": (
            "Flottant majestueusement au-dessus des nuages,\n"
            "elle accueille les pontes de la haute corporation\n"
            "loin de la pollution terrestre."
        ),
        "cost": 1200000000,
        "cps": 15000000.0,
        "color": YELLOW,
        "icon": "rocket",
    },
    {
        "id": "rogue_ai_cluster",
        "name": "Nœud d'IA Souveraine",
        "desc": "Un conglomérat d'intelligences artificielles rebelles qui réécrit l'économie globale en temps réel à votre unique avantage.",
        "lore": (
            "Ces entités dépassent l'entendement humain,\n"
            "façonnant les flux monétaires mondiaux par de\nsimples pulses quantiques invisibles."
        ),
        "cost": 6000000000,
        "cps": 80000000.0,
        "color": RED,
        "icon": "cpu",
    },
    {
        "id": "nanotech_swarm",
        "name": "Essaim de Nanomachines Global",
        "desc": "Recycle la matière physique de Night City en devises numériques en temps réel, consumant chaque atome d'infrastructure.",
        "lore": (
            "Une brume grise microscopique qui dévore\n"
            "lentement les structures obsolètes pour accroître\n"
            "exponentiellement votre capital."
        ),
        "cost": 30000000000,
        "cps": 400000000.0,
        "color": GREEN,
        "icon": "particle",
    },
    {
        "id": "chronos_engine",
        "name": "Moteur Temporel Arasaka",
        "desc": "Anticipe les fluctuations boursières une microseconde avant qu'elles ne se produisent grâce à des calculs quantiques déments.",
        "lore": (
            "Un prototype ultra-secret capable de tordre\n"
            "légèrement la chronologie pour garantir un\n"
            "rendement financier absolument infini."
        ),
        "cost": 150000000000,
        "cps": 2100000000.0,
        "color": GOLD,
        "icon": "clock",
    },
    {
        "id": "god_machine",
        "name": "Singularité de Night City",
        "desc": "Contrôle l'intégralité de la matrice urbaine, centralisant toute la richesse et le pouvoir de la mégalopole en un point unique.",
        "lore": (
            "Vous ne gérez plus l'économie de la ville :\n"
            "vous ÊTES l'économie de la ville, le dieu\n"
            "omniscient régnant sur les néons."
        ),
        "cost": 800000000000,
        "cps": 11000000000.0,
        "color": CYAN,
        "icon": "infinity",
    },
]

# --- AMÉLIORATIONS DE CLIC ---
UPGRADES_DATA = [
    {
        "id": "finger",
        "name": "Câblage Neural Sub-Dermique",
        "desc": "Améliore la vitesse de transmission synaptique pour doubler l'efficacité des impulsions nerveuses (+2 par clic).",
        "cost": 100,
        "icon": "chip",
    },
    {
        "id": "overclock",
        "name": "Overclocking Synaptique",
        "desc": "Pousse le système nerveux au-delà des limites biologiques habituelles pour maximiser les dégâts de données (+5 par clic).",
        "cost": 750,
        "icon": "cpu",
    },
    {
        "id": "nanites",
        "name": "Nanites Médicales d'Urgence",
        "desc": "Répare les tissus musculaires en temps réel pour éviter la fatigue instantanée lors des frappes répétées (+50 par clic).",
        "cost": 5000,
        "icon": "syringe",
    },
    {
        "id": "hyper_thread",
        "name": "Processeur Militech Mk.IV",
        "desc": "Assure un multithreading quantique massif pour traiter chaque pression sur l'interface à la vitesse de la lumière (+500 par clic).",
        "cost": 45000,
        "icon": "server",
    },
    {
        "id": "reflex_booster",
        "name": "Accélérateur de Synapses Kiroshi",
        "desc": "Améliore la perception visuelle et la vitesse de réaction des doigts sur les terminaux de commande (+1,500 par clic).",
        "cost": 250000,
        "icon": "eye",
    },
    {
        "id": "biopod_mk2",
        "name": "Biopode de Survie Avancé",
        "desc": "Remplace une partie des organes vitaux par des pompes synthétiques ultra-rapides pour soutenir l'effort (+7,500 par clic).",
        "cost": 1200000,
        "icon": "heart",
    },
    {
        "id": "quantum_fingers",
        "name": "Doigts Tactiles Quantiques",
        "desc": "Permet d'interagir directement avec les sous-couches de données par simple effleurement de la matrice (+35,000 par clic).",
        "cost": 6000000,
        "icon": "hand",
    },
    {
        "id": "synaptic_accelerator",
        "name": "Accélérateur Synaptique Militaire",
        "desc": "Décuple l'impulsion électrique du système nerveux central pour des performances de frappe surhumaines (+150,000 par clic).",
        "cost": 30000000,
        "icon": "zap",
    },
    {
        "id": "nanite_muscles",
        "name": "Fibres Musculaires Myofibres",
        "desc": "Remplace les fibres musculaires par des faisceaux de nanotubes de carbone ultra-puissants (+700,000 par clic).",
        "cost": 150000000,
        "icon": "muscles",
    },
    {
        "id": "neural_matrix",
        "name": "Matrice Neuronale Concurrente",
        "desc": "Permet de traiter plusieurs milliers de requêtes de clics simultanément par dédoublement de conscience (+3,500,000 par clic).",
        "cost": 750000000,
        "icon": "grid",
    },
    {
        "id": "omega_nerves",
        "name": "Câblage Cérébral Oméga",
        "desc": "Installe un réseau synaptique intégralement synthétique totalement affranchi de toute latence biologique (+18,000,000 par clic).",
        "cost": 3500000000,
        "icon": "omega",
    },
    {
        "id": "ai_enhancement",
        "name": "Symbiose d'IA Cognitive",
        "desc": "Fusionne votre esprit avec une intelligence artificielle pour automatiser chaque impulsion physique (+90,000,000 par clic).",
        "cost": 18000000000,
        "icon": "brain",
    },
    {
        "id": "god_fingers",
        "name": "Interface de Transcendance Divine",
        "desc": "Transforme chaque mouvement physique en un cataclysme de données pures sur le réseau mondial (+450,000,000 par clic).",
        "cost": 90000000000,
        "icon": "sparkle",
    },
    {
        "id": "singularity_reflex",
        "name": "Réflexes de Singularité Temporelle",
        "desc": "Agit avant même que l'intention de cliquer ne se forme consciemment dans le cortex cérébral (+2,200,000,000 par clic).",
        "cost": 450000000000,
        "icon": "star",
    },
    {
        "id": "ultimate_chrome",
        "name": "Ascension Cybernétique Absolue",
        "desc": "L'apogée absolue de l'augmentation humaine, transcendant définitivement les limites de la chair et du silicium (+10,000,000,000 par clic).",
        "cost": 2500000000000,
        "icon": "crown",
    },
]

# --- OBJETS LÉGENDAIRES LIÉS À L'HISTOIRE DE DAVID MARTINEZ ---
ITEMS_DATA = [
    {
        "id": "ticket",
        "name": "Badge d'Accès Arasaka",
        "desc": "Le vieux badge de l'académie de David. Il rappelle ses débuts avant qu'il ne bascule corps et âme dans la pègre.",
        "perf": "+1 Puissance de Clic",
        "icon": "terminal",
    },
    {
        "id": "jacket",
        "name": "Veste de Maine",
        "desc": "La veste iconique de l'ancien caïd de Santo Domingo. Elle dégage une aura indélébile de respect et de danger.",
        "perf": "+25% de production globale (CPS)",
        "icon": "jacket",
    },
    {
        "id": "sandevistan",
        "name": "Implant Sandevistan (Militech Apogee)",
        "desc": "Le prototype militaire qui ralentit le temps. Permet à David d'esquiver la mort, du moins pour un temps...",
        "perf": "+50 de Puissance de Clic",
        "icon": "eye",
    },
    {
        "id": "relic_core",
        "name": "Processeur Neural Personnalisé",
        "desc": "Optimisé pour supporter la terrible surcharge de chrome sans risquer de disjoncter immédiatement.",
        "perf": "+20 Puissance de Clic",
        "icon": "cpu",
    },
    {
        "id": "neuro_blocker",
        "name": "Bloqueurs de Synapses",
        "desc": "L'unique moyen chimique de repousser l'inévitable et tragique descente dans la folie furieuse de la cyberpsychose.",
        "perf": "Multiplie la production totale par x2.5",
        "icon": "pill",
    },
    {
        "id": "lucy_shard",
        "name": "Éclat de Mémoire de Lucy",
        "desc": "Un éclat de données crypté contenant les souvenirs précieux des rêves lunaires partagés avec David.",
        "perf": "+100 Clics & +10% CPS",
        "icon": "moon",
    },
    {
        "id": "kiroshi_optics",
        "name": "Optiques Kiroshi « Massacre »",
        "desc": "Des lentilles oculaires haut de gamme modifiées pour cibler avec une précision chirurgicale les points faibles des corpos.",
        "perf": "+500 Puissance de Clic",
        "icon": "lens",
    },
    {
        "id": "dorio_fist",
        "name": "Poings d'Acier de Dorio",
        "desc": "Des plaques de renforcement osseux et des articulations lourdes ayant appartenu à la redoutable et loyale Dorio.",
        "perf": "+2,500 Puissance de Clic",
        "icon": "fist",
    },
    {
        "id": "pillar_goggles",
        "name": "Lunettes de Briseur de Code de Pilar",
        "desc": "Un équipement de netrunner excentrique truffé de scripts agressifs d'analyse rapide de failles logicielles.",
        "perf": "+10,000 CPS global",
        "icon": "glasses",
    },
    {
        "id": "becca_shotgun",
        "name": "Cartouche de Calibre Lourd de Rebecca",
        "desc": "Une munition spéciale surdimensionnée portant fièrement les graffitis anarchiques de la frondeuse et explosive Rebecca.",
        "perf": "+50,000 Puissance de Clic",
        "icon": "bullet",
    },
    {
        "id": "faraday_data",
        "name": "Disque Dur Crypté de Faraday",
        "desc": "Contient les dossiers compromettants du fixeur véreux révélant ses sombres contrats secrets avec Arasaka.",
        "perf": "+250,000 CPS global",
        "icon": "drive",
    },
    {
        "id": "arasaka_tower_blueprint",
        "name": "Plans Architecturaux d'Arasaka Tower",
        "desc": "Le schéma topographique détaillé des sous-sols secrets et des redoutables tourelles de défense de la tour principale.",
        "perf": "Multiplicateur x3.0 CPS",
        "icon": "blueprint",
    },
    {
        "id": "smasher_armor_plate",
        "name": "Plaque d'Armure d'Adam Smasher",
        "desc": "Un fragment de céramique composite indestructible arraché au cyborg le plus redoutable et terrifiant de toute la ville.",
        "perf": "+1,500,000 Puissance de Clic",
        "icon": "armor",
    },
    {
        "id": "moon_ticket",
        "name": "Billet pour la Lune (Reservations Tanaka)",
        "desc": "Le billet tant convoité pour le complexe lunaire, promesse ultime d'un voyage vers les étoiles loin de la Terre.",
        "perf": "+10,000,000 CPS global",
        "icon": "ticket_moon",
    },
    {
        "id": "legend_jacket",
        "name": "Mémorial Holographique de David",
        "desc": "Une projection permanente immortalisant pour l'éternité la légende de David Martinez au cœur du bar Afterlife.",
        "perf": "Multiplicateur x15.0 Global",
        "icon": "hologram",
    },
]

# --- CHAPITRE D'HISTOIRE (15 étapes étendues avec sauts de ligne pour un affichage propre) ---
STORY_CHAPTERS = [
    (
        0,
        (
            "Journal de bord // David Martinez - Entrée #01\n\n"
            "Night City ne fait pas de cadeaux. Ce matin-là, la pluie acide tapait contre les vitres crasseuses de l'appartement de Santo Domingo. Gloria, ma mère, s'escrimait encore sur ses bilans comptables, persuadée qu'en bossant vingt heures par jour, on finirait par s'en sortir.\n\n"
            "Mais on ne s'en sort pas. Pas ici. Pas qu'une corpo décide de vous écraser pour un pet de travers.\n"
            "J'ai regardé mes mains trembler. J'avais besoin de pognon, vite, pour espérer entrer à l'Académie Arasaka et porter le gilet blindé. C'est ce jour-là que j'ai ramassé cette vieille relique technologique rouillée cachée sous le lit. Un vieux bout de code neuronal qui allait changer ma vie... ou l'abréger."
        ),
        "ticket",
    ),
    (
        2500,
        (
            "Après avoir quitté l'académie, David fait la\n"
            "rencontre de Maine et de son crew redoutable.\n"
            "Il récupère la veste jaune iconique, symbole\n"
            "de son entrée dans le milieu mercenaire."
        ),
        "jacket",
    ),
    (
        15000,
        (
            "David se fait greffer le Sandevistan militaire.\n"
            "Sa vitesse surpasse tout ce que Night City a connu,\n"
            "mais le prix à payer pour son corps commence\n"
            "à se faire lourdement ressentir."
        ),
        "sandevistan",
    ),
    (
        60000,
        (
            "Pour stabiliser ses fonctions cognitives malgré\n"
            "l'excès de chrome, David installe un processeur\n"
            "neural de pointe capable de limiter\n"
            "la surcharge électrique."
        ),
        "relic_core",
    ),
    (
        200000,
        (
            "La cyberpsychose guette à chaque coin de rue.\n"
            "Malgré les avertissements répétés de Lucy,\n"
            "David sombre dans l'obsession de l'implant\n"
            "et de l'Arasaka Tower."
        ),
        "neuro_blocker",
    ),
    (
        750000,
        (
            "Lucy protège David dans le cyberespace profond,\n"
            "cachant ses traces face aux traqueurs d'Arasaka\n"
            "tout en rêvant secrètement de leur voyage\n"
            "futur vers la colonie lunaire."
        ),
        "lucy_shard",
    ),
    (
        2500000,
        (
            "L'installation des optiques Kiroshi 'Massacre'\n"
            "permet à David d'analyser les failles tactiques\n"
            "des forces de sécurité en une fraction\n"
            "de seconde."
        ),
        "kiroshi_optics",
    ),
    (
        8000000,
        (
            "La disparition tragique de Maine et Dorio\n"
            "laisse des cicatrices profondes dans le groupe,\n"
            "poussant David à endosser le rôle de leader\n"
            "malgré sa jeunesse."
        ),
        "dorio_fist",
    ),
    (
        25000000,
        (
            "Pilar et Rebecca apportent leur grain de folie\n"
            "dans les missions musclées à travers les quartiers\n"
            "chauds, transformant chaque contrat en bain\n"
            "de sang fluorescent."
        ),
        "pillar_goggles",
    ),
    (
        80000000,
        (
            "Rebecca refuse d'abandonner David alors que\n"
            "son corps commence à rejeter massivement\n"
            "les implants, armée jusqu'aux dents pour\n"
            "le dernier combat."
        ),
        "becca_shotgun",
    ),
    (
        250000000,
        (
            "Le piège se referme lorsque le fixeur Faraday\n"
            "livre le crew aux intérêts corporatistes\n"
            "d'Arasaka lors d'une embuscade préméditée\n"
            "au sommet de Night City."
        ),
        "faraday_data",
    ),
    (
        800000000,
        (
            "L'assaut désespéré est lancé directement contre\n"
            "l'Arasaka Tower, évitant les patrouilles grâce\n"
            "aux plans topographiques dérobés dans les\n"
            "réseaux sécurisés."
        ),
        "arasaka_tower_blueprint",
    ),
    (
        2500000000,
        (
            "Le monstre d'Arasaka entre en scène : Adam Smasher\n"
            "se dresse face à David dans un duel titanesque\n"
            "où la chair affronte le métal lourd\n"
            "sans aucune pitié."
        ),
        "smasher_armor_plate",
    ),
    (
        8000000000,
        (
            "Grâce au sacrifice ultime de David pour sauver\n"
            "Lucy, cette dernière atteint enfin la surface\n"
            "de la Lune, réalisant leur promesse commune\n"
            "sous la lumière froide des étoiles."
        ),
        "moon_ticket",
    ),
    (
        25000000000,
        (
            "À Night City, les légendes ne meurent jamais :\n"
            "un verre personnalisé à son nom trône désormais\n"
            "fièrement au comptoir de l'Afterlife,\n"
            "immortalisant son histoire."
        ),
        "legend_jacket",
    ),
]


# --- GESTION DES POLICES D'ÉCRITURE DYNAMIQUES ---
def get_fonts(screen_height):
    base_size = max(12, int(screen_height / 45))
    try:
        return {
            "small": pygame.font.SysFont("Consolas", base_size),
            "med": pygame.font.SysFont("Consolas", int(base_size * 1.3)),
            "large": pygame.font.SysFont("Consolas", int(base_size * 1.8)),
            "title": pygame.font.SysFont("Consolas", int(base_size * 2.4)),
        }
    except Exception:
        return {
            "small": pygame.font.Font(None, int(base_size * 1.2)),
            "med": pygame.font.Font(None, int(base_size * 1.6)),
            "large": pygame.font.Font(None, int(base_size * 2.2)),
            "title": pygame.font.Font(None, int(base_size * 3.0)),
        }