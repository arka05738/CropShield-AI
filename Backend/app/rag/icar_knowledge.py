"""
Comprehensive ICAR Package of Practices (POP) Knowledge Base.
Contains verified agricultural guidelines from:
- Indian Council of Agricultural Research (ICAR)
- Central Insecticide Board and Registration Committee (CIBRC)
- State Agricultural Universities (PAU, TNAU, UAS Bengaluru, MPKV Rahuri, BCKV)
"""

ICAR_POP_RECORDS = [
    {
        "id": "icar_pop_tomato_early_blight",
        "crop": "Tomato",
        "disease": "Early Blight",
        "pest": "Aphid",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "Package of Practices for Commercial Solanaceous Crops - Tomato Health Management",
        "page_number": 42,
        "condition_summary": "Alternaria solani infection characterized by concentric brown target spots on leaves, exacerbated by temperature 24-30°C and frequent dew.",
        "pesticide": {
            "active_ingredient": "Mancozeb 75% WP",
            "chemical_name": "Dithane M-45 / Indofil M-45",
            "exact_dose_per_liter": "2.5 g/L",
            "withholding_period_days": 7,
            "application_method": "Foliar spray using hollow cone nozzle, ensuring coverage on both upper and lower leaf surfaces.",
            "safety_warnings": [
                "Wear protective eyewear and gloves during preparation.",
                "Do not spray during peak midday sunlight or when honeybees are actively foraging.",
                "Adhere strictly to 7-day waiting period prior to fruit harvest."
            ]
        },
        "fertilizer": {
            "n_ratio": "Reduced Nitrogen (-30%)",
            "p_ratio": "Standard Phosphorus (50 kg/ha)",
            "k_ratio": "Elevated Potassium (+25% via SOP/MOP)",
            "micronutrients": ["Zinc Sulphate 0.5%", "Borax 0.2% foliar spray"],
            "instructions": "Temporarily suspend excess urea application as succulent vegetative flush increases fungal susceptibility. Apply Potassium Sulphate to thicken leaf cell walls."
        },
        "ipm": {
            "cultural": [
                "Remove and burn lower infected leaves showing target spots (sanitation).",
                "Maintain 60 x 45 cm plant spacing to facilitate canopy aeration and rapid dew drying.",
                "Employ drip irrigation rather than overhead sprinklers to prevent leaf moisture persistence."
            ],
            "biological": [
                "Foliar spray of Trichoderma viride or T. harzianum @ 5 g/L in early morning.",
                "Application of Pseudomonas fluorescens (2% WP) @ 10 g/L for systemic resistance induction.",
                "Neem seed kernel extract (NSKE 5%) or Neem Oil 1500 ppm @ 3 ml/L for aphid deterrence."
            ],
            "mechanical": [
                "Install yellow sticky traps @ 15-20 traps/acre at canopy height to capture winged aphid and whitefly vectors.",
                "Erect bird perches @ 10/acre to encourage natural predators."
            ],
            "chemical": [
                "Foliar spray with Mancozeb 75 WP @ 2.5 g/L or Chlorothalonil 75 WP @ 2.0 g/L.",
                "For severe blight spread, alternate with Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Complete foliar spray with calibrated knapsack sprayer. Rogue out severely blighted bottom leaves.",
            "day_3": "Inspect treated foliage for arrest of spot expansion and absence of active fungal sporulation halo.",
            "day_7": "Re-evaluate canopy; inspect 20 random plants across the field. If new lesions appear, apply alternate systemic mode of action.",
            "day_14": "Assess recovery rate, examine young emergent leaves, and ensure zero leaf curling."
        }
    },
    {
        "id": "icar_pop_rice_blast",
        "crop": "Rice",
        "disease": "Rice Blast",
        "pest": "Yellow Stem Borer",
        "authority": "ICAR-National Rice Research Institute (NRRI), Cuttack",
        "document_title": "Standard Operating Procedure for Rice Blast & Stem Borer Management in India",
        "page_number": 28,
        "condition_summary": "Magnaporthe oryzae (Pyricularia grisea) spindle-shaped foliar blast lesions with greyish centres, accompanied by Scirpophaga incertulas dead hearts.",
        "pesticide": {
            "active_ingredient": "Tricyclazole 75% WP",
            "chemical_name": "Beam / Baan 75 WP",
            "exact_dose_per_liter": "0.6 g/L",
            "withholding_period_days": 30,
            "application_method": "High-volume knapsack sprayer applying 500 liters of water spray volume per hectare.",
            "safety_warnings": [
                "Do not allow spray drift into adjacent fish ponds or aquaculture canals.",
                "Store in original sealed container away from animal feed and drinking water."
            ]
        },
        "fertilizer": {
            "n_ratio": "Split Nitrogen into 3 equal doses; do not top-dress during cloudy/rainy days",
            "p_ratio": "Single Super Phosphate (SSP) 60 kg/ha basal",
            "k_ratio": "Muriate of Potash (MOP) 40 kg/ha in 2 splits",
            "micronutrients": ["Silicon fertilization (Calcium Silicate @ 200 kg/ha)"],
            "instructions": "Avoid excessive basal or top-dressed nitrogenous fertilizers which elevate leaf blast susceptibility."
        },
        "ipm": {
            "cultural": [
                "Adjust transplanting time to avoid coincidence of heading stage with high humidity blast peak.",
                "Drain standing water from paddy field for 24-48 hours to aerate soil and reduce humidity."
            ],
            "biological": [
                "Seed treatment with Pseudomonas fluorescens @ 10 g/kg seed followed by seedling dip.",
                "Release egg parasitoid Trichogramma japonicum @ 100,000/ha at weekly intervals against stem borer."
            ],
            "mechanical": [
                "Set up pheromone traps with (Z)-11-hexadecenal lure @ 8 traps/ha for monitoring stem borer moth emergence.",
                "Clip seedling leaf tips before transplanting to remove stem borer egg masses."
            ],
            "chemical": [
                "For blast: Spray Tricyclazole 75 WP @ 0.6 g/L or Isoprothiolane 40 EC @ 1.5 ml/L.",
                "For stem borer dead hearts: Cartap Hydrochloride 50 SP @ 2.0 g/L or Chlorantraniliprole 18.5 SC @ 0.3 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply Tricyclazole spray immediately upon sighting spindle-shaped leaf blast spots.",
            "day_3": "Count stem borer moth catches in pheromone traps; check water drainage level.",
            "day_7": "Assess flag leaf health and measure percentage of 'dead heart' tillers.",
            "day_14": "Inspect panicle emergence for absence of neck blast infection."
        }
    },
    {
        "id": "icar_pop_cotton_bollworm",
        "crop": "Cotton",
        "disease": "Cotton Leaf Curl Virus",
        "pest": "American Bollworm",
        "authority": "ICAR-Central Institute for Cotton Research (CICR), Nagpur",
        "document_title": "Integrated Pest and Resistance Management Strategy for Cotton in Central & North Zones",
        "page_number": 56,
        "condition_summary": "Helicoverpa armigera larval feeding on squares and bolls combined with whitefly-vectored leaf curl enations.",
        "pesticide": {
            "active_ingredient": "Chlorantraniliprole 18.5% SC",
            "chemical_name": "Coragen 18.5 SC",
            "exact_dose_per_liter": "0.3 ml/L",
            "withholding_period_days": 15,
            "application_method": "Foliar mist directed at upper and mid-canopy fruiting branches.",
            "safety_warnings": [
                "Rotate with insect growth regulators (IGRs) to prevent pesticide resistance.",
                "Do not harvest cotton within 15 days of Coragen treatment."
            ]
        },
        "fertilizer": {
            "n_ratio": "Moderate N (80 kg/ha in 3 split doses)",
            "p_ratio": "DAP 40 kg/ha basal",
            "k_ratio": "MOP 40 kg/ha in 2 splits",
            "micronutrients": ["Magnesium Sulphate 1% + Zinc Sulphate 0.5% foliar spray"],
            "instructions": "Spray 2% DAP or 1% 19:19:19 during flowering stage to mitigate square shedding."
        },
        "ipm": {
            "cultural": [
                "Plant trap crop rows of Marigold (1 row for every 16 cotton rows) to attract bollworm moths.",
                "Maintain weed-free field borders to eliminate alternate whitefly hosts like Abutilon indicum."
            ],
            "biological": [
                "Spray HaNPV (Helicoverpa armigera Nuclear Polyhedrosis Virus) @ 250 LE/ha in evening hours.",
                "Release Chrysoperla zastrowi sillemi @ 10,000 nymphs/ha for sucking pest control."
            ],
            "mechanical": [
                "Install Helilure pheromone traps @ 5 traps/acre for adult moth monitoring.",
                "Hand-pick and destroy grown larvae and damaged flared squares."
            ],
            "chemical": [
                "For bollworm: Chlorantraniliprole 18.5 SC @ 0.3 ml/L or Flubendiamide 39.35 SC @ 0.2 ml/L.",
                "For whitefly vector: Diafenthiuron 50 WP @ 1.2 g/L or Pyriproxyfen 10 EC @ 2 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply targeted larvicide spray. Inspect marigold trap rows for egg laying.",
            "day_3": "Check pheromone trap counts; inspect terminal shoots for whitefly nymphs.",
            "day_7": "Sample 20 green bolls across 5 field quadrants for boring holes or frass.",
            "day_14": "Verify boll retention and measure new vegetative canopy formation."
        }
    },
    {
        "id": "icar_pop_potato_late_blight",
        "crop": "Potato",
        "disease": "Late Blight",
        "pest": "Potato Tuber Moth",
        "authority": "ICAR-Central Potato Research Institute (CPRI), Shimla",
        "document_title": "Decision Support System for Late Blight Management in Indo-Gangetic Plains",
        "page_number": 19,
        "condition_summary": "Phytophthora infestans causing rapid foliar necrosis and tuber decay during cool, overcast weather with RH > 85%.",
        "pesticide": {
            "active_ingredient": "Cymoxanil 8% + Mancozeb 64% WP",
            "chemical_name": "Curzate M-8 / Moximate WP",
            "exact_dose_per_liter": "2.5 g/L",
            "withholding_period_days": 10,
            "application_method": "Foliar mist covering both foliage and ridge soil surface to prevent tuber infection.",
            "safety_warnings": [
                "Never apply sub-lethal doses which trigger fungicide resistance.",
                "Wear rubber gloves and mask during tank mixing."
            ]
        },
        "fertilizer": {
            "n_ratio": "150 kg N/ha (50% basal, 50% at earthing up)",
            "p_ratio": "80 kg P2O5/ha basal",
            "k_ratio": "100 kg K2O/ha (SOP preferred for starch quality)",
            "micronutrients": ["Foliar Zinc Sulphate 0.2% + Ferrous Sulphate 0.2%"],
            "instructions": "Avoid nitrogen top-dressing after tuber initiation. Ensure adequate soil potassium to improve tuber skin firmness."
        },
        "ipm": {
            "cultural": [
                "Proper earthing-up to provide at least 10 cm soil cover over developing tubers.",
                "Dehaulm (cut foliage) 10-12 days before harvest if late blight is active on leaves."
            ],
            "biological": [
                "Prophylactic foliar spray of Trichoderma harzianum @ 5 g/L before onset of overcast humidity.",
                "Use certified disease-free seed tubers from seed potato production zones."
            ],
            "mechanical": [
                "Destroy cull piles and self-sown potato volunteers around field margins."
            ],
            "chemical": [
                "Prophylactic: Mancozeb 75 WP @ 2.5 g/L or Chlorothalonil 75 WP @ 2.0 g/L.",
                "Curative: Cymoxanil + Mancozeb @ 2.5 g/L or Dimethomorph 50 WP @ 1.0 g/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply systemic curative fungicide across infected patches immediately.",
            "day_3": "Check lesion margins for white downy mildew growth; ensure ridge soil is dry.",
            "day_7": "Assess disease suppression. Re-spray with protectant Mancozeb if rain is forecast.",
            "day_14": "Inspect tubers near soil surface for water-soaked rot symptoms."
        }
    },
    {
        "id": "icar_pop_wheat_rust",
        "crop": "Wheat",
        "disease": "Yellow Stripe Rust",
        "pest": "Wheat Aphid",
        "authority": "ICAR-Indian Institute of Wheat & Barley Research (IIWBR), Karnal",
        "document_title": "Guidelines for Surveillance and Management of Wheat Stripe Rust in North-Western Plains Zone",
        "page_number": 15,
        "condition_summary": "Puccinia striiformis f. sp. tritici causing linear yellow-orange uredinial stripes on leaves, accompanied by Rhopalosiphum padi sap-sucking colony vectors.",
        "pesticide": {
            "active_ingredient": "Tebuconazole 25.9% EC",
            "chemical_name": "Folicur 25.9 EC / Orius",
            "exact_dose_per_liter": "1.0 ml/L",
            "withholding_period_days": 35,
            "application_method": "Tractor mounted boom sprayer or knapsack sprayer applying 500 liters spray volume/ha.",
            "safety_warnings": [
                "Do not spray if strong winds (>15 km/h) threaten drift.",
                "Ensure minimum 35 days before grain harvest."
            ]
        },
        "fertilizer": {
            "n_ratio": "Standard recommended 120 kg N/ha (split basal + 2 irrigations)",
            "p_ratio": "60 kg P2O5/ha as DAP basal",
            "k_ratio": "40 kg K2O/ha as MOP basal",
            "micronutrients": ["Zinc Sulphate 21% @ 25 kg/ha basal"],
            "instructions": "Avoid late-stage nitrogenous top dressing which softens flag leaves and accelerates rust germination."
        },
        "ipm": {
            "cultural": [
                "Sow rust-resistant varieties recommended for NWPZ (e.g. DBW 187, DBW 303, HD 3226).",
                "Ensure timely sowing before November 15 to avoid high temperature rust triggers during grain filling."
            ],
            "biological": [
                "Conserve ladybird beetle (Coccinella septempunctata) predators against wheat aphids.",
                "Avoid unnecessary early chemical sprays that decimate syrphid fly larvae."
            ],
            "mechanical": [
                "Install yellow water pan traps at field boundaries for early alate aphid detection."
            ],
            "chemical": [
                "For stripe rust: Spray Propiconazole 25 EC @ 1.0 ml/L or Tebuconazole 25.9 EC @ 1.0 ml/L at first appearance of yellow stripes.",
                "For severe aphid colonies: Dimethoate 30 EC @ 1.5 ml/L or Thiamethoxam 25 WG @ 0.2 g/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply targeted triazole fungicide spray immediately upon spotting first yellow rust focus.",
            "day_3": "Examine rust pustules for browning/arrest of powder formation.",
            "day_7": "Survey neighboring wheat plots within 500m radius to confirm absence of secondary focal spots.",
            "day_14": "Inspect earhead and flag leaf green area retention."
        }
    },
    {
        "id": "icar_pop_maize_fall_armyworm",
        "crop": "Maize",
        "disease": "Northern Corn Leaf Blight",
        "pest": "Fall Armyworm",
        "authority": "ICAR-Indian Institute of Maize Research (IIMR), Ludhiana",
        "document_title": "Standard Management Protocol for Fall Armyworm & Foliar Blights in Indian Maize",
        "page_number": 34,
        "condition_summary": "Spodoptera frugiperda larvae feeding within the central whorl with characteristic window-paning, combined with Exserohilum turcicum necrotic lesions.",
        "pesticide": {
            "active_ingredient": "Emamectin Benzoate 5% SG",
            "chemical_name": "Proclaim 5 SG",
            "exact_dose_per_liter": "0.4 g/L",
            "withholding_period_days": 14,
            "application_method": "Direct spray nozzle directly into the central plant whorl where larvae shelter.",
            "safety_warnings": [
                "Target larvae at early instar stage (instar 1-2) before they bore deeply into whorls.",
                "Rotate with Chlorantraniliprole 18.5 SC to prevent resistance development."
            ]
        },
        "fertilizer": {
            "n_ratio": "120 kg N/ha in 3 splits (basal, knee-high stage, tasseling)",
            "p_ratio": "60 kg P2O5/ha basal",
            "k_ratio": "40 kg K2O/ha basal",
            "micronutrients": ["Zinc Sulphate @ 25 kg/ha basal", "Borax @ 10 kg/ha"],
            "instructions": "Maintain optimal potassium nutrition to thicken leaf parenchyma and limit fungal lesion elongation."
        },
        "ipm": {
            "cultural": [
                "Intercrop maize with pulse crops (Cowpea or Pigeonpea in 2:1 or 4:1 ratio) to reduce FAW infestation.",
                "Maintain weed-free plots, destroying alternate graminaceous weed hosts."
            ],
            "biological": [
                "Apply Metarhizium rileyi or Beauveria bassiana (1x10^8 cfu/g) @ 5 g/L into the whorl.",
                "Erect bird perches @ 15/acre to encourage insectivorous birds."
            ],
            "mechanical": [
                "Apply sand-lime mixture (9:1 ratio) or wood ash into whorls of young plants to physically abrade larvae.",
                "Install FAW pheromone traps @ 5 traps/acre."
            ],
            "chemical": [
                "Chlorantraniliprole 18.5 SC @ 0.4 ml/L or Emamectin Benzoate 5 SG @ 0.4 g/L applied directly into whorls.",
                "For Turcicum leaf blight: Mancozeb 75 WP @ 2.5 g/L or Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Whirl application of larvicide during morning or late afternoon.",
            "day_3": "Check whorl for dead larvae and cessation of fresh frass.",
            "day_7": "Assess newly emerging leaves for windowing or pinholes.",
            "day_14": "Inspect cob initiation stage and ear leaf health."
        }
    },
    {
        "id": "icar_pop_chilli_anthracnose",
        "crop": "Chilli",
        "disease": "Anthracnose Fruit Rot",
        "pest": "Chilli Thrips",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "Package of Practices for High-Value Solanaceous Spices - Chilli Pest & Disease Shield",
        "page_number": 21,
        "condition_summary": "Colletotrichum capsici causing dark circular sunken lesions on ripe pods with concentric acervuli rings, accompanied by Scirtothrips dorsalis upward leaf curling.",
        "pesticide": {
            "active_ingredient": "Azoxystrobin 18.2% + Difenoconazole 11.4% SC",
            "chemical_name": "Amistar Top 325 SC",
            "exact_dose_per_liter": "1.0 ml/L",
            "withholding_period_days": 5,
            "application_method": "Foliar spray ensuring thorough misting of developing green and red pods.",
            "safety_warnings": [
                "Do not spray during high temperatures exceeding 35°C.",
                "Maintain 5-day pre-harvest interval before picking green chillies."
            ]
        },
        "fertilizer": {
            "n_ratio": "150 kg N/ha in 4 splits",
            "p_ratio": "75 kg P2O5/ha basal",
            "k_ratio": "75 kg K2O/ha in 3 splits",
            "micronutrients": ["Foliar spray of Calcium Nitrate 0.5% + Boron 0.1% to prevent blossom end rot and fruit drop"],
            "instructions": "Ensure balanced potassium fertilization to impart toughness to fruit pericarp against anthracnose penetration."
        },
        "ipm": {
            "cultural": [
                "Collect and burn fallen diseased fruits and dry twigtips (sanitation).",
                "Grow 2-3 border rows of Maize or Sorghum as windbreaks and sucking pest barrier."
            ],
            "biological": [
                "Seed treatment with Trichoderma viride @ 10 g/kg seed + Pseudomonas fluorescens @ 10 g/kg seed.",
                "Foliar spray of Lecanicillium lecanii @ 5 g/L for thrips and mite control."
            ],
            "mechanical": [
                "Install blue sticky traps @ 15-20 traps/acre specifically for thrips attraction."
            ],
            "chemical": [
                "For anthracnose: Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L or Tebuconazole 50% + Trifloxystrobin 25% WG @ 0.6 g/L.",
                "For thrips: Spinetoram 11.7 SC @ 0.8 ml/L or Fipronil 5 SC @ 1.5 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply dual fungicide-insecticide spray; prune dead twigs.",
            "day_3": "Inspect blue traps for thrips count; check fruit surface spots.",
            "day_7": "Examine newly forming fruitlets for clean unblemished skin.",
            "day_14": "Assess ripe fruit harvest for percentage of clean premium pods."
        }
    },
    {
        "id": "icar_pop_soybean_rust",
        "crop": "Soybean",
        "disease": "Soybean Rust",
        "pest": "Girdle Beetle",
        "authority": "ICAR-Indian Institute of Soybean Research (IISR), Indore",
        "document_title": "National Package of Practices for Rainfed and Irrigated Soybean in Central India",
        "page_number": 48,
        "condition_summary": "Phakopsora pachyrhizi polygonous foliar rust pustules rapidly defoliating plants during warm humid monsoons, combined with Oberereopsis brevis petiole girdling.",
        "pesticide": {
            "active_ingredient": "Tebuconazole 10% + Sulphur 65% WG",
            "chemical_name": "Harvester / Shaktiman WG",
            "exact_dose_per_liter": "2.5 g/L",
            "withholding_period_days": 21,
            "application_method": "Knapsack or tractor spray delivering 450-500 L water volume per hectare.",
            "safety_warnings": [
                "Spray when wind is calm (<10 km/h) to ensure penetration into dense canopy.",
                "Observe 21 days pre-harvest safety interval."
            ]
        },
        "fertilizer": {
            "n_ratio": "Starter N 20-30 kg/ha basal (nodulation supplies rest)",
            "p_ratio": "60 kg P2O5/ha as SSP basal (supplies Sulphur)",
            "k_ratio": "40 kg K2O/ha basal",
            "micronutrients": ["Zinc Sulphate 25 kg/ha basal", "Ammonium Molybdate seed treatment"],
            "instructions": "Inoculate seeds with Bradyrhizobium japonicum + PSB culture @ 5 g/kg seed to maximize natural nitrogen fixation."
        },
        "ipm": {
            "cultural": [
                "Adopt Broad Bed Furrow (BBF) or Ridge and Furrow system for proper drainage during heavy rains.",
                "Ensure plant population does not exceed 45 plants/sq.m to avoid microclimatic humid congestion."
            ],
            "biological": [
                "Spray Beauveria bassiana @ 5 g/L against defoliator caterpillars and girdle beetle.",
                "Seed treatment with Trichoderma viride @ 5 g/kg seed."
            ],
            "mechanical": [
                "Hand-pick and destroy girdle beetle ringed petioles at early vegetative stage."
            ],
            "chemical": [
                "For rust: Tebuconazole 25.9 EC @ 1.25 ml/L or Hexaconazole 5 EC @ 1 ml/L at first symptom.",
                "For girdle beetle: Chlorantraniliprole 18.5 SC @ 0.3 ml/L or Thiamethoxam 12.6% + Lambda-cyhalothrin 9.5% ZC @ 0.3 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply protective foliar fungicide upon seeing first lower leaf rust flecking.",
            "day_3": "Check bottom canopy for drying of pustules and cessation of spore dust.",
            "day_7": "Survey mid-canopy leaves and count pod set retention.",
            "day_14": "Inspect seed filling in pods for normal weight gain."
        }
    },
    {
        "id": "icar_pop_sugarcane_red_rot",
        "crop": "Sugarcane",
        "disease": "Red Rot",
        "pest": "Early Shoot Borer",
        "authority": "ICAR-Indian Institute of Sugarcane Research (IISR), Lucknow",
        "document_title": "Integrated Disease and Pest Management in Subtropical Sugarcane",
        "page_number": 12,
        "condition_summary": "Colletotrichum falcatum causing internal stalk reddening with characteristic transverse white patches and alcohol odor, combined with Chilo infuscatellus dead hearts.",
        "pesticide": {
            "active_ingredient": "Carbendazim 50% WP",
            "chemical_name": "Bavistin 50 WP",
            "exact_dose_per_liter": "1.0 g/L (Sett Treatment)",
            "withholding_period_days": 60,
            "application_method": "Dipping 3-budded setts for 15 minutes in fungicidal solution before planting.",
            "safety_warnings": [
                "Do not use seed setts from red-rot infected mother cane fields.",
                "Burn all infected stubbles after harvest."
            ]
        },
        "fertilizer": {
            "n_ratio": "150-200 kg N/ha in 3 splits (basal, 45 DAP, 90 DAP)",
            "p_ratio": "60 kg P2O5/ha basal",
            "k_ratio": "60 kg K2O/ha basal",
            "micronutrients": ["Ferrous Sulphate 25 kg/ha + Zinc Sulphate 25 kg/ha in calcareous soils"],
            "instructions": "Avoid excessive nitrogen in late growth stage to minimize succulent tissue susceptibility."
        },
        "ipm": {
            "cultural": [
                "Plant healthy certified setts of red rot resistant varieties (e.g. Co 0238 replacements, CoLk 14201).",
                "Ensure proper field drainage and prevent waterlogging."
            ],
            "biological": [
                "Sett treatment with Trichoderma viride / T. harzianum @ 10 g/L.",
                "Release Trichogramma chilonis @ 50,000/ha for shoot borer suppression."
            ],
            "mechanical": [
                "Rogue out and destroy infected clumps with rhizomes as soon as yellowing spindle appears.",
                "Earthing-up at 90 days after planting to prevent shoot borer entry."
            ],
            "chemical": [
                "Sett treatment: Carbendazim 50 WP @ 1 g/L or Thiophanate Methyl 70 WP @ 1 g/L.",
                "For shoot borer: Chlorantraniliprole 18.5 SC @ 0.4 ml/L applied at planting furrow or Fipronil 0.3 G @ 25 kg/ha."
            ]
        },
        "monitoring": {
            "day_1": "Sett treatment and furrow insecticide application at sowing.",
            "day_3": "Verify germination vigor and sett emergence.",
            "day_7": "Count early shoot borer dead heart percentage.",
            "day_14": "Inspect tillering density and rogue any diseased sprouts."
        }
    },
    {
        "id": "icar_pop_groundnut_tikka",
        "crop": "Groundnut",
        "disease": "Tikka Leaf Spot",
        "pest": "Tobacco Caterpillar",
        "authority": "ICAR-Directorate of Groundnut Research (DGR), Junagadh",
        "document_title": "Package of Practices for Kharif and Rabi-Summer Groundnut in India",
        "page_number": 26,
        "condition_summary": "Cercospora arachidicola (early leaf spot) and Cercosporidium personatum (late leaf spot) causing dark necrotic circular spots with yellow halos leading to defoliation.",
        "pesticide": {
            "active_ingredient": "Mancozeb 75% WP + Carbendazim 12% WP",
            "chemical_name": "Saaf / Companion WP",
            "exact_dose_per_liter": "2.0 g/L",
            "withholding_period_days": 15,
            "application_method": "High-volume foliar spray ensuring thorough canopy wetting.",
            "safety_warnings": [
                "Do not allow spray run-off into livestock grazing zones.",
                "Ensure 15 days pre-harvest safety period."
            ]
        },
        "fertilizer": {
            "n_ratio": "20 kg N/ha basal starter dose",
            "p_ratio": "40 kg P2O5/ha as SSP basal (supplies Sulphur)",
            "k_ratio": "40 kg K2O/ha as MOP basal",
            "micronutrients": ["Gypsum @ 400 kg/ha at pegging stage (40-45 DAP) for calcium pod filling"],
            "instructions": "Gypsum application is crucial during pegging stage to prevent pops (empty pods) and pod rot."
        },
        "ipm": {
            "cultural": [
                "Crop rotation with cereals like Pearl Millet, Sorghum, or Maize to break soil pathogen cycles.",
                "Maintain optimal plant spacing (30 x 10 cm)."
            ],
            "biological": [
                "Seed treatment with Trichoderma viride @ 4 g/kg seed.",
                "SlNPV (Spodoptera litura NPV) @ 250 LE/ha in evening hours."
            ],
            "mechanical": [
                "Install Spodolure pheromone traps @ 5/acre.",
                "Destroy egg masses and gregarious young larvae on leaves."
            ],
            "chemical": [
                "For Tikka: Hexaconazole 5 EC @ 1 ml/L or Tebuconazole 25.9 EC @ 1 ml/L.",
                "For Spodoptera: Novaluron 10 EC @ 1 ml/L or Chlorantraniliprole 18.5 SC @ 0.3 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply systemic fungicide upon noticing lower leaf spots.",
            "day_3": "Check for arrest of necrotic spot expansion.",
            "day_7": "Survey pegging development and check leaf retention.",
            "day_14": "Inspect developing pods for soundness."
        }
    },
    {
        "id": "icar_pop_chickpea_wilt_pod_borer",
        "crop": "Chickpea",
        "disease": "Fusarium Wilt",
        "pest": "Gram Pod Borer",
        "authority": "ICAR-Indian Institute of Pulses Research (IIPR), Kanpur",
        "document_title": "Standard Operating Procedure for Pulse Protection - Chickpea Health Protocol",
        "page_number": 34,
        "condition_summary": "Fusarium oxysporum f. sp. ciceri vascular wilt with internal xylem browning and Helicoverpa armigera pod borer larval infestation.",
        "pesticide": {
            "active_ingredient": "Chlorantraniliprole 18.5% SC",
            "chemical_name": "Coragen 18.5 SC",
            "exact_dose_per_liter": "0.3 ml/L",
            "withholding_period_days": 14,
            "application_method": "Foliar spray during early pod formation stage targeting young larvae before pod entry.",
            "safety_warnings": [
                "Wear protective respirator mask and gloves when measuring concentrated suspension.",
                "Ensure minimum 14-day pre-harvest waiting window before dry pod harvesting."
            ]
        },
        "fertilizer": {
            "n_ratio": "Starter Nitrogen 20 kg/ha basal only",
            "p_ratio": "40 kg P2O5/ha as Single Super Phosphate (supplies 16% S)",
            "k_ratio": "20 kg K2O/ha as Muriate of Potash basal",
            "micronutrients": ["Foliar spray of 2% Urea or DAP at flower initiation and 15 days later"],
            "instructions": "Inoculate seeds with Rhizobium and Phosphate Solubilizing Bacteria (PSB) @ 10 g/kg seed. Restrict excess nitrogen to prevent wilt susceptibility."
        },
        "ipm": {
            "cultural": [
                "Deep summer ploughing to expose pupae to predatory birds and solar heat.",
                "Intercropping with Coriander, Mustard (4:1) or Marigold borders to attract parasites."
            ],
            "biological": [
                "Seed treatment with Trichoderma asperellum @ 5 g/kg seed + Pseudomonas fluorescens @ 5 g/kg.",
                "Spray HaNPV (Helicoverpa armigera Nuclear Polyhedrosis Virus) @ 250 LE/ha during evening hours."
            ],
            "mechanical": [
                "Install T-shaped bamboo bird perches @ 15-20 per acre.",
                "Erect Helilure pheromone traps @ 5 per acre for monitoring ETL."
            ],
            "chemical": [
                "Seed treatment: Carboxin 37.5% + Thiram 37.5% DS @ 2 g/kg seed against wilt.",
                "Foliar spray: Emamectin Benzoate 5 SG @ 0.4 g/L or Chlorantraniliprole 18.5 SC @ 0.3 ml/L at ETL (1 larva/meter row)."
            ]
        },
        "monitoring": {
            "day_1": "Deploy pheromone traps and examine 20 plants for young neonate larvae.",
            "day_3": "Apply bio-rational or chemical spray if moth catch exceeds 4-5 moths/trap/night.",
            "day_7": "Verify cessation of pod boring and larva drop-off.",
            "day_14": "Inspect seed fullness and assess canopy recovery."
        }
    },
    {
        "id": "icar_pop_mustard_alternaria_aphid",
        "crop": "Mustard",
        "disease": "Alternaria Blight",
        "pest": "Mustard Aphid",
        "authority": "ICAR-Directorate of Rapeseed-Mustard Research (DRMR), Bharatpur",
        "document_title": "Integrated Pest & Disease Management in Rapeseed-Mustard - DRMR Technical Bulletin",
        "page_number": 19,
        "condition_summary": "Alternaria brassicae concentric brown zonate spots on leaves/pods and Lipaphis erysimi aphid colonies curling tender shoots.",
        "pesticide": {
            "active_ingredient": "Mancozeb 75% WP + Dimethoate 30% EC",
            "chemical_name": "Dithane M-45 + Rogor 30 EC",
            "exact_dose_per_liter": "2.0 g/L + 1.5 ml/L",
            "withholding_period_days": 21,
            "application_method": "High-volume foliar spray covering both upper foliage and lower inflorescence branches.",
            "safety_warnings": [
                "Do not spray during morning hours (8 AM - 11 AM) to avoid harming foraging honeybees.",
                "Ensure 21-day withholding interval prior to seed harvesting for oil extraction."
            ]
        },
        "fertilizer": {
            "n_ratio": "80 kg N/ha applied in two splits (50% basal, 50% at first irrigation)",
            "p_ratio": "40 kg P2O5/ha as Single Super Phosphate basal",
            "k_ratio": "40 kg K2O/ha as Muriate of Potash basal",
            "micronutrients": ["Elemental Sulphur @ 40 kg/ha or Gypsum @ 250 kg/ha basal"],
            "instructions": "Sulphur fertilization is vital for mustard glucosinolate oil synthesis and enhances epidermal thickness against fungal spore germination."
        },
        "ipm": {
            "cultural": [
                "Timely sowing between 10th-25th October to escape peak aphid infestation in January.",
                "Maintain row spacing of 30 cm x 10 cm to reduce canopy humidity."
            ],
            "biological": [
                "Conserve ladybird beetles (Coccinella septempunctata) and syrphid fly predators.",
                "Foliar spray of entomopathogenic fungus Verticillium lecanii @ 5 g/L."
            ],
            "mechanical": [
                "Install yellow sticky traps @ 15 per acre to capture winged alate aphids.",
                "Pluck and destroy aphid-infested central twigs at early colony initiation."
            ],
            "chemical": [
                "For Blight: Mancozeb 75 WP @ 2.0 g/L or Iprodione 50 WP @ 2.0 g/L.",
                "For Aphids: Thiamethoxam 25 WG @ 0.3 g/L or Dimethoate 30 EC @ 1.5 ml/L when aphid population reaches 25-30 aphids/10 cm twig."
            ]
        },
        "monitoring": {
            "day_1": "Carry out knapsack application during afternoon hours after pollinator flight ceases.",
            "day_3": "Check for aphid colony collapse and absence of honeydew sticky secretions.",
            "day_7": "Assess siliquae for absence of black sunken blight lesions.",
            "day_14": "Inspect pod maturity and monitor oilseed filling."
        }
    },
    {
        "id": "icar_pop_onion_purple_blotch_thrips",
        "crop": "Onion",
        "disease": "Purple Blotch",
        "pest": "Onion Thrips",
        "authority": "ICAR-Directorate of Onion and Garlic Research (DOGR), Rajgurunagar, Pune",
        "document_title": "Good Agricultural Practices for Onion Health Management & Export Standardization",
        "page_number": 41,
        "condition_summary": "Alternaria porri sunken purple-brown lesions with yellow halo and Thrips tabaci silvery scarring on tubular leaves.",
        "pesticide": {
            "active_ingredient": "Difenoconazole 25% EC",
            "chemical_name": "Score 25 EC",
            "exact_dose_per_liter": "1.0 ml/L",
            "withholding_period_days": 10,
            "application_method": "Foliar spray mixed with non-ionic surfactant/sticker (Sandovit or Triton @ 0.5 ml/L) to prevent run-off on waxy leaves.",
            "safety_warnings": [
                "Always incorporate wetting agent/sticker as waxy onion leaves repel aqueous droplets.",
                "Avoid spraying in windy conditions."
            ]
        },
        "fertilizer": {
            "n_ratio": "100 kg N/ha (50% basal, 25% at 30 DAT, 25% at 45 DAT)",
            "p_ratio": "50 kg P2O5/ha as SSP basal",
            "k_ratio": "50 kg K2O/ha as MOP basal",
            "micronutrients": ["Zinc Sulphate 0.5% + Borax 0.2% foliar spray at 30 & 45 DAT"],
            "instructions": "Discontinue nitrogen top-dressing after 60 days of transplanting to ensure firm bulb formation and prevent neck rot."
        },
        "ipm": {
            "cultural": [
                "Plant 2 border rows of Maize or Sorghum as barrier crops around onion plots to impede thrips migration.",
                "Sprinkler irrigation suppresses thrips population by 40-50% compared to furrow irrigation."
            ],
            "biological": [
                "Foliar spray of Beauveria bassiana @ 5 g/L + Neem Oil 1500 ppm @ 3 ml/L.",
                "Seedling root dip in Pseudomonas fluorescens (0.5% suspension) for 30 minutes before transplanting."
            ],
            "mechanical": [
                "Install blue and yellow sticky traps @ 20 per acre at crop height.",
                "Deep summer ploughing to destroy pupating thrips in soil."
            ],
            "chemical": [
                "For Blotch: Tebuconazole 25.9 EC @ 1.5 ml/L or Azoxystrobin 23 SC @ 1.0 ml/L.",
                "For Thrips: Fipronil 5 SC @ 1.5 ml/L or Spinetoram 11.7 SC @ 0.8 ml/L at ETL (30 thrips/plant)."
            ]
        },
        "monitoring": {
            "day_1": "Spray with sticker-adjuvant ensuring droplet adhesion along vertical cylindrical leaves.",
            "day_3": "Examine leaf sheaths and inner axial crevices for nymph mortality.",
            "day_7": "Survey purple blotch lesions; verify lesion margin desiccation.",
            "day_14": "Inspect emerging tubular leaves for vigorous upright growth."
        }
    },
    {
        "id": "icar_pop_banana_panama_wilt_weevil",
        "crop": "Banana",
        "disease": "Panama Wilt (Fusarium TR4)",
        "pest": "Banana Pseudostem Weevil",
        "authority": "ICAR-National Research Centre for Banana (NRCB), Tiruchirappalli",
        "document_title": "National Biosecurity Protocol for Tropical Race 4 Containment & Weevil Management in Banana",
        "page_number": 15,
        "condition_summary": "Fusarium oxysporum f. sp. cubense Tropical Race 4 vascular wilt with pseudostem splitting and Odoiporus longicollis pseudostem bore holes.",
        "pesticide": {
            "active_ingredient": "Carbendazim 50% WP + Chlorpyrifos 20% EC",
            "chemical_name": "Bavistin 50 WP + Dursban 20 EC",
            "exact_dose_per_liter": "2.0 g/L (corm drench) + 2.5 ml/L (stem swab)",
            "withholding_period_days": 30,
            "application_method": "Soil drenching around root rhizosphere and pseudostem swabbing/injection up to 1 meter height.",
            "safety_warnings": [
                "Disinfect all farm tools with 2% sodium hypochlorite or formaldehyde between plants.",
                "Do not transport suckers from affected areas without quarantine certification."
            ]
        },
        "fertilizer": {
            "n_ratio": "200 g N/plant applied in 4 equal splits during vegetative and shooting stages",
            "p_ratio": "60 g P2O5/plant basal at planting",
            "k_ratio": "300 g K2O/plant in 4 splits (crucial for bunch weight and vascular resilience)",
            "micronutrients": ["NRCB Banana Shakti micronutrient mixture @ 10 g/L foliar spray at 4th, 5th, and 7th month"],
            "instructions": "Avoid excessive ammoniacal nitrogen which acidifies the root zone and stimulates Fusarium microconidia germination."
        },
        "ipm": {
            "cultural": [
                "Strict biosecurity: use certified tissue-culture plantlets hardened in sterile substrate.",
                "Clean field sanitation: uproot and destroy TR4-infected mats using bleaching powder @ 250 g/pit."
            ],
            "biological": [
                "Rhizosphere application of Trichoderma viride (NRCB strain) @ 50 g/plant enriched in 5 kg FYM.",
                "Beauveria bassiana @ 10 ml/L applied to pseudostem cuts to control weevil larvae."
            ],
            "mechanical": [
                "Split pseudostem traps @ 25 traps/ha baited with longitudinal cut banana pseudostem to trap adult weevils.",
                "Maintain weed-free collar region around pseudostem base."
            ],
            "chemical": [
                "Corm injection: Carbendazim 2% solution (2 ml/plant) at 5th and 7th month.",
                "Stem swabbing: Chlorpyrifos 20 EC @ 2.5 ml/L or Swab with Carbaryl 50 WP @ 4 g/L mixed with copper."
            ]
        },
        "monitoring": {
            "day_1": "Drench rhizosphere with 2 liters of fungicide solution per mat; erect split stem traps.",
            "day_3": "Inspect split pseudostem traps and collect adult weevils.",
            "day_7": "Check for arrest of lower leaf skirt yellowing and collar necrosis.",
            "day_14": "Inspect crown shooting and emergent heartleaf health."
        }
    },
    {
        "id": "icar_pop_mango_powdery_mildew_hopper",
        "crop": "Mango",
        "disease": "Powdery Mildew",
        "pest": "Mango Hopper",
        "authority": "ICAR-Central Institute for Subtropical Horticulture (CISH), Lucknow",
        "document_title": "Standard Operating Procedure for Mango Canopy Protection and Export Quality Production",
        "page_number": 38,
        "condition_summary": "Oidium mangiferae white powdery fungal coating on panicles and Amritodus atkinsoni hoppers sucking sap causing blossom drying.",
        "pesticide": {
            "active_ingredient": "Hexaconazole 5% EC + Thiamethoxam 25% WG",
            "chemical_name": "Contaf 5 EC + Actara 25 WG",
            "exact_dose_per_liter": "1.0 ml/L + 0.3 g/L",
            "withholding_period_days": 21,
            "application_method": "High-pressure power sprayer directed at tree crown and flower panicles before full blossom.",
            "safety_warnings": [
                "Never spray during peak flowering/pollination window to avoid killing honeybees.",
                "Adhere to 21-day pre-harvest interval to comply with export maximum residue limits (MRL)."
            ]
        },
        "fertilizer": {
            "n_ratio": "1000 g N/tree (for 10+ year old bearing trees) applied post-harvest",
            "p_ratio": "500 g P2O5/tree applied in post-harvest circular trench",
            "k_ratio": "1000 g K2O/tree applied post-harvest along tree dripline",
            "micronutrients": ["Foliar spray of Zinc Sulphate 0.5% + Boric Acid 0.2% at marble stage fruit development"],
            "instructions": "Apply fertilizers post-harvest in October; avoid winter nitrogen applications that induce untimely vegetative flushes."
        },
        "ipm": {
            "cultural": [
                "Post-harvest canopy pruning to open dense centers and allow sunlight penetration.",
                "Clean orchard floor and destroy fallen malformed inflorescences."
            ],
            "biological": [
                "Release of Chrysoperla carnea green lacewing predators @ 50-100 per tree.",
                "Foliar spray of Lecanicillium lecanii @ 5 g/L against overwintering hopper nymphs."
            ],
            "mechanical": [
                "Install solar light traps @ 1 trap per 2 acres to monitor hopper flight density.",
                "Sticky banding on tree trunk to prevent ant mutualists."
            ],
            "chemical": [
                "Spray 1 (Panicle emergence): Wettable Sulphur 80 WDG @ 2.5 g/L + Imidacloprid 17.8 SL @ 0.3 ml/L.",
                "Spray 2 (Post fruit-set): Hexaconazole 5 EC @ 1 ml/L + Thiamethoxam 25 WG @ 0.3 g/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply fine mist canopy spray using power tractor-mounted sprayer.",
            "day_3": "Examine panicles; confirm elimination of hopper nymphs and honeydew drops.",
            "day_7": "Assess fruit setting (pea-to-marble stage) and ensure panicle cleanliness.",
            "day_14": "Inspect fruit development and screen for anthracnose spot emergence."
        }
    },
    {
        "id": "icar_pop_apple_scab_mite",
        "crop": "Apple",
        "disease": "Apple Scab",
        "pest": "European Red Mite",
        "authority": "SKUAST Kashmir / Dr YSP University of Horticulture & Forestry, Nauni",
        "document_title": "Comprehensive Spray Schedule for Apple Orchards in Western Himalayas",
        "page_number": 52,
        "condition_summary": "Venturia inaequalis olive-green scabby lesions on leaves/fruits and Panonychus ulmi red mite bronzing of foliage.",
        "pesticide": {
            "active_ingredient": "Difenoconazole 25% EC + Propergite 57% EC",
            "chemical_name": "Score 25 EC + Omite 57 EC",
            "exact_dose_per_liter": "0.3 ml/L + 1.0 ml/L",
            "withholding_period_days": 28,
            "application_method": "High-volume air-blast sprayer delivering uniform misty droplet distribution across entire orchard canopy.",
            "safety_warnings": [
                "Do not mix fungicides with alkaline products like lime sulphur or Bordeaux mixture.",
                "Wear complete chemical safety coveralls when operating air-blast orchard sprayers."
            ]
        },
        "fertilizer": {
            "n_ratio": "70 g N per year of tree age (up to max 700 g N/tree)",
            "p_ratio": "35 g P2O5 per year of tree age basal in winter",
            "k_ratio": "70 g K2O per year of tree age (up to max 700 g K2O/tree)",
            "micronutrients": ["Foliar spray of Calcium Chloride 0.5% at 30 days before harvest to prevent bitter pit"],
            "instructions": "Urea foliar spray (5% solution) applied on tree canopy immediately before autumn leaf fall accelerates fallen leaf decomposition."
        },
        "ipm": {
            "cultural": [
                "Autumn sanitation: collect and destroy or compost fallen leaves to eliminate overwintering pseudothecia.",
                "Annual pruning to improve air circulation and rapid leaf surface drying after morning dew."
            ],
            "biological": [
                "Conserve and encourage predatory phytoseiid mites (Typhlodromus pyri).",
                "Avoid broad-spectrum synthetic pyrethroids which induce severe secondary spider mite resurgence."
            ],
            "mechanical": [
                "Corrugated cardboard bands wrapped around tree trunks in August to trap overwintering adult mites.",
                "Erect pheromone traps for codling moth monitoring."
            ],
            "chemical": [
                "Green tip to pink bud: Captan 50 WP @ 2.5 g/L or Dodine 65 WP @ 0.75 g/L.",
                "Petal fall: Difenoconazole 25 EC @ 0.3 ml/L or Tebuconazole 50% + Trifloxystrobin 25% WG @ 0.4 g/L.",
                "Summer mite peak: Propergite 57 EC @ 1 ml/L or Fenazaquin 10 EC @ 1.5 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Complete calibrated air-blast spray covering tree spurs and leaf undersides.",
            "day_3": "Check leaves under 10x hand lens for dead adult red mites.",
            "day_7": "Survey apple fruitlets for smooth skin without corky olive scab lesions.",
            "day_14": "Inspect spur vigor and evaluate leaf greenness."
        }
    },
    {
        "id": "icar_pop_grapes_downy_mildew_mealybug",
        "crop": "Grapes",
        "disease": "Downy Mildew",
        "pest": "Grapevine Mealybug",
        "authority": "ICAR-National Research Centre for Grapes (NRCG), Pune",
        "document_title": "Grape Protection Protocol & Residue Monitoring Plan (GrapeNet Compliance)",
        "page_number": 47,
        "condition_summary": "Plasmopara viticola translucent yellowish oil spots with white downy growth and Maconellicoccus hirsutus cottony mealybugs on bunches.",
        "pesticide": {
            "active_ingredient": "Dimethomorph 50% WP + Spirotetramat 15.31% OD",
            "chemical_name": "Acrobat 50 WP + Movento 150 OD",
            "exact_dose_per_liter": "1.0 g/L + 0.7 ml/L",
            "withholding_period_days": 60,
            "application_method": "Electrostatic or directed knapsack sprayer targeted into the bunch zone and lower leaf surfaces.",
            "safety_warnings": [
                "Strict compliance with APEDA GrapeNet residue monitoring schedule is mandatory.",
                "Observe 60-day pre-harvest withholding period for export-bound table grapes."
            ]
        },
        "fertilizer": {
            "n_ratio": "Controlled Nitrogen; split into fertigation pulses during cane growth only",
            "p_ratio": "Phosphoric acid via fertigation (50 kg P2O5/ha)",
            "k_ratio": "High Potassium (150 kg K2O/ha as Potassium Nitrate / SOP)",
            "micronutrients": ["Potassium phosphonate (0.4%) foliar spray to induce Systemic Acquired Resistance (SAR)"],
            "instructions": "Excessive nitrogen produces dense vegetative shading that exacerbates downy mildew spore germination."
        },
        "ipm": {
            "cultural": [
                "Canopy management: shoot positioning and leaf thinning around bunches to maximize airflow.",
                "Scraping loose bark from main trunk and cordons to remove mealybug overwintering shelters."
            ],
            "biological": [
                "Release of predatory Australian ladybird beetle (Cryptolaemus montrouzieri) @ 1200-1500 beetles/ha.",
                "Application of bio-fungicide Ampelomyces quisqualis or Trichoderma viride @ 5 g/L."
            ],
            "mechanical": [
                "Apply sticky grease bands around the base of vine trunks to prevent mutualist ants from protecting mealybugs.",
                "Manual removal and burning of severely infested grape bunches."
            ],
            "chemical": [
                "Preventative: Bordeaux mixture 1% or Copper Hydroxide 53.8 DF @ 2.0 g/L.",
                "Curative Downy Mildew: Dimethomorph 50 WP @ 1 g/L or Cyazofamid 34.5 SC @ 0.5 ml/L.",
                "Mealybug: Buprofezin 25 SC @ 1.25 ml/L or Spirotetramat 15.31 OD @ 0.7 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply targeted spray ensuring penetration into bunch cluster microclimate.",
            "day_3": "Examine under surfaces of leaves for desiccation of white downy fungal sporangia.",
            "day_7": "Inspect grape bunch stems for absence of honeydew exudation and ant trails.",
            "day_14": "Evaluate berry sizing, bunch uniformity, and cuticle development."
        }
    },
    {
        "id": "icar_pop_pomegranate_bacterial_blight_borer",
        "crop": "Pomegranate",
        "disease": "Bacterial Blight / Oily Spot",
        "pest": "Fruit Borer / Anar Butterfly",
        "authority": "ICAR-National Research Centre on Pomegranate (NRCP), Solapur",
        "document_title": "Package of Practices for Bacterial Blight Management & Anar Butterfly Control",
        "page_number": 33,
        "condition_summary": "Xanthomonas axonopodis pv. punicae dark brown oily angular spots with cracking on rind and Deudorix isocrates borer holes with frass.",
        "pesticide": {
            "active_ingredient": "Streptomycin Sulphate 90% + Tetracycline Hydrochloride 10% (Streptocycline) + Copper Oxychloride 50% WP",
            "chemical_name": "Streptocycline + Blitox 50 WP",
            "exact_dose_per_liter": "0.5 g/L + 2.5 g/L",
            "withholding_period_days": 20,
            "application_method": "High-pressure foliar spray covering branches, stems, and fruits, repeated at 10-day intervals during monsoon showers.",
            "safety_warnings": [
                "Disinfect pruning secateurs with 2.5% sodium hypochlorite solution between every cut.",
                "Never leave pruned infected twigs inside the orchard boundary."
            ]
        },
        "fertilizer": {
            "n_ratio": "250 g N/tree applied during Hasta/Ambe bahar flowering",
            "p_ratio": "125 g P2O5/tree basal",
            "k_ratio": "250 g K2O/tree in 2 splits to reinforce fruit peel tensile strength",
            "micronutrients": ["Foliar spray of Boron 0.1% + Zinc 0.25% + Calcium Nitrate 0.5% to prevent fruit splitting"],
            "instructions": "Enrich farmyard manure with Pseudomonas fluorescens and Trichoderma (10 kg enriched FYM/tree) to build rhizosphere immunity."
        },
        "ipm": {
            "cultural": [
                "Prune blight cankers 5 cm below infected margins, sanitize cuts immediately with 10% Bordeaux paste.",
                "Adopt Hasta bahar flowering (Sept-Oct) to escape high-humidity monsoon bacterial blight proliferation."
            ],
            "biological": [
                "Foliar spray of antagonistic bacteria Bacillus subtilis or B. amyloliquefaciens @ 5 ml/L.",
                "Release egg parasitoid Trichogramma chilonis @ 100,000 per hectare for fruit borer suppression."
            ],
            "mechanical": [
                "Bag individual marble-sized fruits with non-woven polypropylene or butter paper bags (100% effective against butterfly).",
                "Collect and deep-bury all bore-damaged and fallen fruits."
            ],
            "chemical": [
                "For Blight: Streptocycline @ 0.5 g/L + COC 50 WP @ 2.5 g/L or 2-Bromo-2-nitropropane-1,3-diol (Bronopol) @ 0.5 g/L.",
                "For Fruit Borer: Spinetoram 11.7 SC @ 1.0 ml/L or Chlorantraniliprole 18.5 SC @ 0.4 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Prune out visible stem cankers, swab wounds with Bordeaux paste, and apply bactericidal foliar spray.",
            "day_3": "Check fruit rind spots for drying and absence of active bacterial ooze.",
            "day_7": "Survey fruit bags and inspect 25 trees for fresh borer entry frass.",
            "day_14": "Inspect fruit development and verify clean rind expansion."
        }
    },
    {
        "id": "icar_pop_tea_blister_blight_mosquito_bug",
        "crop": "Tea",
        "disease": "Blister Blight",
        "pest": "Tea Mosquito Bug",
        "authority": "UPASI Tea Research Foundation, Valparai / TRA Tocklai, Jorhat",
        "document_title": "Planters Guide to Plant Protection in Commercial Tea - Integrated Disease & Pest Strategy",
        "page_number": 22,
        "condition_summary": "Exobasidium vexans translucent circular blister lesions on tender leaves and Helopeltis theivora necrotic rusty punctures on flush.",
        "pesticide": {
            "active_ingredient": "Hexaconazole 5% EC + Copper Oxychloride 50% WP",
            "chemical_name": "Contaf 5 EC + Blitox 50 WP (Combination)",
            "exact_dose_per_liter": "0.4 ml/L + 1.0 g/L",
            "withholding_period_days": 14,
            "application_method": "Motorized mist-blower knapsack applying fine spray on the plucking table canopy immediately following plucking round.",
            "safety_warnings": [
                "Strict compliance with Tea Board of India Plant Protection Code (PPC) is mandatory.",
                "Observe 14-day pre-harvest withholding period before plucking two leaves and a bud."
            ]
        },
        "fertilizer": {
            "n_ratio": "120-140 kg N/ha applied in 4 splits coinciding with rainfall flushes",
            "p_ratio": "Rock Phosphate applied once in 2 years (40 kg P2O5/ha)",
            "k_ratio": "N:K2O ratio maintained at 1:1 or 1:1.5 (High K enhances cuticle thickness)",
            "micronutrients": ["Zinc Sulphate 1% foliar spray combined with Boric acid 0.1% during pre-monsoon"],
            "instructions": "Adequate potash nutrition is essential to impart mechanical resistance against basidiospore penetration in young flush."
        },
        "ipm": {
            "cultural": [
                "Regulate overhead shade tree canopy before monsoon onset to eliminate damp humid pockets.",
                "Maintain strict short-round plucking (5-7 days) to remove tender susceptible shoots and bug eggs."
            ],
            "biological": [
                "Foliar spray of Beauveria bassiana @ 3 g/L or Metarhizium anisopliae.",
                "Conserve naturally occurring predatory spiders (Oxyopes spp.) and reduviid assassin bugs."
            ],
            "mechanical": [
                "Manual hand collection of adult tea mosquito bugs during early morning hours.",
                "Prune heavily infested boundary patches to reset flush cycle."
            ],
            "chemical": [
                "For Blister Blight: Hexaconazole 5 EC @ 0.4 ml/L + COC @ 1 g/L at 7-10 day intervals.",
                "For Helopeltis: Bifenthrin 8% SC @ 1.0 ml/L or Thiamethoxam 25 WG @ 0.25 g/L strictly within PPC guidelines."
            ]
        },
        "monitoring": {
            "day_1": "Apply fine canopy mist immediately after plucking round to protect freshly severed stem cuts.",
            "day_3": "Check young tender flush for absence of fresh water-soaked feeding punctures.",
            "day_7": "Survey blister spots on under-leaf surface; verify absence of white velvety sporulation.",
            "day_14": "Inspect new flush emergence for tender clean shoots ready for next harvest round."
        }
    },
    {
        "id": "icar_pop_coffee_leaf_rust_borer",
        "crop": "Coffee",
        "disease": "Coffee Leaf Rust",
        "pest": "Coffee White Stem Borer",
        "authority": "Central Coffee Research Institute (CCRI), Coffee Board of India, Balehonnur",
        "document_title": "Package of Practices for Arabica & Robusta Coffee Cultivation - CCRI Technical Guide",
        "page_number": 45,
        "condition_summary": "Hemileia vastatrix orange-yellow powdery pustules on lower leaves causing defoliation and Xylotrechus quadripes stem tunneling with ridged ring swellings.",
        "pesticide": {
            "active_ingredient": "Triadimefon 25% WP + Chlorpyrifos 20% EC",
            "chemical_name": "Bayleton 25 WP + Dursban 20 EC",
            "exact_dose_per_liter": "0.5 g/L (foliar) + 3.0 ml/L (stem swab with 10% lime)",
            "withholding_period_days": 30,
            "application_method": "Foliar spray directed onto leaf undersides for rust, and trunk bark swabbing with lime suspension for white stem borer.",
            "safety_warnings": [
                "Stem swabbing must only target the main wooden trunk and thick primary scaffold branches.",
                "Wear rubber gloves and protective eye shields during lime-insecticide slurry preparation."
            ]
        },
        "fertilizer": {
            "n_ratio": "Post-monsoon balanced application of N:P2O5:K2O (40:30:40 kg/ha)",
            "p_ratio": "40 kg P2O5/ha as Rock Phosphate / DAP basal",
            "k_ratio": "50 kg K2O/ha as MOP post-monsoon (essential for berry sizing and wood hardiness)",
            "micronutrients": ["Zinc Sulphate 0.25% + Urea 0.5% foliar spray during pre-blossom and post-monsoon"],
            "instructions": "Soil test-based lime application (Agricultural lime @ 500 kg/ha) every 2-3 years to correct soil acidity (pH 6.0-6.5)."
        },
        "ipm": {
            "cultural": [
                "Two-tier overhead shade regulation to maintain 40-50% filtered sunlight across the estate.",
                "Tracing, collar uprooting, and immediate burning of borer-infested coffee bushes prior to flight periods (April-May and October-November)."
            ],
            "biological": [
                "Foliar spray of Verticillium lecanii (hyperparasitic fungus on rust pustules) @ 5 g/L.",
                "Release of parasitoid Cephalonomia stephanoderis and conservation of predatory woodpeckers."
            ],
            "mechanical": [
                "Bark scrubbing of main stem and thick primaries using coir gloves/scrubbers to crush borer eggs and pupae in crevices.",
                "Install CCRI white stem borer cross-vane pheromone traps @ 25 traps per hectare."
            ],
            "chemical": [
                "Pre-monsoon and post-monsoon: Bordeaux mixture 0.5% or Epoxiconazole 12.5 SC @ 0.7 ml/L or Triadimefon 25 WP @ 0.5 g/L.",
                "Trunk swabbing: Chlorpyrifos 20 EC @ 3 ml/L + 10% Agricultural Lime slurry applied twice annually."
            ]
        },
        "monitoring": {
            "day_1": "Complete bark scrubbing and swabbing of main stems; apply pre-monsoon Bordeaux or Triadimefon spray.",
            "day_3": "Check stem bark for uniform lime coating without uncovered crevices.",
            "day_7": "Survey lower leaf surfaces for desiccation and necrosis of orange rust pustules.",
            "day_14": "Inspect developing green coffee berries and examine canopy density."
        }
    }
]
